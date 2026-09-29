"""Local sensitivities of the dividend-adjusted European Black--Scholes price.

Delta and Gamma use a one-currency-unit spot move. Vega is returned per 0.01
change in decimal annual volatility, and Theta per calendar day of time decay
(ACT/365). At expiry or effectively zero volatility the smooth derivatives are
not reported, because the payoff or deterministic value can have a kink.
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.special import ndtr

from app.pricing.black_scholes import NumberOrArray, OptionType, black_scholes

GreekValue = NumberOrArray | None


@dataclass(frozen=True)
class GreeksResult:
    delta: GreekValue
    gamma: GreekValue
    vega_per_vol_point: GreekValue
    theta_per_day: GreekValue


def greeks(
    spot: ArrayLike,
    strike: ArrayLike,
    time_to_expiry: ArrayLike,
    volatility: ArrayLike,
    risk_free_rate: ArrayLike,
    dividend_yield: ArrayLike,
    option_type: OptionType,
) -> GreeksResult:
    """Return analytic partial derivatives, broadcasting NumPy-compatible inputs.

    For vector inputs, unavailable entries are NaN; for scalars they are None.
    The pricing function supplies exactly the same input validation and boundary
    conventions as the model value shown beside these Greeks.
    """
    black_scholes(spot, strike, time_to_expiry, volatility, risk_free_rate, dividend_yield, option_type)
    s, k, t, sigma, r, q = np.broadcast_arrays(*(
        np.asarray(value, dtype=float)
        for value in (spot, strike, time_to_expiry, volatility, risk_free_rate, dividend_yield)
    ))
    unavailable = (t <= 1e-12) | (sigma <= 1e-12)
    safe_t = np.where(unavailable, 1.0, t)
    safe_sigma = np.where(unavailable, 1.0, sigma)
    root_t = np.sqrt(safe_t)
    d1 = (np.log(s / k) + (r - q + 0.5 * safe_sigma**2) * safe_t) / (safe_sigma * root_t)
    d2 = d1 - safe_sigma * root_t
    discounted_spot = s * np.exp(-q * safe_t)
    discounted_strike = k * np.exp(-r * safe_t)
    density = np.exp(-0.5 * d1**2) / np.sqrt(2.0 * np.pi)

    gamma = np.exp(-q * safe_t) * density / (s * safe_sigma * root_t)
    vega_per_vol_point = discounted_spot * density * root_t * 0.01
    common_theta = -discounted_spot * density * safe_sigma / (2.0 * root_t)
    if option_type == "call":
        delta = np.exp(-q * safe_t) * ndtr(d1)
        annual_theta = common_theta - r * discounted_strike * ndtr(d2) + q * discounted_spot * ndtr(d1)
    else:
        delta = -np.exp(-q * safe_t) * ndtr(-d1)
        annual_theta = common_theta + r * discounted_strike * ndtr(-d2) - q * discounted_spot * ndtr(-d1)

    def available(value: NDArray[np.float64]) -> GreekValue:
        masked = np.where(unavailable, np.nan, value)
        if masked.ndim == 0:
            return None if bool(unavailable) else float(masked)
        return masked

    return GreeksResult(
        delta=available(delta),
        gamma=available(gamma),
        vega_per_vol_point=available(vega_per_vol_point),
        theta_per_day=available(annual_theta / 365.0),
    )
