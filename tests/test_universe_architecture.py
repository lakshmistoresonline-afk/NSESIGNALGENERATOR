"""Acceptance tests for fixed universe architecture separating BroadNSEEquityUniverse from Nifty200BenchmarkUniverse."""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nse_signal.data.universe_policy import (
    UniversePolicy, BroadNSEEquityUniverse, Nifty200BenchmarkUniverse, resolve_universe_symbols
)

def test_broad_nse_works_without_nifty200(tmp_path):
    policy = UniversePolicy(universe_mode="BROAD_NSE", nifty200_path=str(tmp_path / "nonexistent.csv"))
    sm = pd.DataFrame({
        "symbol": ["RELIANCE", "TCS"],
        "series": ["EQ", "EQ"],
        "effective_from": ["2020-01-01", "2020-01-01"],
        "effective_to": ["2025-01-01", "2025-01-01"]
    })
    symbols = resolve_universe_symbols(policy, security_master=sm, timestamp="2021-06-01")
    assert "RELIANCE" in symbols
    assert "TCS" in symbols

def test_nifty200_mode_fails_closed_without_membership(tmp_path):
    policy = UniversePolicy(universe_mode="NIFTY200", nifty200_path=str(tmp_path / "nonexistent.csv"))
    with pytest.raises((FileNotFoundError, RuntimeError, ValueError)):
        resolve_universe_symbols(policy, timestamp="2021-06-01")

def test_interval_contract_excludes_exact_effective_to():
    policy = UniversePolicy(universe_mode="BROAD_NSE")
    sm = pd.DataFrame({
        "symbol": ["TESTSYM"],
        "series": ["EQ"],
        "effective_from": ["2020-01-01"],
        "effective_to": ["2021-01-01"]
    })
    # Exactly on effective_to (2021-01-01) should be excluded due to [effective_from, effective_to) contract
    symbols = resolve_universe_symbols(policy, security_master=sm, timestamp="2021-01-01")
    assert "TESTSYM" not in symbols

def test_future_liquidity_cannot_affect_historical_eligibility():
    policy = UniversePolicy(universe_mode="BROAD_NSE", min_history_days=5)
    sm = pd.DataFrame({
        "symbol": ["FUTURESAVE"],
        "series": ["EQ"],
        "effective_from": ["2020-01-01"],
        "effective_to": ["2025-01-01"]
    })
    # Bars only exist in 2022, querying as of 2020 should have no bars <= 2020
    bars = pd.DataFrame({
        "symbol": ["FUTURESAVE"] * 10,
        "date": pd.date_range("2022-01-01", periods=10),
        "close": [100.0] * 10,
        "volume": [50000] * 10
    })
    symbols = resolve_universe_symbols(policy, security_master=sm, timestamp="2020-06-01", bars=bars)
    # Without bars <= 2020, liquidity filter returns empty or ignores future bars
    assert "FUTURESAVE" not in symbols
