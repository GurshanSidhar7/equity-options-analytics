import math
import statistics

import numpy as np
import pytest

from app.volatility.realized_vol import log_returns, realized_volatility


def test_known_manual_sample():
    result = log_returns([100, 101, 100])
    assert np.isnan(result[0])
    assert result[1] == pytest.approx(math.log(1.01))
    assert result[2] == pytest.approx(-math.log(1.01))
    assert realized_volatility([100, 101, 100], 2)[-1] == pytest.approx(0.2233843736256063)


@pytest.mark.parametrize("window", [20, 30])
def test_constant_prices_and_window_boundary(window):
    result = realized_volatility([100] * (window + 3), window)
    assert np.all(np.isnan(result[:window]))
    np.testing.assert_array_equal(result[window:], 0)


def test_each_rolling_window_against_independent_sample_std():
    returns = np.array([0.01, -0.03, 0.02, 0.015, -0.01, 0.04])
    prices = 100 * np.exp(np.r_[0, np.cumsum(returns)])
    result = realized_volatility(prices, 3)
    for index in range(3, len(prices)):
        expected = statistics.stdev(returns[index - 3:index]) * math.sqrt(252)
        assert result[index] == pytest.approx(expected)


def test_future_data_does_not_change_past_results():
    prices = [100, 102, 101, 105, 99, 98, 100]
    np.testing.assert_allclose(realized_volatility(prices, 3), realized_volatility(prices + [2000], 3)[:-1], equal_nan=True)


def test_missing_price_invalidates_returns_and_windows_then_recovers():
    prices = [100, 101, np.nan, 103, 104, 105, 106]
    returns = log_returns(prices)
    assert np.isnan(returns[2]) and np.isnan(returns[3])
    result = realized_volatility(prices, 2)
    assert np.all(np.isnan(result[:5]))
    assert np.all(np.isfinite(result[5:]))


def test_scale_invariance_and_annualization():
    prices = np.array([100, 101, 99, 104])
    np.testing.assert_allclose(log_returns(prices), log_returns(prices * 100), equal_nan=True)
    assert realized_volatility(prices, 3, 252)[-1] == pytest.approx(realized_volatility(prices, 3, 63)[-1] * 2)


@pytest.mark.parametrize("prices", [[], [100], [100, 101]])
def test_insufficient_history_is_unavailable(prices):
    assert np.all(np.isnan(realized_volatility(prices, 20)))


@pytest.mark.parametrize("prices", [[0, 1], [-1, 2], [1, np.inf], [[100, 101]]])
def test_invalid_prices_rejected(prices):
    with pytest.raises(ValueError):
        log_returns(prices)


@pytest.mark.parametrize("window", [0, 1, 20.5, True])
def test_invalid_windows(window):
    with pytest.raises(ValueError):
        realized_volatility([100, 101], window)


@pytest.mark.parametrize("factor", [0, 367, 252.5, True])
def test_invalid_annualization(factor):
    with pytest.raises(ValueError):
        realized_volatility([100, 101, 100], 2, factor)
