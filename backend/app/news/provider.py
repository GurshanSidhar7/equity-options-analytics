"""Yahoo Finance ticker-news I/O; never fetch or scrape article bodies.

The search endpoint is unofficial, as is the existing Yahoo history adapter.
Ticker association alone is insufficient; the service also checks headline focus.
"""
from datetime import datetime, timezone
import re
from typing import Protocol

import httpx

from app.news.models import NewsCandidate, NewsStatus, TickerAssociation


class NewsError(Exception):
    def __init__(self, status: NewsStatus, message: str):
        super().__init__(message)
        self.status = status


class NewsProvider(Protocol):
    name: str

    def fetch(self, ticker: str) -> list[NewsCandidate]: ...


def company_names(quote: dict) -> list[str]:
    """Use names supplied for an exact symbol; trim legal/share-class suffixes."""
    names = []
    for field in ("shortname", "longname"):
        name = quote.get(field)
        if not isinstance(name, str) or not name.strip():
            continue
        name = re.split(r"\b(?:incorporated|inc|corporation|corp|plc|ltd|limited|class)\b", name, maxsplit=1, flags=re.IGNORECASE)[0].strip(" ,.-")
        if len(name) >= 3 and name not in names:
            names.append(name)
    return names


def parse_feed(payload: object, ticker: str) -> list[NewsCandidate]:
    if not isinstance(payload, dict) or not isinstance(payload.get("news"), list) or not isinstance(payload.get("quotes"), list):
        raise NewsError("unavailable", "The news provider returned unsupported ticker data.")
    quote = next((row for row in payload["quotes"] if isinstance(row, dict) and row.get("symbol") == ticker and row.get("quoteType") in {"EQUITY", "ETF"}), None)
    if quote is None:
        # Never attach a fuzzy symbol match to the user's requested ticker.
        return []
    names = company_names(quote)
    candidates = []
    for row in payload["news"]:
        if not isinstance(row, dict):
            continue
        try:
            associated = row.get("relatedTickers")
            if not isinstance(associated, list) or ticker not in associated:
                continue
            epoch = row["providerPublishTime"]
            if isinstance(epoch, bool) or not isinstance(epoch, (int, float)):
                continue
            candidates.append(NewsCandidate(
                title=row["title"], source=row["publisher"], url=row["link"],
                published_at=datetime.fromtimestamp(epoch, timezone.utc),
                associations=[TickerAssociation(ticker=ticker)],
                company_names=names,
                provider_id=row.get("uuid") if isinstance(row.get("uuid"), str) else None,
                summary=row.get("summary") if isinstance(row.get("summary"), str) else None,
            ))
        except (KeyError, TypeError, ValueError, OverflowError, OSError):
            continue
    return candidates


class YahooFinanceNewsProvider:
    name = "Yahoo Finance ticker news (unofficial)"

    def fetch(self, ticker: str) -> list[NewsCandidate]:
        try:
            with httpx.Client(timeout=8.0, headers={"User-Agent": "Mozilla/5.0"}) as client:
                response = client.get("https://query1.finance.yahoo.com/v1/finance/search", params={
                    "q": ticker, "quotesCount": 1, "newsCount": 50, "enableFuzzyQuery": "false",
                })
            if response.status_code == 429:
                raise NewsError("rate_limited", "The news provider's request limit was reached. Please try again later.")
            response.raise_for_status()
            return parse_feed(response.json(), ticker)
        except NewsError:
            raise
        except (httpx.HTTPError, ValueError):
            raise NewsError("unavailable", "Recent ticker news is temporarily unavailable.") from None
