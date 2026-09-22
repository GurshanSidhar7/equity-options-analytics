"""Scaffolding smoke test only; no quantitative features exist yet."""

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
