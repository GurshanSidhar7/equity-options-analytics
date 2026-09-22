"""Dividend-adjusted Black--Scholes pricing for European calls and puts.

Inputs use years and decimal annual rates/volatility.  The implementation is pure
analytics: it does not fetch market data or interpret the result as a market quote.
"""

from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.special import ndtr

OptionType = Literal["call", "put"]
NumberOrArray = float | NDArray[np.float64]

_TIME_EPSILON = 1e-12
_VOLATILITY_EPSILON = 1e-12


@dataclass(frozen=True)
class BlackScholesResult:
    model_price: NumberOrArray
    intrinsic_value: NumberOrArray
    time_value: NumberOrArray


def black_scholes(
    spot: ArrayLike,
    strike: ArrayLike,
    time_to_expiry: ArrayLike,
    volatility: ArrayLike,
    risk_free_rate: ArrayLike,
    dividend_yield: ArrayLike,
    option_type: OptionType,
) -> BlackScholesResult:
    """Price European options, broadcasting scalar and NumPy-compatible inputs.

    At expiry the value is payoff.  With effectively zero volatility before
    expiry, the discounted deterministic payoff is used, avoiding division by
    zero while preserving the model's limiting value.
    """
    if option_type not in ("call", "put"):
        raise ValueError("option_type must be 'call' or 'put'")

    arrays = np.broadcast_arrays(
        np.asarray(spot, dtype=float),
        np.asarray(strike, dtype=float),
        np.asarray(time_to_expiry, dtype=float),
        np.asarray(volatility, dtype=float),
        np.asarray(risk_free_rate, dtype=float),
        np.asarray(dividend_yield, dtype=float),
    )
    s, k, t, sigma, r, q = arrays
    if not all(np.all(np.isfinite(value)) for value in arrays):
        raise ValueError("all inputs must be finite")
    if np.any(s <= 0) or np.any(k <= 0):
        raise ValueError("spot and strike must be greater than zero")
    if np.any(t < 0) or np.any(sigma < 0):
        raise ValueError("time_to_expiry and volatility cannot be negative")

    intrinsic = np.maximum(s - k, 0.0) if option_type == "call" else np.maximum(k - s, 0.0)
    at_expiry = t <= _TIME_EPSILON
    zero_volatility = sigma <= _VOLATILITY_EPSILON

    discounted_spot = s * np.exp(-q * t)
    discounted_strike = k * np.exp(-r * t)
    deterministic = (
        np.maximum(discounted_spot - discounted_strike, 0.0)
        if option_type == "call"
        else np.maximum(discounted_strike - discounted_spot, 0.0)
    )

    safe_t = np.where(at_expiry, 1.0, t)
    safe_sigma = np.where(zero_volatility, 1.0, sigma)
    root_t = np.sqrt(safe_t)
    d1 = (np.log(s / k) + (r - q + 0.5 * safe_sigma**2) * safe_t) / (safe_sigma * root_t)
    d2 = d1 - safe_sigma * root_t
    if option_type == "call":
        regular = discounted_spot * ndtr(d1) - discounted_strike * ndtr(d2)
    else:
        regular = discounted_strike * ndtr(-d2) - discounted_spot * ndtr(-d1)

    model_price = np.where(at_expiry, intrinsic, np.where(zero_volatility, deterministic, regular))
    time_value = model_price - intrinsic
    return BlackScholesResult(
        model_price=_scalar_if_zero_dim(model_price),
        intrinsic_value=_scalar_if_zero_dim(intrinsic),
        time_value=_scalar_if_zero_dim(time_value),
    )


def _scalar_if_zero_dim(value: NDArray[np.float64]) -> NumberOrArray:
    return float(value) if value.ndim == 0 else value
