"""Unit tests for HistoricalSignalEngine verifying point-in-time constraints and zero future data leakage."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nse_signal.signals.historical_engine import HistoricalSignalEngine

def test_historical_signal_generation_causality():
    engine = HistoricalSignalEngine()
    # Query a historical date range
    signals = engine.generate_historical_signals("2024-01-02", "2024-01-03", universe="BroadNSEEquityUniverse", timeframe="1D")
    for sig in signals:
        assert sig.generation_mode == "HISTORICAL"
        assert sig.historical_asof_date is not None
        assert sig.historical_run_id is not None
        assert sig.real_trading is False
        assert sig.signal_only is True
        # Verify no future leakage: asof_time <= signal_time
        assert sig.asof_time <= sig.signal_time
