"""Rigorous proof that secondary providers can never satisfy production PIT readiness."""
from __future__ import annotations
import sys
import json
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nse_signal.data.production_gate import evaluate_production_gate
from nse_signal.data.providers.base import ProviderResult, iso_now
from nse_signal.data.providers.policy import assert_secondary_allowed

def test_provider_result_carries_provenance_fields():
    res = ProviderResult(
        provider="upstox",
        symbol="RELIANCE",
        dataframe=None,
        retrieved_at=iso_now(),
        source_url="https://api.upstox.com",
        authority_class="SECONDARY_UNOFFICIAL",
        as_of_timestamp=iso_now()
    )
    assert res.provider == "upstox"
    assert res.authority_class == "SECONDARY_UNOFFICIAL"
    assert res.pit_authoritative is False
    assert res.as_of_timestamp is not None

def test_nse_unavailable_plus_secondary_available_remains_blocked(monkeypatch):
    monkeypatch.setenv("ALLOW_SECONDARY_PROVIDER", "true")
    # Simulate missing NSE PIT data
    pit_root = Path("data/processed/nse_pit")
    cash_csv = pit_root / "cash_daily.csv"
    bars_jsonl = Path("data/processed/pit/canonical_price_bars.jsonl")

    bak_cash = cash_csv.read_bytes() if cash_csv.exists() else None
    bak_bars = bars_jsonl.read_bytes() if bars_jsonl.exists() else None

    if cash_csv.exists(): cash_csv.unlink()
    if bars_jsonl.exists(): bars_jsonl.unlink()

    try:
        gate = evaluate_production_gate()
        assert gate["status"] == "BLOCKED"
        # Secondary availability must not satisfy gate
        assert gate["eligible"] is False
    finally:
        if bak_cash is not None: cash_csv.write_bytes(bak_cash)
        if bak_bars is not None: bars_jsonl.write_bytes(bak_bars)

def test_secondary_failure_does_not_silently_fallback(monkeypatch):
    monkeypatch.setenv("ALLOW_SECONDARY_PROVIDER", "true")
    from nse_signal.data.providers.fallback import SecondaryFallback
    fallback = SecondaryFallback(order=["invalid_provider"])
    with pytest.raises(Exception):
        fallback.historical("RELIANCE", "2025-01-01", "2025-01-03")
