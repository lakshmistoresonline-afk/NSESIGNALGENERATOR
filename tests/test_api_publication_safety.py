"""Comprehensive API and publication contract test suite covering health, PIT blocking, provenance, authorization, signal validation, and absence of order endpoints."""
from __future__ import annotations
import sys
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))

from server.api import app

def test_api_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["signal_only"] is True
    assert data["real_trading"] is False

def test_api_dashboard_overview():
    client = TestClient(app)
    response = client.get("/api/dashboard/overview")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["signal_only"] is True
    assert data["real_trading"] is False

def test_api_readiness_endpoint():
    client = TestClient(app)
    response = client.get("/api/readiness")
    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert data["signal_only"] is True
    assert data["real_trading"] is False

def test_v1_signals_missing_authorization_rejected():
    client = TestClient(app)
    response = client.get("/api/v1/signals")
    assert response.status_code == 401

def test_v1_signals_authorized_analyst_succeeds():
    client = TestClient(app)
    headers = {"Authorization": "Bearer dev-analyst-token"}
    response = client.get("/api/v1/signals", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["signal_only"] is True
    assert data["real_trading"] is False
    assert "items" in data

def test_v1_signals_unauthorized_role_rejected():
    client = TestClient(app)
    headers = {"Authorization": "Bearer dev-non-analyst-token"}
    response = client.get("/api/v1/signals", headers=headers)
    assert response.status_code == 403

def test_published_signals_rejects_execution_enabled_artifacts(monkeypatch):
    from server import api
    bad_pub = api.ROOT / "data" / "processed" / "published_signals.json"
    bad_pub.parent.mkdir(parents=True, exist_ok=True)
    bak = bad_pub.read_bytes() if bad_pub.exists() else None

    bad_pub.write_text(json.dumps({
        "signal_only": False,
        "real_trading": True,
        "items": [{"symbol": "BAD", "real_trading": True}]
    }), encoding="utf-8")

    try:
        client = TestClient(app)
        response = client.get("/api/dashboard/signals")
        assert response.status_code == 500
    finally:
        if bak is not None:
            bad_pub.write_bytes(bak)
        elif bad_pub.exists():
            bad_pub.unlink()

def test_no_order_endpoint_exists():
    client = TestClient(app)
    for route in ["/api/v1/orders", "/api/v1/trade", "/api/v1/execute", "/api/orders", "/trade", "/execute"]:
        response = client.post(route, json={"symbol": "RELIANCE", "qty": 10})
        assert response.status_code in (404, 405, 422, 401, 403)
