from datetime import date, datetime, timedelta, timezone
import math

from fastapi.testclient import TestClient
import pytest

from app.api.routes import get_history_provider
from app.main import app
from app.market_data.history import DailyPrice, MarketDataError, PriceHistory


class TestProvider:
    def history(self, ticker):
        # Synthetic inputs are test-only; production never falls back to these.
        if ticker == "BAD":
            raise MarketDataError("Provider unavailable", 503)
        count = 21 if ticker == "SHORT" else 40
        rows = [DailyPrice(date(2026, 1, 1) + timedelta(days=i), 100 + i, 100 * math.exp(0.01 * (i % 3))) for i in range(count)]
        if ticker == "MSFT":
            rows = [DailyPrice(row.date, row.close * 2, row.adjusted_close * 2) for row in rows]
        if ticker == "GAP":
            rows[-1] = DailyPrice(rows[-1].date, None, None)
        return PriceHistory(ticker, "USD", datetime(2026, 9, 16, tzinfo=timezone.utc), rows, [], source="Synthetic test fixture — tests only")


@pytest.fixture
def client():
    app.dependency_overrides[get_history_provider] = TestProvider
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_overview_contract_and_python_daily_change(client):
    response = client.get("/api/overview?ticker=test")
    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "TEST"
    assert body["spot"] == 139
    assert body["daily_change"] == 1
    assert body["daily_change_pct"] == pytest.approx(1 / 138)
    assert body["hv20"] is not None and body["hv30"] is not None
    assert body["hv20"] == body["history"][-1]["hv20"]
    assert body["timestamp"].startswith("2026-09-16")
    assert body["history"][0]["log_return"] is None
    assert "decimals" in body["units"]


def test_short_history_has_hv20_but_no_hv30(client):
    body = client.get("/api/overview?ticker=SHORT").json()
    assert body["hv20"] is not None and body["hv30"] is None
    assert any("HV30 unavailable" in warning for warning in body["warnings"])


def test_latest_gap_does_not_reuse_older_metrics(client):
    body = client.get("/api/overview?ticker=GAP").json()
    assert all(body[key] is None for key in ["spot", "daily_change", "daily_change_pct", "hv20", "hv30"])


def test_provider_failure_has_no_metrics(client):
    response = client.get("/api/overview?ticker=BAD")
    assert response.status_code == 503
    assert response.json() == {"detail": "Provider unavailable"}


@pytest.mark.parametrize("ticker", ["", "a/b", "A" * 21, "<script>"])
def test_bad_ticker(client, ticker):
    assert client.get("/api/overview", params={"ticker": ticker}).status_code == 422
