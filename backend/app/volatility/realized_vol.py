"""Daily log returns and trailing sample volatility. No data-provider calls.

Prices must represent successive daily sessions with a consistent adjustment basis.
Missing prices are NaN; they remain gaps, never filled or dropped. Outputs align
with input prices. Volatility is an annualized decimal, with ddof=1 and 252 sessions.
"""

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray


def log_returns(prices: ArrayLike) -> NDArray[np.float64]:
    """Return aligned ln(P[t])-ln(P[t-1]); first observation has no return."""
    values = np.asarray(prices, dtype=float)
    if values.ndim != 1:
        raise ValueError("Prices must be a one-dimensional sequence.")
    if np.any(np.isinf(values)) or np.any(values <= 0):
        raise ValueError("Observed prices must be positive and finite; use NaN for missing data.")
    result = np.full(values.size, np.nan)
    result[1:] = np.diff(np.log(values))
    return result


def realized_volatility(prices: ArrayLike, window: int = 20, periods_per_year: int = 252) -> NDArray[np.float64]:
    """Trailing volatility over window returns (window+1 prices), with no lookahead.

    A result requires a full window of valid daily returns. Leading and incomplete
    windows are NaN. Square-root annualization assumes uncorrelated daily returns
    with stable variance. Window lengths are sessions, not calendar days.
    """
    if type(window) is not int or window < 2:
        raise ValueError("window must be an integer of at least two returns.")
    if type(periods_per_year) is not int or not 1 <= periods_per_year <= 366:
        raise ValueError("periods_per_year must be an integer from 1 to 366.")
    returns = pd.Series(log_returns(prices))
    return (returns.rolling(window, min_periods=window).std(ddof=1) * np.sqrt(periods_per_year)).to_numpy()
