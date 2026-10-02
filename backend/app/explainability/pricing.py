"""Submitted-result explanations; reuse pricing, never recompute Greek formulas."""
from typing import TYPE_CHECKING

from app.explainability.models import ExplanationItem, ExplanationValue, PricingExplanation, PricingScenarios, SensitivityCheck
from app.pricing.black_scholes import BlackScholesResult, black_scholes
from app.pricing.greeks import GreeksResult

if TYPE_CHECKING:
    from app.api.schemas import PricingRequest


def direction(value: float) -> str:
    return f"{abs(value):.6f} currency units {'increase' if value > 0 else 'decrease' if value < 0 else 'change (zero)'}"


def explain_pricing(request: "PricingRequest", years: float, result: BlackScholesResult, greek: GreeksResult) -> PricingExplanation:
    s, k = request.spot, request.strike
    pct = (s - k) / k * 100
    relationship = "above" if s > k else "below" if s < k else "equal"
    scenarios = PricingScenarios(
        spot_strike_pct=pct, spot_relationship=relationship,
        delta_model_change=greek.delta, approx_delta_after_up_1=greek.delta + greek.gamma if greek.delta is not None and greek.gamma is not None else None,
        volatility_before=request.volatility, volatility_after=request.volatility + 0.01,
        vega_model_change=greek.vega_per_vol_point, theta_model_change=greek.theta_per_day,
    )
    def item(id, title, plain, why, math, example, note, values=()):
        return ExplanationItem(id=id, title=title, plain_english=plain, why_it_matters=why, math_expression=math, numerical_example=example, technical_note=note, values=[ExplanationValue(label=label, value=value, unit=unit) for label, value, unit in values])

    model_formula = (
        "V_call = S e^(−qT) N(d1) − K e^(−rT) N(d2)"
        if request.option_type == "call"
        else "V_put = K e^(−rT) N(−d2) − S e^(−qT) N(−d1)"
    ) + "; d1 = [ln(S/K) + (r−q+σ²/2)T] / (σ√T); d2 = d1 − σ√T"
    payoff = "max(S − K, 0)" if request.option_type == "call" else "max(K − S, 0)"
    itm = s > k if request.option_type == "call" else s < k
    spot_text = "Spot and strike are currently equal." if relationship == "equal" else f"Spot is {abs(pct):.2f}% {relationship} the selected strike."
    items = [item("assumptions", "Submitted assumptions",
        f"This European {request.option_type} has spot {s:.4f}, strike {k:.4f}, and {years:.6f} years remaining. Assumed annual volatility is {request.volatility:.2%}, risk-free rate {request.risk_free_rate:.2%}, and continuous dividend yield {request.dividend_yield:.2%}.",
        "A call pays for spot above strike at expiry; a put pays for spot below strike. European exercise occurs at expiry only.",
        "T = days / 365 for day inputs; rates, dividend yield, and volatility use annual decimals",
        f"Submitted time: {request.time_to_expiry:g} {request.time_unit}; T = {years:.6f} years; σ = {request.volatility:g} decimal.",
        "Volatility is a user-entered assumption, not implied volatility. Rates and yield are continuously compounded.",
        [("Spot", s, "currency / share"), ("Strike", k, "currency / share"), ("Time", years, "years"), ("Volatility", request.volatility, "annual decimal"), ("Risk-free rate", request.risk_free_rate, "annual decimal"), ("Dividend yield", request.dividend_yield, "annual decimal")]),
        item("spot-strike", "Spot versus strike", spot_text + f" This {request.option_type} has {'a positive' if itm else 'zero'} spot intrinsic payoff component.",
        "The relationship describes current spot moneyness, not a forecast of the expiry payoff.", "Spot relationship (%) = (S − K) / K × 100",
        f"({s:g} − {k:g}) / {k:g} × 100 = {pct:+.4f}%.", "Equality means exact equality; no exchange-specific ATM band is assumed.", [("Spot relative to strike", pct, "%")]),
        item("model-value", "Model value", f"Under the submitted assumptions, Black–Scholes produces a theoretical value of {result.model_price:.6f} currency units per option share. This is a model output, not the observed market price of an option.",
        "This provides a consistent model reference for exploring assumptions.", model_formula,
        f"V = {result.model_price:.6f} currency units per share.", "N denotes the standard-normal CDF. Smooth formulas apply before expiry with positive volatility; boundaries use payoff or discounted deterministic payoff. Constant volatility, rates, and dividend yield; European exercise.", [("Model value", result.model_price, "currency / share")]),
        item("intrinsic", "Intrinsic value", f"If expiry occurred at the current spot, the payoff component would be {result.intrinsic_value:.6f} currency units per option share.",
        "This isolates the spot payoff component without assuming immediate European exercise.", f"Intrinsic = {payoff}", f"Intrinsic = {result.intrinsic_value:.6f} per share.", "A European option cannot necessarily be exercised now.", [("Intrinsic value", result.intrinsic_value, "currency / share")]),
        item("time-value", "Model time value", f"Model value {result.model_price:.6f} minus intrinsic value {result.intrinsic_value:.6f} gives model time value {result.time_value:.6f} per share.",
        "This decomposes the theoretical model output, rather than an observed market time premium.", "Model time value = model value − spot intrinsic value", f"{result.model_price:.6f} − {result.intrinsic_value:.6f} = {result.time_value:.6f}.",
        "Model time value can be negative for dividend-paying European options because early exercise is unavailable.", [("Model time value", result.time_value, "currency / share")]),
    ]
    local = "Local model sensitivity, not a guarantee of how a market quote will move. Other submitted inputs stay fixed."
    if greek.delta is None:
        items.append(item("greeks-unavailable", "Greeks unavailable", "Smooth Greek sensitivities are unavailable at expiry or effectively zero volatility (≤ 1e−12), where the payoff or deterministic model value may have a kink.",
            "The model price remains available, but no smooth scenario numbers are invented.", "Smooth derivatives require T > 1e−12 and σ > 1e−12", "No Delta, Gamma, Vega, or Theta scenario is returned.", local))
        return PricingExplanation(items=items, scenarios=scenarios, sensitivity_check=None)
    items.extend([
        item("delta", "Delta", f"For a small +1 currency-unit stock move, the model locally estimates approximately a {direction(greek.delta)} in option value per share, holding other inputs fixed.",
        "Delta measures the immediate slope of model value with respect to spot.", "ΔV ≈ Delta × ΔS", f"ΔV ≈ {greek.delta:.6f} × 1 = {greek.delta:+.6f} per share.", local + " Delta is not the probability of expiring in the money.", [("Delta", greek.delta, "price / +1 spot"), ("Local model change", scenarios.delta_model_change, "currency / share")]),
        item("gamma", "Gamma", f"Delta is {greek.delta:.6f}. With Gamma {greek.gamma:.6f}, a small +1 spot move takes Delta to approximately {scenarios.approx_delta_after_up_1:.6f} locally.",
        "Gamma measures how quickly Delta itself changes as spot changes.", "Delta_new ≈ Delta + Gamma × ΔS", f"{greek.delta:.6f} + {greek.gamma:.6f} × 1 = {scenarios.approx_delta_after_up_1:.6f}.", local + " Gamma itself can change after spot moves.", [("Gamma", greek.gamma, "Delta / +1 spot"), ("Approximate Delta after +1", scenarios.approx_delta_after_up_1, "price / +1 spot")]),
        item("vega", "Vega", f"A one-volatility-point increase from {scenarios.volatility_before:.2%} to {scenarios.volatility_after:.2%} corresponds locally to approximately a {direction(greek.vega_per_vol_point)} in model value per share.",
        "Vega links model value to the volatility assumption, holding other inputs fixed.", "1 volatility point = 0.01 decimal; ΔV ≈ Vega_per_vol_point × 1", f"σ: {scenarios.volatility_before:g} → {scenarios.volatility_after:g}; ΔV ≈ {greek.vega_per_vol_point:+.6f} per share.", local,
        [("Volatility before", scenarios.volatility_before, "annual decimal"), ("Volatility after", scenarios.volatility_after, "annual decimal"), ("Local model change", greek.vega_per_vol_point, "currency / share")]),
        item("theta", "Theta", f"If one calendar day passes while spot, volatility, rates, and dividends stay fixed, the model locally estimates approximately a {direction(greek.theta_per_day)} in value per option share.",
        "Theta measures sensitivity to calendar time passing; its sign depends on the assumptions.", "Theta_per_day = −(∂V/∂T) / 365; ΔV ≈ Theta_per_day × 1 day", f"One calendar day: ΔV ≈ {greek.theta_per_day:+.6f} per share.", local + " This is a tangent estimate, including when less than one day remains.", [("Local model change", greek.theta_per_day, "currency / share / calendar day")]),
    ])
    repriced = black_scholes(s + 1, k, years, request.volatility, request.risk_free_rate, request.dividend_yield, request.option_type)
    check = SensitivityCheck(current_model_price=result.model_price, repriced_model_price=repriced.model_price, actual_model_change=repriced.model_price - result.model_price, delta_only_estimate=greek.delta, delta_gamma_estimate=greek.delta + 0.5 * greek.gamma)
    items.append(item("sensitivity-check", "Model Sensitivity Check", "Delta is a tangent approximation. Gamma accounts for curvature and can improve the approximation for a finite +1 spot move.",
        "Compare local approximations with repricing the same model while changing only spot.", "ΔV ≈ Delta × 1; ΔV ≈ Delta × 1 + 0.5 × Gamma × 1²; model change = V(S + 1) − V(S)",
        f"Delta-only: {check.delta_only_estimate:+.6f}; Delta + Gamma: {check.delta_gamma_estimate:+.6f}; repriced model change: {check.actual_model_change:+.6f}.",
        "This is a model sensitivity demonstration, not realized trading P&L or a market-price prediction.", [("Current model price", check.current_model_price, "currency / share"), ("Repriced model price", check.repriced_model_price, "currency / share"), ("Repriced model change", check.actual_model_change, "currency / share"), ("Delta-only estimate", check.delta_only_estimate, "currency / share"), ("Delta + Gamma estimate", check.delta_gamma_estimate, "currency / share")]))
    return PricingExplanation(items=items, scenarios=scenarios, sensitivity_check=check)
