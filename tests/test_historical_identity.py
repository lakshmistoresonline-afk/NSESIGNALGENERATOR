"""Adversarial tests for historical security identity layer."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nse_signal.data.nse.security_identity import (
    identity_asof, resolve_historical_symbol, validate_identity_intervals
)

def test_unknown_identity_returns_unknown():
    res = identity_asof("NONEXISTENT_SYM_XYZ", "2020-01-02")
    assert res["status"] == "UNKNOWN"

def test_future_identity_cannot_resolve_backward():
    # If symbol only existed later, querying earlier should return UNKNOWN
    res = identity_asof("LATER_LISTED_SYM", "2010-01-02")
    assert res["status"] == "UNKNOWN"

def test_identity_interval_validation():
    valid, errors = validate_identity_intervals()
    assert isinstance(valid, bool)
    assert isinstance(errors, list)
