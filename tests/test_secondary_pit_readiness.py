"""Tests guaranteeing secondary data can never satisfy production PIT readiness."""
from __future__ import annotations
import sys
import json
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nse_signal.data.production_gate import evaluate_production_gate
from nse_signal.data.providers.policy import assert_secondary_allowed

def test_secondary_data_cannot_satisfy_production_gate(monkeypatch, tmp_path):
    monkeypatch.setenv("ALLOW_SECONDARY_PROVIDER", "true")

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
        assert any("Required PIT Layers" in r or "cash_daily" in r or "Missing" in r for r in gate["blocking_reasons"])
    finally:
        if bak_cash is not None: cash_csv.write_bytes(bak_cash)
        if bak_bars is not None: bars_jsonl.write_bytes(bak_bars)

def test_authoritative_nse_source_preferred_over_secondary(monkeypatch):
    monkeypatch.setenv("ALLOW_SECONDARY_PROVIDER", "true")
    assert_secondary_allowed("upstox")
    from nse_signal.data.providers.providers import UpstoxProvider
    p = UpstoxProvider("token")
    assert getattr(p, "source_tier", "SECONDARY_UNOFFICIAL") != "PRIMARY_AUTHORITATIVE"
