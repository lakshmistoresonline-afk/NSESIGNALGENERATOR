import json
import pytest
from fastapi.testclient import TestClient
import server.api as api

client = TestClient(api.app)
AUTH_HEADERS = {"Authorization": "Bearer dev-analyst-token"}

def test_v1_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["signal_only"] is True
    assert data["real_trading"] is False

def test_no_published_signal_file(tmp_path, monkeypatch):
    sig_path = api.ROOT / "data" / "processed" / "published_signals.json"
    orig_text = sig_path.read_text(encoding="utf-8") if sig_path.exists() else None
    if sig_path.exists():
        sig_path.unlink()
    try:
        response = client.get("/api/v1/signals", headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["items"] == []
    finally:
        if orig_text is not None:
            sig_path.parent.mkdir(parents=True, exist_ok=True)
            sig_path.write_text(orig_text, encoding="utf-8")

def test_unknown_symbol_returns_no_signal(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "dashboard_overview", lambda: {"pit": {"ready": True}})
    monkeypatch.setattr("nse_signal.data.nse.data_governance.data_governance_status", lambda p: {"production_eligible": True})

    sig_path = api.ROOT / "data" / "processed" / "published_signals.json"
    orig_text = sig_path.read_text(encoding="utf-8") if sig_path.exists() else None
    sig_path.parent.mkdir(parents=True, exist_ok=True)
    sig_path.write_text(json.dumps([]), encoding="utf-8")
    try:
        response = client.get("/api/v1/signals/UNKNOWN_SYM", headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["signal"] == "NO_SIGNAL"
        assert data["publication_status"] == "NOT_AVAILABLE"
        assert data["reason"] == "SYMBOL_NOT_PUBLISHED"
        assert data["confidence"] is None
        assert data["price"] is None
    finally:
        if orig_text is not None:
            sig_path.write_text(orig_text, encoding="utf-8")
        else:
            sig_path.unlink(missing_ok=True)

def test_missing_confidence_and_price_are_null(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "dashboard_overview", lambda: {"pit": {"ready": True}})
    monkeypatch.setattr("nse_signal.data.nse.data_governance.data_governance_status", lambda p: {"production_eligible": True})

    sig_path = api.ROOT / "data" / "processed" / "published_signals.json"
    orig_text = sig_path.read_text(encoding="utf-8") if sig_path.exists() else None
    sig_path.parent.mkdir(parents=True, exist_ok=True)
    sig_path.write_text(json.dumps([{
        "symbol": "TESTSYM",
        "exchange": "NSE",
        "signal": "NO_SIGNAL",
        "confidence": None,
        "price": None,
        "signal_time": None,
        "regime": "UNKNOWN",
        "publication_status": "ABSTAINED",
        "conformal_status": None,
        "model_dispersion": None,
        "signal_only": True,
        "real_trading": False,
        "reason": "TEST_ABS"
    }]), encoding="utf-8")
    try:
        response = client.get("/api/v1/signals/TESTSYM", headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["confidence"] is None
        assert data["price"] is None
        assert data["signal"] == "NO_SIGNAL"
    finally:
        if orig_text is not None:
            sig_path.write_text(orig_text, encoding="utf-8")
        else:
            sig_path.unlink(missing_ok=True)

def test_no_synthetic_fallback_for_fabricated_buy(monkeypatch):
    monkeypatch.setattr(api, "dashboard_overview", lambda: {"pit": {"ready": True}})
    monkeypatch.setattr("nse_signal.data.nse.data_governance.data_governance_status", lambda p: {"production_eligible": True})

    response = client.get("/api/v1/signals/FAKEBUYSYMBOL", headers=AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["signal"] == "NO_SIGNAL"
    assert data["signal"] != "BUY"
    assert data["signal"] != "SELL"

def test_details_endpoint_does_not_claim_unverified_verification(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "dashboard_overview", lambda: {"pit": {"ready": True}})
    monkeypatch.setattr("nse_signal.data.nse.data_governance.data_governance_status", lambda p: {"production_eligible": True})

    sig_path = api.ROOT / "data" / "processed" / "published_signals.json"
    orig_text = sig_path.read_text(encoding="utf-8") if sig_path.exists() else None
    sig_path.parent.mkdir(parents=True, exist_ok=True)
    sig_path.write_text(json.dumps([{
        "symbol": "UNVERIFIEDSYM",
        "exchange": "NSE",
        "signal": "NO_SIGNAL",
        "confidence": None,
        "price": None,
        "signal_time": None,
        "regime": "UNKNOWN",
        "publication_status": "ABSTAINED",
        "pit_provenance_verified": False,
        "conformal_status": "UNVERIFIED",
        "signal_only": True,
        "real_trading": False
    }]), encoding="utf-8")
    try:
        response = client.get("/api/v1/signal/UNVERIFIEDSYM/details", headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["pit_provenance_verified"] is False
        assert data["conformal_calibration_status"] == "UNVERIFIED"
        assert data["publication_gate"] != "PASSED"
    finally:
        if orig_text is not None:
            sig_path.write_text(orig_text, encoding="utf-8")
        else:
            sig_path.unlink(missing_ok=True)

def test_no_broker_execution_endpoints():
    for path in ["/api/v1/order", "/api/v1/execute", "/api/v1/trade", "/api/v1/broker/order", "/order", "/execute", "/trade"]:
        resp = client.post(path, json={"symbol": "RELIANCE", "qty": 10}, headers=AUTH_HEADERS)
        assert resp.status_code == 404
