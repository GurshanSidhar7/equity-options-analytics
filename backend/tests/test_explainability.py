"""Explanations are grounded in quantitative outputs, with no live dependencies."""
import pytest

from app.api.routes import pricing
from app.api.schemas import PricingRequest
from app.explainability.overview import explain_overview
from app.pricing.black_scholes import black_scholes
from app.volatility.overview import build_overview
from tests.test_overview import TestProvider


BASE = dict(spot=100, strike=100, time_to_expiry=1, volatility=0.2,
            risk_free_rate=0.05, dividend_yield=0.02, option_type="call")


def priced(**changes):
    return pricing(PricingRequest(**(BASE | changes)))


def item(explanation, id):
    return next(row for row in explanation.items if row.id == id)


@pytest.mark.parametrize("hv20,hv30,relationship,difference", [
    (0.24, 0.20, "above", 4), (0.15, 0.20, "below", 5),
    (0.2, 0.2, "equal", 0), (0.2000001, 0.2, "above", 0.00001),
    (None, 0.2, "unavailable", None), (0.2, None, "unavailable", None),
])
def test_hv_comparison(hv20, hv30, relationship, difference):
    data = build_overview(TestProvider().history("MSFT")).model_copy(update={"hv20": hv20, "hv30": hv30})
    comparison = explain_overview(data).comparison
    assert comparison.hv20 == hv20 and comparison.hv30 == hv30
    assert comparison.relationship == relationship
    assert comparison.absolute_difference_pp == (pytest.approx(difference) if difference is not None else None)


def test_overview_ticker_close_daily_change_and_units():
    data = build_overview(TestProvider().history("MSFT"))
    explanation = data.desk_translator
    assert "MSFT" in item(explanation, "latest-close").plain_english
    assert "not a live quote" in item(explanation, "latest-close").plain_english
    daily = item(explanation, "daily-change")
    assert [row.value for row in daily.values] == [276, 2, pytest.approx(2 / 276)]
    assert "276.00" in daily.plain_english and "278.00" in daily.plain_english
    for window in (20, 30):
        row = item(explanation, f"hv{window}")
        assert "sqrt(252)" in row.math_expression and "ddof=1" in row.math_expression
        assert f"latest {window}" in row.plain_english
        assert "not future direction" in row.why_it_matters
        assert "implied volatility" in row.why_it_matters
        assert row.values[0].value == getattr(data, f"hv{window}")
    prose = " ".join(row.plain_english for row in explanation.items).lower()
    assert all(phrase not in prose for phrase in ("will rise", "will fall", "will remain elevated"))


def test_overview_missing_close_and_missing_windows():
    data = build_overview(TestProvider().history("GAP"))
    for id in ("latest-close", "daily-change", "hv20", "hv30", "hv-comparison"):
        assert "unavailable" in item(data.desk_translator, id).plain_english
    assert data.desk_translator.comparison.absolute_difference_pp is None
    data = build_overview(TestProvider().history("SHORT"))
    assert "unavailable" in item(data.desk_translator, "hv30").plain_english
    data.daily_change = None
    assert "unavailable" in item(explain_overview(data), "daily-change").plain_english


@pytest.mark.parametrize("option_type,word", [("call", "increase"), ("put", "decrease")])
def test_delta_and_scenarios_reuse_exact_outputs(option_type, word):
    result = priced(option_type=option_type)
    explanation = result.desk_translator
    scenario = explanation.scenarios
    assert scenario.delta_model_change == result.greeks.delta
    assert word in item(explanation, "delta").plain_english
    assert "increase by -" not in item(explanation, "delta").plain_english
    assert scenario.approx_delta_after_up_1 == result.greeks.delta + result.greeks.gamma
    assert scenario.volatility_before == 0.2
    assert scenario.volatility_after == pytest.approx(0.21)
    assert "20.00% to 21.00%" in item(explanation, "vega").plain_english
    assert scenario.vega_model_change == result.greeks.vega_per_vol_point
    assert scenario.theta_model_change == result.greeks.theta_per_day
    assert "0.01 decimal" in item(explanation, "vega").math_expression
    assert "not the observed market price" in item(explanation, "model-value").plain_english
    assert "European" in item(explanation, "intrinsic").technical_note
    assert "negative" in item(explanation, "time-value").technical_note
    if option_type == "call":
        assert result.model_price == pytest.approx(9.227006, abs=1e-6)
        assert scenario.delta_model_change == pytest.approx(0.586851146)


@pytest.mark.parametrize("spot,relationship,pct", [(103.2, "above", 3.2), (95.3, "below", -4.7), (100, "equal", 0)])
@pytest.mark.parametrize("option_type", ["call", "put"])
def test_exact_spot_relationship(spot, relationship, pct, option_type):
    result = priced(spot=spot, option_type=option_type)
    assert result.desk_translator.scenarios.spot_relationship == relationship
    assert result.desk_translator.scenarios.spot_strike_pct == pytest.approx(pct)
    assert ("positive" in item(result.desk_translator, "spot-strike").plain_english) == (result.intrinsic_value > 0)


@pytest.mark.parametrize("changes,word", [({}, "decrease"), ({"option_type": "put", "spot": 50, "risk_free_rate": 0.1, "dividend_yield": 0}, "increase")])
def test_theta_sign_is_not_hardcoded(changes, word):
    result = priced(**changes)
    assert word in item(result.desk_translator, "theta").plain_english
    assert (result.greeks.theta_per_day > 0) == (word == "increase")


@pytest.mark.parametrize("changes", [{"time_to_expiry": 0}, {"volatility": 0}, {"volatility": 1e-14}, {"time_to_expiry": 1e-14}])
def test_greek_boundaries_are_educational_and_not_fabricated(changes):
    explanation = priced(**changes).desk_translator
    assert explanation.sensitivity_check is None
    assert explanation.scenarios.delta_model_change is None
    assert explanation.scenarios.approx_delta_after_up_1 is None
    assert explanation.scenarios.vega_model_change is None
    assert explanation.scenarios.theta_model_change is None
    assert "kink" in item(explanation, "greeks-unavailable").plain_english
    assert not any(row.id == "delta" for row in explanation.items)


def test_sensitivity_check_reprices_existing_model():
    result = priced()
    check = result.desk_translator.sensitivity_check
    repriced = black_scholes(101, 100, 1, 0.2, 0.05, 0.02, "call").model_price
    assert check.current_model_price == result.model_price
    assert check.repriced_model_price == repriced
    assert check.actual_model_change == repriced - result.model_price
    assert check.delta_only_estimate == result.greeks.delta
    assert check.delta_gamma_estimate == result.greeks.delta + 0.5 * result.greeks.gamma
    assert abs(check.actual_model_change - check.delta_gamma_estimate) < abs(check.actual_model_change - check.delta_only_estimate)


def test_submitted_day_units_and_negative_time_value_are_preserved():
    result = priced(spot=200, dividend_yield=0.5, time_to_expiry=365, time_unit="days")
    assert result.time_to_expiry_years == 1
    assert result.time_value < 0
    assert item(result.desk_translator, "time-value").values[0].value == result.time_value
    assert "365 days" in item(result.desk_translator, "assumptions").numerical_example
