from __future__ import annotations
import pytest
import ast
from pathlib import Path
import pandas as pd
from nse_signal.data.canonical import DataProvenance, PriceBar, InstrumentPIT
from nse_signal.data.ingest_pipeline import sha256_hash, assert_point_in_time_integrity, run_real_ingestion
from nse_signal.data.pit_builder import build_pit_dataset
from nse_signal.data.pit_validator import validate_pit_dataset
from nse_signal.data.reporting import generate_all_reports

def test_sha256_hash():
    h1 = sha256_hash(b"hello nse")
    h2 = sha256_hash(b"hello nse")
    assert h1 == h2

def test_assert_point_in_time_integrity():
    assert assert_point_in_time_integrity("2024-01-01T15:30:00Z", "RELIANCE") is True
    with pytest.raises(ValueError):
        assert_point_in_time_integrity("2099-01-01T00:00:00Z", "RELIANCE")

def test_pit_builder_and_validator(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    res = build_pit_dataset()
    assert res["status"] == "PIT_RECONSTRUCTION_PARTIAL"

    val = validate_pit_dataset()
    assert val["validation_status"] in ("PIT_VALIDATION_PARTIAL", "PIT_INVALID")
    assert len(val["checks"]) == 30

def test_validator_ast_self_audit():
    validator_path = Path("src/nse_signal/data/pit_validator.py")
    tree = ast.parse(validator_path.read_text(encoding="utf-8"))
    # Verify that add_check calls are present and dynamic
    add_check_calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "add_check"]
    assert len(add_check_calls) >= 28

def test_dynamic_reports_generation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    r1, r2, r3, r4, r5 = generate_all_reports()
    assert r1.exists()
    assert r2.exists()
    assert r3.exists()
    assert r4.exists()
    assert r5.exists()
    assert "Data Source Availability Report" in r1.read_text(encoding="utf-8")
    assert "PIT Coverage Report" in r2.read_text(encoding="utf-8")
    assert "V31 Data Execution Report" in r3.read_text(encoding="utf-8")
