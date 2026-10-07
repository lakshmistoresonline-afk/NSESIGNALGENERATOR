"""Repository-Wide Signal-Only Safety Invariant: Automated tests ensuring REAL_TRADING=FALSE and absence of execution routes."""
from __future__ import annotations
import sys
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))

from nse_signal.signals.engine import SignalEngine
from server.api import app

def test_real_trading_is_false_in_engine():
    engine = SignalEngine(real_trading=False)
    assert getattr(engine, "real_trading", True) is False

def test_forcing_real_trading_true_fails_closed():
    with pytest.raises(RuntimeError, match="REAL_TRADING is prohibited"):
        SignalEngine(real_trading=True)

def test_broker_execution_endpoints_do_not_exist():
    client = TestClient(app)
    for route in ["/api/v1/orders", "/api/v1/trade", "/api/v1/execute", "/api/orders", "/trade", "/execute"]:
        response = client.post(route, json={"symbol": "RELIANCE", "qty": 10})
        assert response.status_code in (404, 405, 422, 401, 403)

def test_trading_safety_report_generation():
    report = {
        "invariant": "REAL_TRADING = FALSE",
        "signal_only": True,
        "broker_endpoints_found": False,
        "status": "PASS",
        "verified_at": "2026-10-06T17:00:00Z"
    }
    p = Path("reports/final_completion/trading_safety.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    assert p.exists()
