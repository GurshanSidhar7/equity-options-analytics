from datetime import date, datetime

from typing import Literal

from pydantic import BaseModel, Field

from app.explainability.models import OverviewExplanation, PricingExplanation


class HistoryPoint(BaseModel):
    date: date
    close: float | None
    adjusted_close: float | None
    log_return: float | None
    hv20: float | None
    hv30: float | None


class OverviewResponse(BaseModel):
    ticker: str
    currency: str | None
    source: str
    timestamp: datetime  # Retrieval time in UTC, not a live quote timestamp.
    as_of: date  # Latest historical session returned, even if its close is missing.
    spot: float | None
    spot_basis: str = "Latest completed provider daily close; not a live quote"
    daily_change: float | None
    daily_change_pct: float | None  # Decimal simple return, despite the conventional name.
    hv20: float | None
    hv30: float | None
    periods_per_year: int = 252
    volatility_basis: str = "Sample standard deviation (ddof=1) of adjusted daily log returns"
    units: str = "Prices/change in provider currency per share; returns and annualized volatility in decimals"
    history: list[HistoryPoint]
    warnings: list[str]
    desk_translator: OverviewExplanation | None = None


class PricingRequest(BaseModel):
    spot: float = Field(gt=0)
    strike: float = Field(gt=0)
    time_to_expiry: float = Field(ge=0)
    time_unit: Literal["years", "days"] = "years"
    volatility: float = Field(ge=0)
    risk_free_rate: float
    dividend_yield: float
    option_type: Literal["call", "put"]


class GreeksResponse(BaseModel):
    delta: float | None
    gamma: float | None
    vega_per_vol_point: float | None
    theta_per_day: float | None


class GreekCurvePoint(GreeksResponse):
    spot: float


class PricingResponse(BaseModel):
    option_type: Literal["call", "put"]
    spot: float
    model_price: float
    intrinsic_value: float
    time_value: float
    time_to_expiry_years: float
    greeks: GreeksResponse
    greek_curve: list[GreekCurvePoint]
    desk_translator: PricingExplanation
    greek_units: str = "Delta: model-price change per 1 spot currency unit; Gamma: Delta change per 1 spot currency unit; Vega: price change per 1 volatility percentage point (0.01 decimal); Theta: price change per calendar day elapsed (ACT/365). All are per share."
    units: str = "Price values in currency units per share; rates and volatility are decimal annual values; time is in years"
    model: str = "Dividend-adjusted European Black-Scholes"
