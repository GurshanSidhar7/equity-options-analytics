import numpy as np
import pytest

from app.pricing.black_scholes import black_scholes
from app.pricing.greeks import greeks


BASE = dict(spot=100.0, strike=100.0, time_to_expiry=1.0,
            volatility=0.2, risk_free_rate=0.05, dividend_yield=0.02)


def price(option_type, **changes):
    return black_scholes(**(BASE | changes), option_type=option_type).model_price


@pytest.mark.parametrize("option_type", ["call", "put"])
@pytest.mark.parametrize("spot,time,vol,rate,yield_", [
    (100.0, 1.0, 0.2, 0.05, 0.02),
    (85.0, 0.3, 0.4, -0.01, 0.03),
    (115.0, 2.0, 0.15, 0.01, 0.07),
])
def test_analytic_greeks_match_price_finite_differences(option_type, spot, time, vol, rate, yield_):
    inputs = dict(spot=spot, time_to_expiry=time, volatility=vol,
                  risk_free_rate=rate, dividend_yield=yield_)
    result = greeks(**(BASE | inputs), option_type=option_type)

    def p(**changes):
        return price(option_type, **(inputs | changes))

    h = 0.01
    center = p()
    assert result.delta == pytest.approx((p(spot=spot + h) - p(spot=spot - h)) / (2 * h), abs=2e-7)
    assert result.gamma == pytest.approx((p(spot=spot + h) - 2 * center + p(spot=spot - h)) / h**2, abs=2e-7)
    dv = 1e-4
    assert result.vega_per_vol_point == pytest.approx((p(volatility=vol + dv) - p(volatility=vol - dv)) / (2 * dv) * 0.01, abs=2e-8)
    dt = 1e-4
    assert result.theta_per_day == pytest.approx((p(time_to_expiry=time - dt) - p(time_to_expiry=time + dt)) / (2 * dt) / 365, abs=2e-9)


def test_signs_parity_and_vector_shape():
    call = greeks(**BASE, option_type="call")
    put = greeks(**BASE, option_type="put")
    assert 0 < call.delta < 1
    assert -1 < put.delta < 0
    assert call.delta - put.delta == pytest.approx(np.exp(-BASE["dividend_yield"] * BASE["time_to_expiry"]))
    assert call.gamma == pytest.approx(put.gamma)
    assert call.vega_per_vol_point == pytest.approx(put.vega_per_vol_point)
    assert call.gamma > 0 and call.vega_per_vol_point > 0
    vector = greeks(**(BASE | {"spot": np.array([85.0, 100.0, 115.0])}), option_type="call")
    assert vector.delta.shape == (3,)
    assert np.all(np.diff(vector.delta) > 0)


@pytest.mark.parametrize("time,vol", [(0.0, 0.2), (1.0, 0.0), (1e-14, 0.2), (1.0, 1e-14)])
def test_nonsmooth_boundaries_are_unavailable(time, vol):
    result = greeks(**(BASE | {"time_to_expiry": time, "volatility": vol}), option_type="put")
    assert all(value is None for value in vars(result).values())


def test_invalid_inputs_follow_pricing_validation():
    with pytest.raises(ValueError):
        greeks(**(BASE | {"spot": 0}), option_type="call")
