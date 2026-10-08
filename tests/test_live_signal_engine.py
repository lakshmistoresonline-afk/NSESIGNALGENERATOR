"""Unit tests for LiveSignalEngine verifying BroadNSEEquityUniverse scanning, signal generation, and signal-only invariants."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nse_signal.signals.live_engine import LiveSignalEngine

def test_live_signal_scan():
    engine = LiveSignalEngine()
    res = engine.scan_live_universe(session_id="TEST_SESSION_1")
    assert "live_session_id" in res
    assert res["status"] in ("COMPLETED", "BLOCKED", "PARTIAL")
    assert "signal_count" in res
    for sig in res.get("signals", []):
        assert sig["signal_only"] is True
        assert sig["real_trading"] is False
        assert sig["generation_mode"] == "LIVE"
        assert sig["live_session_id"] == "TEST_SESSION_1"
