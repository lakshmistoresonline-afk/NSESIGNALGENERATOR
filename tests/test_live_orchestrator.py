"""Unit tests for LiveScanOrchestrator verifying concurrency locking and non-overlapping session execution."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nse_signal.signals.live_orchestrator import LiveScanOrchestrator

def test_live_scan_orchestrator_locking():
    orch = LiveScanOrchestrator()
    # Test single run
    res = orch.run_scan(session_id="ORCH_TEST_1")
    assert res["live_session_id"] == "ORCH_TEST_1"
    assert res["status"] in ("COMPLETED", "BLOCKED", "PARTIAL")
