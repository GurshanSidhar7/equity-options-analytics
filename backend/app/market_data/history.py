"""Yahoo Finance daily-chart adapter. This unofficial endpoint may be unavailable.

Only this module fetches external data. No generated or fallback prices are used.
"""

from dataclasses import dataclass
from datetime import date, datetime, timezone
import math
from urllib.parse import quote
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx


class MarketDataError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class DailyPrice:
    date: date
    close: float | None
    adjusted_close: float | None


@dataclass(frozen=True)
class PriceHistory:
    ticker: str
    currency: str | None
    retrieved_at: datetime
    prices: list[DailyPrice]
    warnings: list[str]
    source: str = "Yahoo Finance daily chart (unofficial)"


def valid_price(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value) if math.isfinite(value) and value > 0 else None


def normalize_history(payload: dict, ticker: str, now: datetime) -> PriceHistory:
    """Normalize provider fields and preserve missing values as explicit gaps."""
    try:
        chart = payload["chart"]
        if chart.get("error") or not chart.get("result"):
            raise MarketDataError("No historical prices are available for this ticker.", 404)
        data = chart["result"][0]
        meta = data["meta"]
        if meta.get("instrumentType") not in {"EQUITY", "ETF"}:
            raise MarketDataError("Only equity and ETF daily histories are supported.", 422)
        local_today = now.astimezone(ZoneInfo(meta["exchangeTimezoneName"])).date()
        timestamps = data.get("timestamp") or []
        closes = data["indicators"]["quote"][0]["close"]
        adjusted_entries = data["indicators"].get("adjclose") or []
        adjusted = adjusted_entries[0].get("adjclose") if adjusted_entries else None
        if len(closes) != len(timestamps) or (adjusted is not None and len(adjusted) != len(timestamps)):
            raise ValueError("Mismatched daily arrays")
        rows = []
        for index, timestamp in enumerate(timestamps):
            day = datetime.fromtimestamp(timestamp, ZoneInfo(meta["exchangeTimezoneName"])).date()
            # Conservative EOD convention: exclude today's bar even after the close.
            if day >= local_today:
                continue
            rows.append(DailyPrice(day, valid_price(closes[index]), valid_price(adjusted[index]) if adjusted is not None else None))
        rows.sort(key=lambda row: row.date)
        if len({row.date for row in rows}) != len(rows):
            raise ValueError("Duplicate session dates")
        if not rows:
            raise MarketDataError("No completed daily sessions are available for this ticker.", 404)
        warnings = [
            "Latest close is a historical spot proxy, not a live quote. Today's exchange-local bar is excluded, even after the close.",
            "HV uses provider split/dividend-adjusted closes; daily change uses provider closes (split-adjusted, not dividend-adjusted).",
            "Missing sessions are not checked against an exchange calendar. No prices are filled or interpolated.",
            "252-session annualization assumes stable variance and uncorrelated returns. Historical volatility is not a forecast or implied volatility.",
        ]
        if any(row.close is None or row.adjusted_close is None for row in rows):
            warnings.append("Missing or invalid prices are retained as gaps; affected returns and volatility windows are unavailable.")
        if (local_today - rows[-1].date).days > 4:
            warnings.append("Latest available session is more than four calendar days old; data may be stale.")
        currency = meta.get("currency")
        if not isinstance(currency, str) or not currency:
            currency = None
            warnings.append("Provider did not supply a currency; no currency is assumed.")
        return PriceHistory(ticker, currency, now, rows, warnings)
    except MarketDataError:
        raise
    except (AttributeError, KeyError, TypeError, ValueError, IndexError, OverflowError, OSError, ZoneInfoNotFoundError) as exc:
        raise MarketDataError("The market-data provider returned an unsupported historical-data format.") from exc


class YahooHistoryProvider:
    def history(self, ticker: str) -> PriceHistory:
        try:
            with httpx.Client(timeout=12, headers={"User-Agent": "Mozilla/5.0"}) as client:
                response = client.get(
                    f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(ticker, safe='')}",
                    params={"range": "1y", "interval": "1d", "includeAdjustedClose": "true"},
                )
            if response.status_code == 404:
                raise MarketDataError("No historical prices are available for this ticker.", 404)
            if response.status_code == 429:
                raise MarketDataError("The market-data provider is rate limiting requests. Please try again later.", 503)
            response.raise_for_status()
            return normalize_history(response.json(), ticker, datetime.now(timezone.utc))
        except MarketDataError:
            raise
        except (httpx.HTTPError, ValueError) as exc:
            raise MarketDataError("Historical market data is temporarily unavailable. Please try again later.", 503) from exc
