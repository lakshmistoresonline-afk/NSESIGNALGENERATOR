"""Tests for genuine historical Nifty 200 PIT membership and Broad NSE universe independence."""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nse_signal.data.universe_policy import UniversePolicy, Nifty200BenchmarkUniverse, BroadNSEEquityUniverse
from nse_signal.data.nse.membership import load_membership, membership_asof

def test_nifty200_membership_loading():
    m = load_membership("data/reference/nifty200_membership.csv")
    assert not m.empty
    assert "symbol" in m.columns
    assert "effective_from" in m.columns
    assert "effective_to" in m.columns

def test_nifty200_asof_query():
    m = load_membership("data/reference/nifty200_membership.csv")
    active = membership_asof(m, "2020-06-01")
    assert "RELIANCE" in active.symbol.values

def test_nifty200_benchmark_universe_fails_closed_on_unknown_date():
    policy = UniversePolicy(universe_mode="NIFTY200")
    engine = Nifty200BenchmarkUniverse(policy)
    # Querying a date prior to effective_from (e.g. 2010-01-01) should fail closed
    with pytest.raises(RuntimeError):
        engine.get_eligible_symbols("2010-01-01")

def test_broad_nse_equity_universe_independent():
    policy = UniversePolicy(universe_mode="BROAD_NSE")
    engine = BroadNSEEquityUniverse(policy)
    sm = pd.DataFrame({
        "symbol": ["ANYSTOCK"],
        "series": ["EQ"],
        "effective_from": ["2015-01-01"],
        "effective_to": ["2025-01-01"]
    })
    symbols = engine.get_eligible_symbols(sm, "2020-01-01")
    assert "ANYSTOCK" in symbols
