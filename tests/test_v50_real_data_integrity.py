"""Adversarial regression tests for V50 real-data integrity and anti-fabrication constraints."""
from __future__ import annotations
import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from server.api import app

def test_blocked_gate_returns_zero_signals(monkeypatch):
    monkeypatch.setenv("NSE_TEST_MODE", "true")
    # Force production gate to be blocked
    monkeypatch.setattr("nse_signal.data.production_gate.evaluate_production_gate", lambda root_dir=".": {"eligible": False, "status": "BLOCKED", "blocking_reasons": ["Test explicit blocker"]})

    client = TestClient(app)
    res = client.get("/api/dashboard/signals")
    assert res.status_code == 200
    data = res.json()
    assert data["publication_gate"] == "BLOCKED"
    assert len(data.get("live_items", [])) == 0
    assert len(data.get("historical_items", [])) == 0
    assert len(data.get("items", [])) == 0

def test_synthetic_research_disabled_by_default(monkeypatch):
    monkeypatch.delenv("ALLOW_SYNTHETIC_RESEARCH", raising=False)
    client = TestClient(app)
    res = client.post("/api/research", json={"symbol": "RELIANCE", "rows": 300})
    # Should be forbidden or blocked in production by default
    assert res.status_code in (403, 500)

def test_missing_safety_fields_rejected():
    from nse_signal.signals.contract import CanonicalSignal
    sig = CanonicalSignal(
        signal_id="test_id",
        symbol="RELIANCE",
        security_id="NSE_EQ_RELIANCE",
        isin="INE002A01018",
        exchange="NSE",
        universe="BroadNSEEquityUniverse",
        signal_type="DIRECTIONAL",
        side="BUY",
        signal_time="2024-01-02T09:15:00Z",
        asof_time="2024-01-02T09:15:00Z",
        market_date="2024-01-02",
        timeframe="1D",
        price=2500.0,
        entry_price=2500.0,
        stop_price=2450.0,
        target_price=2600.0,
        probability_up=0.7,
        probability_down=0.3,
        confidence=0.4,
        quality_score=0.8,
        model_name="test",
        model_version="1.0",
        model_hash="abc",
        feature_version="v1",
        feature_hash="abc",
        calibration_version="v2",
        conformal_version="1",
        risk_gate_status="PASS",
        publication_status="PASS",
        data_freshness="FRESH",
        pit_provenance_verified=True,
        signal_only=True,
        real_trading=True  # VIOLATION!
    )
    valid, errs = sig.validate()
    assert valid is False
    assert any("REAL_TRADING" in e or "real_trading" in e for e in errs)
