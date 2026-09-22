"""Application liveness, historical Overview, and theoretical-pricing endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.schemas import OverviewResponse, PricingRequest, PricingResponse
from app.market_data.history import MarketDataError, YahooHistoryProvider
from app.pricing.black_scholes import black_scholes
from app.volatility.overview import build_overview

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def get_history_provider() -> YahooHistoryProvider:
    return YahooHistoryProvider()


@router.get("/api/overview", response_model=OverviewResponse)
def overview(
    ticker: Annotated[str, Query(min_length=1, max_length=20, pattern=r"^[A-Za-z0-9][A-Za-z0-9.\-]{0,19}$")],
    provider: Annotated[YahooHistoryProvider, Depends(get_history_provider)],
) -> OverviewResponse:
    try:
        return build_overview(provider.history(ticker.upper()))
    except MarketDataError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.post("/api/pricing", response_model=PricingResponse)
def pricing(request: PricingRequest) -> PricingResponse:
    time_to_expiry_years = (
        request.time_to_expiry / 365.0
        if request.time_unit == "days"
        else request.time_to_expiry
    )
    result = black_scholes(
        spot=request.spot,
        strike=request.strike,
        time_to_expiry=time_to_expiry_years,
        volatility=request.volatility,
        risk_free_rate=request.risk_free_rate,
        dividend_yield=request.dividend_yield,
        option_type=request.option_type,
    )
    return PricingResponse(
        option_type=request.option_type,
        model_price=float(result.model_price),
        intrinsic_value=float(result.intrinsic_value),
        time_value=float(result.time_value),
        time_to_expiry_years=time_to_expiry_years,
    )
