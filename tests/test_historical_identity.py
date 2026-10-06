"""Adversarial tests for historical security identity layer ensuring fail-closed UNKNOWN/AMBIGUOUS mapping."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nse_signal.data.nse.security_identity import (
    identity_asof, resolve_historical_symbol, validate_identity_intervals, SecurityIdentityEngine
)

def test_unknown_identity_returns_unknown():
    res = identity_asof("NONEXISTENT_SYM_XYZ", "2020-01-02")
    assert res["status"] == "UNKNOWN"
    assert resolve_historical_symbol("NONEXISTENT_SYM_XYZ", "2020-01-02") == "UNKNOWN"

def test_future_identity_cannot_resolve_backward():
    # Querying a symbol before its effective_from must return UNKNOWN
    engine = SecurityIdentityEngine()
    engine.intervals = [{
        "instrument_id": "NSE_EQ_TEST_INE000",
        "symbol": "TEST",
        "isin": "INE000",
        "series": "EQ",
        "effective_from": "2022-01-01",
        "effective_to": "2025-01-01"
    }]
    engine._built = True
    res = engine.identity_asof("TEST", "2020-01-02")
    assert res["status"] == "UNKNOWN"

def test_terminated_symbol_after_termination_date():
    engine = SecurityIdentityEngine()
    engine.intervals = [{
        "instrument_id": "NSE_EQ_OLD_INE999",
        "symbol": "OLD",
        "isin": "INE999",
        "series": "EQ",
        "effective_from": "2015-01-01",
        "effective_to": "2020-01-01"
    }]
    engine._built = True
    # Querying after effective_to (2021-01-01) with half-open [effective_from, effective_to) must return UNKNOWN
    res = engine.identity_asof("OLD", "2021-01-01")
    assert res["status"] == "UNKNOWN"

def test_identity_interval_validation():
    valid, errors = validate_identity_intervals()
    assert isinstance(valid, bool)
    assert isinstance(errors, list)
