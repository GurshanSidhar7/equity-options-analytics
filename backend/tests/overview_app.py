"""Test-only server for deterministic browser tests. Never used by app.main."""

from app.api.routes import get_history_provider
from app.main import app
from tests.test_overview import TestProvider

app.dependency_overrides[get_history_provider] = TestProvider


from datetime import datetime, timedelta, timezone

from app.api.routes import get_news_service
from app.news.models import NewsCandidate, TickerAssociation
from app.news.service import NewsService


class BrowserNewsProvider:
    name = "Synthetic browser news — tests only"

    def fetch(self, ticker):
        return [NewsCandidate(
            title=f"{ticker} synthetic test coverage {index + 1}", source="Yahoo Finance",
            published_at=datetime(2026, 10, 1, 15, tzinfo=timezone.utc) - timedelta(hours=index),
            url=f"https://example.com/{ticker}/test/{index}",
            summary="Synthetic provider summary for browser testing only." if index != 1 else None,
            topics=["Earnings"] if index == 0 else [],
            company_names=[ticker],
            associations=[TickerAssociation(ticker=ticker, relevance=0.8)],
        ) for index in range(6)]


browser_news = NewsService(BrowserNewsProvider())
app.dependency_overrides[get_news_service] = lambda: browser_news
