"""Application liveness, historical Overview, and theoretical-pricing endpoints."""

from typing import Annotated
from functools import lru_cache

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.schemas import GreekCurvePoint, GreeksResponse, OverviewResponse, PricingRequest, PricingResponse
from app.explainability.pricing import explain_pricing
from app.news.models import NewsResponse
from app.news.provider import YahooFinanceNewsProvider
from app.news.service import NewsService
from app.market_data.history import MarketDataError, YahooHistoryProvider
from app.pricing.black_scholes import black_scholes
from app.pricing.greeks import greeks
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
    inputs = dict(
        strike=request.strike,
        time_to_expiry=time_to_expiry_years,
        volatility=request.volatility,
        risk_free_rate=request.risk_free_rate,
        dividend_yield=request.dividend_yield,
        option_type=request.option_type,
    )
    sensitivities = greeks(spot=request.spot, **inputs)
    curve: list[GreekCurvePoint] = []
    if sensitivities.delta is not None:
        spots = np.linspace(min(request.spot * 0.7, request.strike * 0.8), max(request.spot * 1.3, request.strike * 1.2), 61)
        sampled = greeks(spot=spots, **inputs)
        curve = [GreekCurvePoint(
            spot=float(spot),
            delta=float(sampled.delta[index]),
            gamma=float(sampled.gamma[index]),
            vega_per_vol_point=float(sampled.vega_per_vol_point[index]),
            theta_per_day=float(sampled.theta_per_day[index]),
        ) for index, spot in enumerate(spots)]
    return PricingResponse(
        option_type=request.option_type,
        spot=request.spot,
        model_price=float(result.model_price),
        intrinsic_value=float(result.intrinsic_value),
        time_value=float(result.time_value),
        time_to_expiry_years=time_to_expiry_years,
        greeks=GreeksResponse(**vars(sensitivities)),
        greek_curve=curve,
        desk_translator=explain_pricing(request, time_to_expiry_years, result, sensitivities),
    )


@lru_cache(maxsize=1)
def get_news_service() -> NewsService:
    return NewsService(YahooFinanceNewsProvider())


@router.get("/api/news", response_model=NewsResponse)
def news(
    ticker: Annotated[str, Query(min_length=1, max_length=20, pattern=r"^[A-Za-z0-9][A-Za-z0-9.\-]{0,19}$")],
    service: Annotated[NewsService, Depends(get_news_service)],
) -> NewsResponse:
    return service.get(ticker.upper())
