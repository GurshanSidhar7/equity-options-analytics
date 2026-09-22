import numpy as np
import pytest

from app.pricing.black_scholes import black_scholes


def price(option_type: str, **overrides):
    inputs = dict(spot=100.0, strike=100.0, time_to_expiry=1.0, volatility=0.2,
                  risk_free_rate=0.05, dividend_yield=0.02, option_type=option_type)
    inputs.update(overrides)
    return black_scholes(**inputs)


def test_known_call_and_put_values():
    assert price("call").model_price == pytest.approx(9.227006, abs=1e-6)
    assert price("put").model_price == pytest.approx(6.330081, abs=1e-6)


def test_put_call_parity():
    call = price("call").model_price
    put = price("put").model_price
    expected = 100 * np.exp(-0.02) - 100 * np.exp(-0.05)
    assert call - put == pytest.approx(expected, abs=1e-12)


def test_expiry_returns_intrinsic_and_zero_time_value():
    result = price("call", spot=112, strike=100, time_to_expiry=0)
    assert result.model_price == 12
    assert result.intrinsic_value == 12
    assert result.time_value == 0

    near_expiry = price("put", spot=88, strike=100, time_to_expiry=1e-14)
    assert near_expiry.model_price == 12
    assert near_expiry.time_value == 0


def test_zero_volatility_uses_discounted_deterministic_payoff():
    result = price("call", volatility=0)
    expected = max(100 * np.exp(-0.02) - 100 * np.exp(-0.05), 0)
    assert result.model_price == pytest.approx(expected)
    assert price("call", volatility=1e-14).model_price == pytest.approx(expected)


def test_vector_inputs_broadcast_and_preserve_shape():
    result = black_scholes(np.array([90, 100, 110]), 100, 1, 0.2, 0.05, 0.02, "call")
    assert isinstance(result.model_price, np.ndarray)
    assert result.model_price.shape == (3,)
    assert np.all(np.diff(result.model_price) > 0)


def test_basic_monotonic_behavior():
    assert price("call", spot=110).model_price > price("call", spot=100).model_price
    assert price("call", strike=110).model_price < price("call", strike=100).model_price
    assert price("call", volatility=0.3).model_price > price("call", volatility=0.2).model_price
    assert price("put", spot=110).model_price < price("put", spot=100).model_price
    assert price("put", strike=110).model_price > price("put", strike=100).model_price
    assert price("put", volatility=0.3).model_price > price("put", volatility=0.2).model_price


@pytest.mark.parametrize("field,value", [("spot", 0), ("strike", -1), ("time_to_expiry", -0.1), ("volatility", -0.1)])
def test_invalid_inputs_raise(field, value):
    with pytest.raises(ValueError):
        price("call", **{field: value})
