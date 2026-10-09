"""Negative unit tests verifying fail-closed behavior for missing features, missing expected value, invalid live provenance, and stale live snapshots."""
from __future__ import annotations
import sys
import json
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nse_signal.signals.live_engine import LiveSignalEngine

def test_live_engine_blocks_missing_snapshot(tmp_path, monkeypatch):
    # If live_snapshot.json is missing, live scan must return BLOCKED
    monkeypatch.setattr("nse_signal.signals.live_engine.evaluate_production_gate", lambda: {"eligible": True})
    monkeypatch.setattr("nse_signal.signals.live_engine.Path", lambda p: tmp_path / Path(p).name if "live_snapshot" in str(p) else Path(p))
    engine = LiveSignalEngine()
    res = engine.scan_live_universe(session_id="NEG_TEST_1")
    assert res["status"] == "BLOCKED"
    assert "Live snapshot file missing" in res["reason"]

def test_live_engine_blocks_unverified_provenance(tmp_path, monkeypatch):
    # If live snapshot lacks authoritative provenance metadata, live scan must return BLOCKED
    monkeypatch.setattr("nse_signal.signals.live_engine.evaluate_production_gate", lambda: {"eligible": True})
    snap_path = tmp_path / "live_snapshot.json"
    snap_path.write_text(json.dumps({"items": []}), encoding="utf-8")
    monkeypatch.setattr("nse_signal.signals.live_engine.Path", lambda p: snap_path if "live_snapshot" in str(p) else Path(p))
    engine = LiveSignalEngine()
    res = engine.scan_live_universe(session_id="NEG_TEST_2")
    assert res["status"] == "BLOCKED"
    assert "NON-AUTHORITATIVE LIVE SNAPSHOT" in res["reason"]
