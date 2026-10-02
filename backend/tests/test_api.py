"""Application liveness and theoretical pricing API contracts."""

from fastapi.testclient import TestClient
import pytest

from app.main import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_pricing_endpoint_returns_model_intrinsic_and_time_values():
    with TestClient(app) as client:
        response = client.post("/api/pricing", json={
            "spot": 100, "strike": 100, "time_to_expiry": 1,
            "volatility": 0.2, "risk_free_rate": 0.05,
            "dividend_yield": 0.02, "option_type": "call",
        })
    assert response.status_code == 200
    body = response.json()
    assert body["model_price"] == pytest.approx(9.227006, abs=1e-6)
    assert body["intrinsic_value"] == 0
    assert body["time_value"] == pytest.approx(body["model_price"])
    assert body["time_to_expiry_years"] == 1
    assert body["model"] == "Dividend-adjusted European Black-Scholes"
    assert body["greeks"]["delta"] == pytest.approx(0.586851146)
    assert body["greeks"]["gamma"] > 0
    assert body["greeks"]["vega_per_vol_point"] > 0
    assert body["greeks"]["theta_per_day"] < 0
    assert len(body["greek_curve"]) == 61
    assert body["greek_curve"][0]["spot"] < 100 < body["greek_curve"][-1]["spot"]
    assert "ACT/365" in body["greek_units"]


def test_pricing_endpoint_rejects_invalid_units_and_option_type():
    with TestClient(app) as client:
        response = client.post("/api/pricing", json={
            "spot": 100, "strike": 100, "time_to_expiry": -1,
            "volatility": 20, "risk_free_rate": 5,
            "dividend_yield": 2, "option_type": "american-call",
        })
    assert response.status_code == 422


def test_pricing_endpoint_converts_days_with_act_365():
    with TestClient(app) as client:
        response = client.post("/api/pricing", json={
            "spot": 100, "strike": 100, "time_to_expiry": 30, "time_unit": "days",
            "volatility": 0.2, "risk_free_rate": 0.05,
            "dividend_yield": 0.02, "option_type": "put",
        })
    assert response.status_code == 200
    assert response.json()["time_to_expiry_years"] == pytest.approx(30 / 365)


def test_pricing_endpoint_expiry_marks_greeks_unavailable():
    with TestClient(app) as client:
        response = client.post("/api/pricing", json={
            "spot": 100, "strike": 100, "time_to_expiry": 0,
            "volatility": 0.2, "risk_free_rate": 0.05,
            "dividend_yield": 0.02, "option_type": "call",
        })
    assert response.status_code == 200
    assert all(value is None for value in response.json()["greeks"].values())
    assert response.json()["greek_curve"] == []
