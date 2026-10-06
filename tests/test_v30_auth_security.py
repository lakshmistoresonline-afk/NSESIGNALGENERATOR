import os
import json
import pytest
from fastapi.testclient import TestClient
import server.api as api

os.environ["NSE_TEST_MODE"] = "true"
client = TestClient(api.app)

def test_protected_endpoint_missing_token():
    response = client.get("/api/v1/signals")
    assert response.status_code == 401

def test_protected_endpoint_malformed_token():
    response = client.get("/api/v1/signals", headers={"Authorization": "Bearer invalid.malformed.token"})
    assert response.status_code == 401

def test_protected_endpoint_non_analyst_token():
    response = client.get("/api/v1/signals", headers={"Authorization": "Bearer dev-non-analyst-token"})
    assert response.status_code == 403

def test_protected_endpoint_valid_token(monkeypatch):
    monkeypatch.setattr(api, "dashboard_overview", lambda: {"pit": {"ready": True}})
    monkeypatch.setattr("nse_signal.data.nse.data_governance.data_governance_status", lambda p: {"production_eligible": True})

    response = client.get("/api/v1/signals", headers={"Authorization": "Bearer dev-analyst-token"})
    assert response.status_code == 200
    data = response.json()
    assert data["signal_only"] is True

def test_unknown_symbol_authenticated(monkeypatch):
    monkeypatch.setattr(api, "dashboard_overview", lambda: {"pit": {"ready": True}})
    monkeypatch.setattr("nse_signal.data.nse.data_governance.data_governance_status", lambda p: {"production_eligible": True})

    response = client.get("/api/v1/signals/UNKNOWN_AUTH_SYM", headers={"Authorization": "Bearer dev-analyst-token"})
    assert response.status_code == 200
    data = response.json()
    assert data["signal"] == "NO_SIGNAL"
    assert data["reason"] == "SYMBOL_NOT_PUBLISHED"

def test_all_protected_v1_endpoints(monkeypatch):
    monkeypatch.setattr(api, "dashboard_overview", lambda: {"pit": {"ready": True}})
    monkeypatch.setattr("nse_signal.data.nse.data_governance.data_governance_status", lambda p: {"production_eligible": True})

    headers = {"Authorization": "Bearer dev-analyst-token"}
    assert client.get("/api/v1/market-status", headers=headers).status_code == 200
    assert client.get("/api/v1/universe", headers=headers).status_code == 200
    assert client.get("/api/v1/signal/RELIANCE/details", headers=headers).status_code == 200

def test_dev_token_rejected_when_test_mode_disabled():
    os.environ["NSE_TEST_MODE"] = "false"
    try:
        response = client.get("/api/v1/signals", headers={"Authorization": "Bearer dev-analyst-token"})
        assert response.status_code == 401
    finally:
        os.environ["NSE_TEST_MODE"] = "true"
