"""Unit tests for CanonicalSignal contract, deterministic ID generation, validation, and serialization."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nse_signal.signals.contract import CanonicalSignal

def test_canonical_signal_validation_and_serialization():
    sig_id = CanonicalSignal.generate_signal_id("RELIANCE", "2024-01-02T18:00:00Z", "1D", "v3.1", "BUY", "LIVE")
    sig = CanonicalSignal(
        signal_id=sig_id,
        symbol="RELIANCE",
        security_id="NSE_EQ_RELIANCE_INE002A01018",
        isin="INE002A01018",
        exchange="NSE",
        universe="BroadNSEEquityUniverse",
        signal_type="DIRECTIONAL",
        side="BUY",
        signal_time="2024-01-02T18:00:00Z",
        asof_time="2024-01-02T18:00:00Z",
        market_date="2024-01-02",
        timeframe="1D",
        price=2500.0,
        entry_price=2500.0,
        stop_price=2450.0,
        target_price=2600.0,
        probability_up=0.65,
        probability_down=0.35,
        confidence=0.30,
        quality_score=0.75,
        model_name="ensemble",
        model_version="3.1.0",
        model_hash="abc123hash",
        feature_version="v3.1",
        feature_hash="feat123hash",
        calibration_version="v2",
        conformal_version="v2",
        risk_gate_status="PASS",
        publication_status="PASS",
        data_freshness="FRESH",
        pit_provenance_verified=True,
        signal_only=True,
        real_trading=False,
        generation_mode="LIVE",
        live_session_id="SESSION_20240102"
    )

    valid, errs = sig.validate()
    assert valid is True
    assert errs == []

    d = sig.to_dict()
    sig2 = CanonicalSignal.from_dict(d)
    assert sig2 == sig
