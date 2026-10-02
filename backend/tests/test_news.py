from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Event

import httpx
import pytest
from fastapi.testclient import TestClient

from app.api.routes import get_news_service
from app.main import app
from app.news.models import NewsCandidate, ProviderSentiment, TickerAssociation
from app.news.provider import NewsError, YahooFinanceNewsProvider, company_names, parse_feed
from app.news.service import NewsService, select_articles

NOW = datetime(2026, 10, 2, 16, tzinfo=timezone.utc)


def candidate(index=0, **changes):
    return NewsCandidate(**(dict(title=f"Apple synthetic test article {index}", source="Reuters", published_at=NOW - timedelta(hours=index + 1), url=f"https://example.com/article/{index}", associations=[TickerAssociation(ticker="AAPL")], company_names=["Apple"]) | changes))


class MockNewsProvider:
    name = "Synthetic test news — tests only"

    def __init__(self, rows=None, error=None):
        self.rows = rows if rows is not None else [candidate(i) for i in range(6)]
        self.error = error
        self.tickers = []

    def fetch(self, ticker):
        self.tickers.append(ticker)
        if self.error:
            raise self.error
        return self.rows


def service(provider=None, **kwargs):
    return NewsService(provider or MockNewsProvider(), now=lambda: NOW, **kwargs)


def raw_article(**changes):
    return dict(title="Apple synthetic test headline", publisher="Reuters", providerPublishTime=int(datetime(2026, 10, 2, 14, tzinfo=timezone.utc).timestamp()), link="https://example.com/story", relatedTickers=["AAPL"], uuid="test-id") | changes


def payload(rows=None, **changes):
    return dict(quotes=[{"symbol": "AAPL", "quoteType": "EQUITY", "shortname": "Apple Inc.", "longname": "Apple Incorporated"}], news=rows if rows is not None else [raw_article()]) | changes


def test_selected_ticker_sorting_limit_and_optional_fields():
    provider = MockNewsProvider(list(reversed([candidate(i) for i in range(6)])))
    result = service(provider).get("aapl")
    assert provider.tickers == ["AAPL"]
    assert result.ticker == "AAPL" and result.retrieved_at == NOW
    assert result.status == "ok"
    assert [row.title for row in result.articles] == [f"Apple synthetic test article {i}" for i in range(4)]
    assert result.articles[0].summary is None and result.articles[0].provider_sentiment is None
    assert result.articles[0].match_reason == "Apple named in headline"
    assert "seven days" in result.selection_note


@pytest.mark.parametrize("count", [0, 1, 3])
def test_fewer_than_four_and_empty(count):
    result = service(MockNewsProvider([candidate(i) for i in range(count)])).get("AAPL")
    assert len(result.articles) == count
    assert result.status == ("empty" if count == 0 else "ok")


def test_dedup_urls_headlines_identifiers_after_sorting():
    rows = [candidate(4), candidate(0, url="https://example.com/article/4?utm_source=test#fragment"), candidate(2, title="  APPLE SYNTHETIC TEST Article 0!!  "), candidate(5, provider_id="same"), candidate(1, provider_id="same")]
    assert [row.title for row in select_articles(rows, "AAPL", NOW)] == ["Apple synthetic test article 0", "Apple synthetic test article 1"]


def test_ticker_matching_future_missing_metadata_and_blank_headline():
    rows = [candidate(0, associations=[TickerAssociation(ticker="MSFT")]), candidate(1, associations=[]), candidate(2), candidate(3, published_at=NOW + timedelta(hours=1)), candidate(4, published_at=NOW.replace(tzinfo=None)), candidate(5, title=" ")]
    assert [row.title for row in select_articles(rows, "AAPL", NOW)] == ["Apple synthetic test article 2"]


@pytest.mark.parametrize("headline", [
    "Fortinet (FTNT) Is Getting More Attention, What Is Behind It?",
    "Cisco Systems Inc Stock (CSCO) Moved Up by 3.21%",
    "Hewlett Packard Enterprise Co Stock (HPE) Moved Up by 7.82%",
    "Honeywell and Ecolab get real about AI's limits",
])
def test_screenshot_peer_headlines_are_excluded_even_with_nvda_tag(headline):
    row = candidate(title=headline, source="Yahoo Finance", summary="NVIDIA is mentioned incidentally in this synthetic test summary.", associations=[TickerAssociation(ticker="NVDA", relevance=1)], company_names=["NVIDIA"])
    assert select_articles([row], "NVDA", NOW) == []


@pytest.mark.parametrize("title,expected", [
    ("Nvidia announces a new chip", True), ("NVIDIAsomething announces a chip", False),
    ("Chip supplier ($NVDA) announces results", True), ("Chip supplier (NVDA) reports", True),
    ("NASDAQ: NVDA announces results", True), ("NVDA-inspired chip startups", False),
])
def test_company_headline_or_explicit_stock_symbol(title, expected):
    row = candidate(title=title, company_names=["NVIDIA"], associations=[TickerAssociation(ticker="NVDA")])
    assert bool(select_articles([row], "NVDA", NOW)) == expected


def test_ordinary_words_are_not_treated_as_stock_symbols():
    row = candidate(title="The cat is out of the bag", company_names=["Caterpillar"], associations=[TickerAssociation(ticker="CAT")])
    assert select_articles([row], "CAT", NOW) == []


def test_publisher_selection_is_case_insensitive_and_conservative():
    rows = [candidate(0, source=" reuters "), candidate(1, source="Unverified Predictions Blog"), candidate(2, source="Motley Fool"), candidate(3, source="MT Newswires")]
    assert [row.source for row in select_articles(rows, "AAPL", NOW)] == ["reuters", "MT Newswires"]


def test_seven_day_age_cutoff_and_boundary():
    rows = [candidate(0, published_at=NOW - timedelta(days=7)), candidate(1, published_at=NOW - timedelta(days=7, seconds=1))]
    assert len(select_articles(rows, "AAPL", NOW)) == 1


def test_timezones_topics_summary_and_optional_sentiment():
    rows = [candidate(0, published_at=NOW.astimezone(timezone(timedelta(hours=5))), topics=["Earnings", "Technology", "Earnings", "Finance", "IPO"], summary="x" * 900, associations=[TickerAssociation(ticker="AAPL", sentiment=ProviderSentiment(label="Neutral", score=0.1))]), candidate(1)]
    result = select_articles(rows, "AAPL", NOW)
    assert result[0].published_at == NOW and result[0].published_at.tzinfo == timezone.utc
    assert result[0].topics == ["Earnings", "Technology", "Finance"]
    assert len(result[0].summary) == 600 and "investor expectations" in result[0].why_it_may_matter
    assert result[0].provider_sentiment.label == "Neutral"


def test_parse_provider_timestamps_and_malformed_articles():
    rows = parse_feed(payload([None, {}, raw_article(), raw_article(providerPublishTime="bad"), raw_article(link="javascript:alert(1)"), raw_article(title=[]), raw_article(providerPublishTime=True)]), "AAPL")
    assert len(rows) == 1
    assert rows[0].published_at.isoformat() == "2026-10-02T14:00:00+00:00"
    assert rows[0].summary is None and rows[0].associations[0].sentiment is None
    assert rows[0].company_names == ["Apple"] and rows[0].provider_id == "test-id"


def test_exact_symbol_resolution_rejects_fuzzy_or_unsupported_quotes():
    for quotes in [[], [{"symbol": "AAP", "quoteType": "EQUITY", "shortname": "Other Company"}], [{"symbol": "AAPL", "quoteType": "CRYPTOCURRENCY"}]]:
        assert parse_feed(payload(quotes=quotes), "AAPL") == []
    assert parse_feed(payload([raw_article(relatedTickers=["MSFT"])]), "AAPL") == []


def test_issuer_names_use_provider_names_without_guessing_aliases():
    assert company_names({"shortname": "NVIDIA Corporation", "longname": "NVIDIA Corp."}) == ["NVIDIA"]
    assert company_names({"shortname": "Alphabet Inc."}) == ["Alphabet"]
    assert company_names({"shortname": None}) == []


@pytest.mark.parametrize("data", [{}, [], {"quotes": [], "news": "invalid"}, {"quotes": "invalid", "news": []}])
def test_malformed_provider_response_is_unavailable(data):
    with pytest.raises(NewsError) as error:
        parse_feed(data, "AAPL")
    assert error.value.status == "unavailable"


@pytest.mark.parametrize("status,expected", [(429, "rate_limited"), (500, "unavailable"), (403, "unavailable")])
def test_http_error(monkeypatch, status, expected):
    original = httpx.Client
    monkeypatch.setattr(httpx, "Client", lambda **kwargs: original(transport=httpx.MockTransport(lambda req: httpx.Response(status)), **kwargs))
    with pytest.raises(NewsError) as error:
        YahooFinanceNewsProvider().fetch("AAPL")
    assert error.value.status == expected


@pytest.mark.parametrize("failure", [httpx.ReadTimeout, httpx.ConnectError])
def test_timeout_connection_failures(monkeypatch, failure):
    original = httpx.Client
    def fail(request):
        raise failure("private provider internals", request=request)
    monkeypatch.setattr(httpx, "Client", lambda **kwargs: original(transport=httpx.MockTransport(fail), **kwargs))
    result = service(YahooFinanceNewsProvider()).get("AAPL")
    assert result.status == "unavailable" and not result.articles
    assert "private provider internals" not in result.model_dump_json()


def test_provider_request_keyless_parameters_and_malformed_json(monkeypatch):
    original = httpx.Client
    def respond(request):
        assert request.url.path == "/v1/finance/search"
        assert request.url.params["q"] == "MSFT"
        assert request.url.params["quotesCount"] == "1"
        assert request.url.params["newsCount"] == "50"
        assert request.url.params["enableFuzzyQuery"] == "false"
        assert "apikey" not in request.url.params
        assert request.extensions["timeout"]["read"] == 8
        return httpx.Response(200, text="not JSON")
    monkeypatch.setattr(httpx, "Client", lambda **kwargs: original(transport=httpx.MockTransport(respond), **kwargs))
    assert service(YahooFinanceNewsProvider()).get("MSFT").status == "unavailable"


@pytest.mark.parametrize("status", ["rate_limited", "unavailable", "not_configured"])
def test_service_failure_states_and_error_cache(status):
    clock = [0]
    provider = MockNewsProvider(error=NewsError(status, "News unavailable"))
    cached = service(provider, clock=lambda: clock[0])
    assert cached.get("AAPL").status == status
    assert cached.get("AAPL").cache_ttl_seconds == 60
    assert provider.tickers == ["AAPL"]
    clock[0] = 61
    cached.get("AAPL")
    assert provider.tickers == ["AAPL", "AAPL"]


def test_success_cache_expiry_ticker_isolation_and_no_mutation():
    clock = [0]
    provider = MockNewsProvider()
    cached = service(provider, clock=lambda: clock[0])
    first = cached.get("AAPL")
    first.articles.clear()
    assert len(cached.get("AAPL").articles) == 4
    cached.get("MSFT")
    assert provider.tickers == ["AAPL", "MSFT"]
    clock[0] = 600
    cached.get("AAPL")
    assert provider.tickers == ["AAPL", "MSFT", "AAPL"]


def test_news_api_normalized_contract_and_invalid_ticker():
    app.dependency_overrides[get_news_service] = lambda: service()
    try:
        with TestClient(app) as client:
            response = client.get("/api/news?ticker=aapl")
            body = response.json()
            assert response.status_code == 200
            assert body["ticker"] == "AAPL" and body["retrieved_at"].endswith("Z")
            assert len(body["articles"]) == 4
            assert {"title", "source", "published_at", "url", "match_reason"} <= body["articles"][0].keys()
            assert "relatedTickers" not in body["articles"][0] and "quotes" not in body
            assert client.get("/api/news?ticker=bad/ticker").status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_successful_http_adapter_response(monkeypatch):
    original = httpx.Client
    monkeypatch.setattr(httpx, "Client", lambda **kwargs: original(transport=httpx.MockTransport(lambda req: httpx.Response(200, json=payload())), **kwargs))
    result = service(YahooFinanceNewsProvider()).get("AAPL")
    assert result.status == "ok" and len(result.articles) == 1
    assert result.articles[0].source == "Reuters"
    assert result.articles[0].published_at.isoformat() == "2026-10-02T14:00:00+00:00"


@pytest.mark.parametrize("status", ["not_configured", "rate_limited", "unavailable"])
def test_news_api_operational_states_return_clean_contract(status):
    app.dependency_overrides[get_news_service] = lambda: service(MockNewsProvider(error=NewsError(status, "News unavailable")))
    try:
        with TestClient(app) as client:
            response = client.get("/api/news?ticker=AAPL")
            assert response.status_code == 200 and response.json()["status"] == status
            assert response.json()["articles"] == []
            assert client.get("/health").json() == {"status": "ok"}
    finally:
        app.dependency_overrides.clear()


def test_slow_ticker_does_not_hold_the_shared_cache_lock():
    started, release = Event(), Event()
    class SlowProvider(MockNewsProvider):
        def fetch(self, ticker):
            if ticker == "AAPL":
                started.set()
                assert release.wait(3)
            return []
    cached = service(SlowProvider())
    with ThreadPoolExecutor(max_workers=2) as pool:
        slow = pool.submit(cached.get, "AAPL")
        assert started.wait(3)
        try:
            assert pool.submit(cached.get, "MSFT").result(timeout=1).status == "empty"
        finally:
            release.set()
        assert slow.result(timeout=3).status == "empty"


def test_cache_storage_is_bounded():
    cached = service(MockNewsProvider([]))
    for index in range(129):
        cached.get(f"T{index}")
    assert len(cached._cache) == 128 and "T0" not in cached._cache
