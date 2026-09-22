"""Compose Overview from normalized history; never fetch external data here."""

import math

from app.api.schemas import HistoryPoint, OverviewResponse
from app.market_data.history import PriceHistory
from app.volatility.realized_vol import log_returns, realized_volatility


def optional_number(value: float) -> float | None:
    return float(value) if math.isfinite(value) else None


def build_overview(history: PriceHistory) -> OverviewResponse:
    prices = [row.adjusted_close if row.adjusted_close is not None else math.nan for row in history.prices]
    returns = log_returns(prices)
    hv20 = realized_volatility(prices, window=20)
    hv30 = realized_volatility(prices, window=30)
    latest = history.prices[-1]
    previous = history.prices[-2].close if len(history.prices) >= 2 else None
    change = latest.close - previous if latest.close is not None and previous is not None else None
    change_pct = optional_number(change / previous) if change is not None else None
    warnings = list(history.warnings)
    if not math.isfinite(hv20[-1]):
        warnings.append("HV20 unavailable: requires 21 consecutive valid adjusted closes (20 returns).")
    if not math.isfinite(hv30[-1]):
        warnings.append("HV30 unavailable: requires 31 consecutive valid adjusted closes (30 returns).")
    return OverviewResponse(
        ticker=history.ticker, currency=history.currency, source=history.source,
        timestamp=history.retrieved_at, as_of=latest.date, spot=latest.close,
        daily_change=change, daily_change_pct=change_pct,
        hv20=optional_number(hv20[-1]), hv30=optional_number(hv30[-1]),
        history=[HistoryPoint(date=row.date, close=row.close, adjusted_close=row.adjusted_close,
                              log_return=optional_number(returns[i]), hv20=optional_number(hv20[i]), hv30=optional_number(hv30[i]))
                 for i, row in enumerate(history.prices)],
        warnings=warnings,
    )
