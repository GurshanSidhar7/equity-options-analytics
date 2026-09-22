from datetime import datetime, timezone

import httpx
import pytest

from app.market_data.history import MarketDataError, YahooHistoryProvider, normalize_history

NOW = datetime(2026, 9, 16, 16, tzinfo=timezone.utc)


def payload():
    dates = [datetime(2026, 9, day, 13, 30, tzinfo=timezone.utc).timestamp() for day in [14, 15, 16]]
    return {"chart": {"error": None, "result": [{
        "meta": {"currency": "USD", "exchangeTimezoneName": "America/New_York", "instrumentType": "EQUITY"},
        "timestamp": dates,
        "indicators": {"quote": [{"close": [100, 101, 999]}], "adjclose": [{"adjclose": [98, 99, 999]}]},
    }]}}


def test_completed_days_and_distinct_price_bases():
    result = normalize_history(payload(), "TEST", NOW)
    assert len(result.prices) == 2
    assert result.prices[-1].date.isoformat() == "2026-09-15"
    assert result.prices[-1].close == 101
    assert result.prices[-1].adjusted_close == 99
    assert result.currency == "USD" and result.retrieved_at == NOW


def test_absent_adjusted_prices_are_not_substituted():
    data = payload()
    del data["chart"]["result"][0]["indicators"]["adjclose"]
    result = normalize_history(data, "TEST", NOW)
    assert result.prices[0].close == 100
    assert all(row.adjusted_close is None for row in result.prices)


@pytest.mark.parametrize("value", [None, 0, -1, float("inf"), float("nan"), True, "100"])
def test_bad_price_is_a_gap_not_a_dropped_row(value):
    data = payload()
    data["chart"]["result"][0]["indicators"]["quote"][0]["close"][0] = value
    result = normalize_history(data, "TEST", NOW)
    assert len(result.prices) == 2 and result.prices[0].close is None


def test_duplicate_dates_rejected():
    data = payload()
    data["chart"]["result"][0]["timestamp"][1] = data["chart"]["result"][0]["timestamp"][0]
    with pytest.raises(MarketDataError):
        normalize_history(data, "TEST", NOW)


@pytest.mark.parametrize("data", [{}, {"chart": "invalid"}, {"chart": {"result": [], "error": None}}, {"chart": {"result": None, "error": {"code": "Not Found"}}}])
def test_missing_or_malformed_data(data):
    with pytest.raises(MarketDataError):
        normalize_history(data, "TEST", NOW)


def test_missing_currency_is_explicit():
    data = payload()
    del data["chart"]["result"][0]["meta"]["currency"]
    assert normalize_history(data, "TEST", NOW).currency is None


@pytest.mark.parametrize("status,expected", [(404, 404), (429, 503), (500, 503)])
def test_http_failures(monkeypatch, status, expected):
    original = httpx.Client
    transport = httpx.MockTransport(lambda request: httpx.Response(status))
    monkeypatch.setattr(httpx, "Client", lambda **kwargs: original(transport=transport, **kwargs))
    with pytest.raises(MarketDataError) as error:
        YahooHistoryProvider().history("TEST")
    assert error.value.status_code == expected


def test_provider_request_and_normalization(monkeypatch):
    original = httpx.Client

    def respond(request):
        assert request.url.path == "/v8/finance/chart/TEST"
        assert request.url.params["interval"] == "1d"
        assert request.url.params["range"] == "1y"
        assert request.url.params["includeAdjustedClose"] == "true"
        return httpx.Response(200, json=payload())

    monkeypatch.setattr(httpx, "Client", lambda **kwargs: original(transport=httpx.MockTransport(respond), **kwargs))
    assert YahooHistoryProvider().history("TEST").ticker == "TEST"


def test_timeout_is_unavailable(monkeypatch):
    original = httpx.Client

    def fail(request):
        raise httpx.ReadTimeout("test timeout", request=request)

    monkeypatch.setattr(httpx, "Client", lambda **kwargs: original(transport=httpx.MockTransport(fail), **kwargs))
    with pytest.raises(MarketDataError) as error:
        YahooHistoryProvider().history("TEST")
    assert error.value.status_code == 503
