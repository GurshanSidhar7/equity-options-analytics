"""Explain the latest included session without forecasts or invented values."""
from typing import TYPE_CHECKING

from app.explainability.models import ExplanationItem, ExplanationValue, OverviewExplanation, VolatilityComparison

if TYPE_CHECKING:
    from app.api.schemas import OverviewResponse


def explain_overview(data: "OverviewResponse") -> OverviewExplanation:
    currency = data.currency or "unspecified provider currency"
    unit = f"{currency} per share"
    previous = data.history[-2].close if len(data.history) >= 2 else None
    items = [ExplanationItem(
        id="latest-close", title="Latest close",
        plain_english=(f"{data.ticker}'s latest included completed daily close is {data.spot:.2f} {unit} on {data.as_of}. Think of it as a completed scoreboard value, not a live quote." if data.spot is not None else f"{data.ticker}'s latest included close is unavailable; an older close is not substituted."),
        why_it_matters="This anchors the historical overview and can serve as an editable spot proxy.",
        math_expression="Latest close = provider Close for the latest included completed session",
        numerical_example=f"Session: {data.as_of}; close: {data.spot if data.spot is not None else 'unavailable'} {unit}.",
        technical_note="Provider Close is split-adjusted, not dividend-adjusted. Today's exchange-local bar is conservatively excluded.",
        values=[ExplanationValue(label="Latest close", value=data.spot, unit=unit)],
    )]
    available = all(value is not None for value in (previous, data.spot, data.daily_change, data.daily_change_pct))
    items.append(ExplanationItem(
        id="daily-change", title="Latest daily change",
        plain_english=(f"On the latest included session, {data.ticker} moved from {previous:.2f} to {data.spot:.2f} {unit}: a {data.daily_change:+.2f} change ({data.daily_change_pct:+.2%})." if available else f"{data.ticker}'s daily change is unavailable because the latest or previous included close is missing."),
        why_it_matters="This compares two included closes; it does not attribute the movement to any headline.",
        math_expression="Change = P_t − P_(t−1); percentage change = (P_t − P_(t−1)) / P_(t−1)",
        numerical_example=(f"{data.spot:.4f} − {previous:.4f} = {data.daily_change:+.4f}; return = {data.daily_change_pct:+.6f} decimal." if available else "A valid pair of included closes is required; no change is invented."),
        technical_note="Daily price change uses Close and is not a dividend-adjusted total return.",
        values=[ExplanationValue(label="Previous included close", value=previous, unit=unit), ExplanationValue(label="Daily change", value=data.daily_change, unit=unit), ExplanationValue(label="Daily percentage change", value=data.daily_change_pct, unit="decimal return")],
    ))
    for window, value in ((20, data.hv20), (30, data.hv30)):
        items.append(ExplanationItem(
            id=f"hv{window}", title=f"HV{window}",
            plain_english=(f"{data.ticker}'s HV{window} is {value:.2%} annualized. It asks how variable the latest {window} adjusted daily log returns have actually been." if value is not None else f"{data.ticker}'s HV{window} is unavailable: {window + 1} consecutive valid adjusted closes are required."),
            why_it_matters="It measures historically realized variability, not future direction, a forecast, or implied volatility.",
            math_expression=f"r_t = ln(P_t / P_(t−1)); HV{window} = sample stdev(last {window} log returns, ddof=1) × sqrt({data.periods_per_year})",
            numerical_example=(f"HV{window} = {value:.6f} decimal = {value:.2%} annualized." if value is not None else "Missing or insufficient observations remain unavailable, rather than zero."),
            technical_note=f"Adjusted closes account for provider split/dividend adjustments. Sample variance divides by {window - 1}; annualization assumes stable variance and uncorrelated returns.",
            values=[ExplanationValue(label=f"HV{window}", value=value, unit="annual decimal volatility")],
        ))
    difference = abs(data.hv20 - data.hv30) * 100 if data.hv20 is not None and data.hv30 is not None else None
    relationship = "unavailable" if difference is None else "above" if data.hv20 > data.hv30 else "below" if data.hv20 < data.hv30 else "equal"
    comparison = VolatilityComparison(hv20=data.hv20, hv30=data.hv30, absolute_difference_pp=difference, relationship=relationship)
    description = ("HV20 and HV30 are exactly equal in the returned analytics." if relationship == "equal" else f"The 20-return realized measure is {difference:.2f} percentage points {relationship} the 30-return measure. The shorter window contained {'more' if relationship == 'above' else 'less'} realized variability." if difference is not None else "The comparison is unavailable until both HV20 and HV30 are available.")
    items.append(ExplanationItem(
        id="hv-comparison", title="HV20 versus HV30", plain_english=description,
        why_it_matters="The overlapping windows include different observations, so their historical variability can differ.",
        math_expression="Absolute percentage-point difference = |HV20 − HV30| × 100",
        numerical_example=(f"|{data.hv20:.6f} − {data.hv30:.6f}| × 100 = {difference:.4f} percentage points." if difference is not None else "Both realized-volatility measurements are required."),
        technical_note="Comparison uses exact Python values with no approximate-equality tolerance. Neither window establishes tomorrow's volatility or price direction.",
        values=[ExplanationValue(label="Absolute difference", value=difference, unit="percentage points")],
    ))
    return OverviewExplanation(items=items, comparison=comparison)
