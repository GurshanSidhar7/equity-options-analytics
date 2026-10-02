"""Normalize, filter, sort, deduplicate, and cache provider-independent news."""
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
import re
from threading import Lock
from time import monotonic
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from app.news.models import NewsArticle, NewsCandidate, NewsResponse
from app.news.provider import NewsError, NewsProvider

CACHE_TTL_SECONDS = 600
ERROR_TTL_SECONDS = 60
MAX_ARTICLE_AGE_DAYS = 7
# An editorial selection policy, not a guarantee that every published claim is true.
SELECTED_PUBLICATIONS = frozenset({
    "yahoo finance", "reuters", "associated press", "ap", "afp", "bloomberg",
    "cnbc", "financial times", "the wall street journal", "wsj", "barrons.com",
    "barron's", "marketwatch", "mt newswires", "investor's business daily",
    "bbc", "bbc news", "fortune", "quartz",
})


def headline_match(row: NewsCandidate, ticker: str) -> str | None:
    for name in row.company_names:
        if len(name.strip()) >= 3 and re.search(r"(?<!\w)" + re.escape(name.strip()) + r"(?!\w)", row.title, re.IGNORECASE):
            return f"{name} named in headline"
    # Decorated symbols avoid treating everyday words such as CAT, ON, or IT
    # as company references. Unknown issuer aliases are not guessed.
    symbol = re.escape(ticker)
    if re.search(r"(?:\$" + symbol + r"(?!\w)|\(" + symbol + r"\)|(?:NASDAQ|NYSE|TSX):\s*" + symbol + r"(?!\w))", row.title):
        return f"{ticker} stock symbol in headline"
    return None
TOPIC_CONTEXT = {
    "earnings": "Earnings updates can change investor expectations around revenue, profitability, and future growth.",
    "mergers & acquisitions": "Acquisition activity can affect financing needs and expectations for future cash flows.",
}


def url_identity(url: str) -> str:
    parts = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(parts.query) if not k.casefold().startswith("utm_") and k.casefold() not in {"fbclid", "gclid"}]
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), urlencode(sorted(query)), ""))


def select_articles(candidates: list[NewsCandidate], ticker: str, now: datetime) -> list[NewsArticle]:
    relevant = []
    for row in candidates:
        association = next((entry for entry in row.associations if entry.ticker.upper() == ticker), None)
        if association is None or row.source.strip().casefold() not in SELECTED_PUBLICATIONS:
            continue
        if not row.title.strip() or not row.source.strip() or row.published_at.tzinfo is None or row.published_at.utcoffset() is None:
            continue
        published = row.published_at.astimezone(timezone.utc)
        match_reason = headline_match(row, ticker)
        if published > now or published < now - timedelta(days=MAX_ARTICLE_AGE_DAYS) or match_reason is None:
            continue
        relevant.append((published, row, association, match_reason))
    relevant.sort(key=lambda entry: entry[0], reverse=True)
    articles, urls, titles, identifiers = [], set(), set(), set()
    for published, row, association, match_reason in relevant:
        url_key = url_identity(str(row.url))
        title_key = re.sub(r"[\W_]+", " ", row.title.casefold()).strip()
        if not title_key or url_key in urls or title_key in titles or (row.provider_id and row.provider_id in identifiers):
            continue
        urls.add(url_key)
        titles.add(title_key)
        if row.provider_id:
            identifiers.add(row.provider_id)
        topics = list(dict.fromkeys(topic.strip() for topic in row.topics if topic.strip()))[:3]
        context = next((TOPIC_CONTEXT[topic.casefold()] for topic in topics if topic.casefold() in TOPIC_CONTEXT), None)
        articles.append(NewsArticle(title=row.title.strip(), source=row.source.strip(), published_at=published, url=row.url,
            summary=row.summary.strip()[:600] if row.summary and row.summary.strip() else None,
            topics=topics, provider_sentiment=association.sentiment, why_it_may_matter=context, match_reason=match_reason))
        if len(articles) == 4:
            break
    return articles


class NewsService:
    """Bounded process-local TTL cache; successful retrieval time is preserved."""
    def __init__(self, provider: NewsProvider, clock=monotonic, now=lambda: datetime.now(timezone.utc)):
        self.provider, self.clock, self.now = provider, clock, now
        self._cache: OrderedDict[str, tuple[float, NewsResponse]] = OrderedDict()
        self._lock = Lock()

    def get(self, ticker: str) -> NewsResponse:
        ticker = ticker.upper()
        with self._lock:
            cached = self._cache.get(ticker)
            if cached and cached[0] > self.clock():
                self._cache.move_to_end(ticker)
                return cached[1].model_copy(deep=True)
        # Never hold the shared cache lock during external I/O: one slow ticker
        # must not queue requests for every other ticker behind its timeout.
        ttl = CACHE_TTL_SECONDS
        try:
            candidates = self.provider.fetch(ticker)
            now = self.now()
            articles = select_articles(candidates, ticker, now)
            result = NewsResponse(ticker=ticker, retrieved_at=now, status="ok" if articles else "empty", message=None if articles else "No recent company-focused articles from the selected publications were returned.", articles=articles, provider=self.provider.name)
        except NewsError as error:
            ttl = ERROR_TTL_SECONDS
            result = NewsResponse(ticker=ticker, retrieved_at=self.now(), status=error.status, message=str(error), provider=self.provider.name, cache_ttl_seconds=ttl)
        with self._lock:
            self._cache[ticker] = (self.clock() + ttl, result)
            self._cache.move_to_end(ticker)
            while len(self._cache) > 128:
                self._cache.popitem(last=False)
        return result.model_copy(deep=True)
