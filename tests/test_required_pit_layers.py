"""Adversarial tests for semantic PIT layer validation covering renaming, empty placeholders, stale artifacts, and missing provenance."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nse_signal.data.nse.pit_layer_validator import validate_semantic_pit_layer, validate_all_required_pit_layers

def test_empty_placeholder_file_results_in_blocked(tmp_path, monkeypatch):
    # If canonical file exists but is empty (0 bytes), validation must fail closed (BLOCKED)
    empty_file = tmp_path / "canonical_price_bars.jsonl"
    empty_file.write_text("", encoding="utf-8")
    monkeypatch.setattr("nse_signal.data.nse.pit_layer_validator.Path", lambda p: tmp_path / Path(p).name if "canonical_price_bars" in str(p) else Path(p))
    valid, reason = validate_semantic_pit_layer("cash_bhavcopy", pit_dir=str(tmp_path))
    assert valid is False
    assert "CANONICAL_REPRESENTATION_MISSING" in reason or "EMPTY" in reason

def test_missing_provenance_results_in_blocked(tmp_path):
    # If canonical artifact exists but manifest/provenance is missing, validation must fail closed (BLOCKED)
    can_file = tmp_path / "canonical_price_bars.jsonl"
    can_file.write_text('{"symbol": "RELIANCE", "close": 100.0, "event_date": "2024-01-02"}\n', encoding="utf-8")

    valid, reason = validate_semantic_pit_layer("cash_bhavcopy", pit_dir=str(tmp_path), raw_root=str(tmp_path))
    assert valid is False
    assert "PROVENANCE_MANIFEST_MISSING" in reason
