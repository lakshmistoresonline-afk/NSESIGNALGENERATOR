"""Generates separate canonical published signals for live and historical views and saves them to data/processed/published_signals.json."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nse_signal.signals.contract import CanonicalSignal

def generate_sample_signals():
    out_dir = ROOT / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)

    now_str = datetime.now(timezone.utc).isoformat()

    live_items = [
        {
            "signal_id": CanonicalSignal.generate_signal_id("RELIANCE", "2024-01-02T09:15:00Z", "1D", "3.1.0", "BUY", "LIVE"),
            "symbol": "RELIANCE",
            "security_id": "NSE_EQ_RELIANCE_INE002A01018",
            "isin": "INE002A01018",
            "exchange": "NSE",
            "universe": "BroadNSEEquityUniverse",
            "signal_type": "DIRECTIONAL",
            "side": "BUY",
            "signal_time": "2024-01-02T09:15:00Z",
            "asof_time": "2024-01-02T09:15:00Z",
            "market_date": "2024-01-02",
            "timeframe": "1D",
            "price": 2520.00,
            "entry_price": 2520.00,
            "stop_price": 2465.00,
            "target_price": 2630.00,
            "probability_up": 0.68,
            "probability_down": 0.32,
            "confidence": 0.36,
            "quality_score": 0.78,
            "model_name": "nse-production",
            "model_version": "3.1.0",
            "model_hash": "sample_model_hash_v31",
            "feature_version": "v3.1",
            "feature_hash": "sample_feat_hash_v31",
            "calibration_version": "v2_time_ordered",
            "conformal_version": "v2",
            "risk_gate_status": "PASS",
            "publication_status": "PASS",
            "data_freshness": "FRESH",
            "pit_provenance_verified": True,
            "signal_only": True,
            "real_trading": False,
            "generation_mode": "LIVE",
            "live_session_id": "LIVE_SESSION_20240102"
        },
        {
            "signal_id": CanonicalSignal.generate_signal_id("TCS", "2024-01-02T09:15:00Z", "1D", "3.1.0", "BUY", "LIVE"),
            "symbol": "TCS",
            "security_id": "NSE_EQ_TCS_INE467B01029",
            "isin": "INE467B01029",
            "exchange": "NSE",
            "universe": "BroadNSEEquityUniverse",
            "signal_type": "DIRECTIONAL",
            "side": "BUY",
            "signal_time": "2024-01-02T09:15:00Z",
            "asof_time": "2024-01-02T09:15:00Z",
            "market_date": "2024-01-02",
            "timeframe": "1D",
            "price": 3850.00,
            "entry_price": 3850.00,
            "stop_price": 3770.00,
            "target_price": 4010.00,
            "probability_up": 0.72,
            "probability_down": 0.28,
            "confidence": 0.44,
            "quality_score": 0.82,
            "model_name": "nse-production",
            "model_version": "3.1.0",
            "model_hash": "sample_model_hash_v31",
            "feature_version": "v3.1",
            "feature_hash": "sample_feat_hash_v31",
            "calibration_version": "v2_time_ordered",
            "conformal_version": "v2",
            "risk_gate_status": "PASS",
            "publication_status": "PASS",
            "data_freshness": "FRESH",
            "pit_provenance_verified": True,
            "signal_only": True,
            "real_trading": False,
            "generation_mode": "LIVE",
            "live_session_id": "LIVE_SESSION_20240102"
        }
    ]

    historical_items = [
        {
            "signal_id": CanonicalSignal.generate_signal_id("HDFCBANK", "2024-01-02T09:15:00Z", "1D", "3.1.0", "SELL", "HISTORICAL"),
            "symbol": "HDFCBANK",
            "security_id": "NSE_EQ_HDFCBANK_INE040A01034",
            "isin": "INE040A01034",
            "exchange": "NSE",
            "universe": "BroadNSEEquityUniverse",
            "signal_type": "DIRECTIONAL",
            "side": "SELL",
            "signal_time": "2024-01-02T09:15:00Z",
            "asof_time": "2024-01-02T09:15:00Z",
            "market_date": "2024-01-02",
            "timeframe": "1D",
            "price": 1650.00,
            "entry_price": 1650.00,
            "stop_price": 1685.00,
            "target_price": 1580.00,
            "probability_up": 0.35,
            "probability_down": 0.65,
            "confidence": 0.30,
            "quality_score": 0.71,
            "model_name": "nse-production",
            "model_version": "3.1.0",
            "model_hash": "sample_model_hash_v31",
            "feature_version": "v3.1",
            "feature_hash": "sample_feat_hash_v31",
            "calibration_version": "v2_time_ordered",
            "conformal_version": "v2",
            "risk_gate_status": "PASS",
            "publication_status": "PASS",
            "data_freshness": "HISTORICAL",
            "pit_provenance_verified": True,
            "signal_only": True,
            "real_trading": False,
            "generation_mode": "HISTORICAL",
            "historical_asof_date": "2024-01-02",
            "historical_run_id": "HIST_RUN_20240102"
        },
        {
            "signal_id": CanonicalSignal.generate_signal_id("INFY", "2024-01-02T09:15:00Z", "1D", "3.1.0", "BUY", "HISTORICAL"),
            "symbol": "INFY",
            "security_id": "NSE_EQ_INFY_INE009A01021",
            "isin": "INE009A01021",
            "exchange": "NSE",
            "universe": "BroadNSEEquityUniverse",
            "signal_type": "DIRECTIONAL",
            "side": "BUY",
            "signal_time": "2024-01-02T09:15:00Z",
            "asof_time": "2024-01-02T09:15:00Z",
            "market_date": "2024-01-02",
            "timeframe": "1D",
            "price": 1500.00,
            "entry_price": 1500.00,
            "stop_price": 1470.00,
            "target_price": 1560.00,
            "probability_up": 0.66,
            "probability_down": 0.34,
            "confidence": 0.32,
            "quality_score": 0.76,
            "model_name": "nse-production",
            "model_version": "3.1.0",
            "model_hash": "sample_model_hash_v31",
            "feature_version": "v3.1",
            "feature_hash": "sample_feat_hash_v31",
            "calibration_version": "v2_time_ordered",
            "conformal_version": "v2",
            "risk_gate_status": "PASS",
            "publication_status": "PASS",
            "data_freshness": "HISTORICAL",
            "pit_provenance_verified": True,
            "signal_only": True,
            "real_trading": False,
            "generation_mode": "HISTORICAL",
            "historical_asof_date": "2024-01-02",
            "historical_run_id": "HIST_RUN_20240102"
        }
    ]

    all_items = live_items + historical_items
    payload = {
        "generated_at": now_str,
        "signal_only": True,
        "real_trading": False,
        "count": len(all_items),
        "live_items": live_items,
        "historical_items": historical_items,
        "items": all_items
    }

    out_path = out_dir / "published_signals.json"
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    rep_dir = ROOT / "reports"
    rep_dir.mkdir(parents=True, exist_ok=True)
    (rep_dir / "published_signals.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Generated {len(live_items)} live and {len(historical_items)} historical canonical published signals.")

if __name__ == "__main__":
    generate_sample_signals()
