from typing import Literal

from pydantic import BaseModel, Field


class ExplanationValue(BaseModel):
    label: str
    value: float | None
    unit: str


class ExplanationItem(BaseModel):
    id: str
    title: str
    plain_english: str
    why_it_matters: str
    math_expression: str
    numerical_example: str
    technical_note: str
    values: list[ExplanationValue] = Field(default_factory=list)


class VolatilityComparison(BaseModel):
    hv20: float | None
    hv30: float | None
    absolute_difference_pp: float | None
    relationship: Literal["above", "below", "equal", "unavailable"]


class OverviewExplanation(BaseModel):
    items: list[ExplanationItem]
    comparison: VolatilityComparison


class PricingScenarios(BaseModel):
    spot_strike_pct: float
    spot_relationship: Literal["above", "below", "equal"]
    spot_move: float = 1.0
    delta_model_change: float | None
    approx_delta_after_up_1: float | None
    volatility_before: float
    volatility_after: float
    vega_model_change: float | None
    elapsed_calendar_days: int = 1
    theta_model_change: float | None


class SensitivityCheck(BaseModel):
    current_model_price: float
    repriced_model_price: float
    actual_model_change: float
    delta_only_estimate: float
    delta_gamma_estimate: float


class PricingExplanation(BaseModel):
    items: list[ExplanationItem]
    scenarios: PricingScenarios
    sensitivity_check: SensitivityCheck | None
