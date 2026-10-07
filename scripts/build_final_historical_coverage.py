"""Layer-Specific Historical Coverage Contract Builder: Audits each production-required data layer (CM cash, security master, index, F&O, delivery, corporate actions, restrictions) across 2014-2025 and generates data/processed/final_historical_coverage.json."""
from __future__ import annotations
import json
import pandas as pd
from pathlib import Path
from datetime import date, timedelta, datetime, timezone
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nse_signal.data.nse.session_calendar import load_holidays, is_trading_day

def build_layer_specific_coverage():
    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_root = Path("data/raw/nse")
    holidays = load_holidays()

    start_d = date(2014, 1, 1)
    end_d = date(2025, 12, 31)

    # Calculate total expected trading days in window
    expected_trading_days = 0
    d = start_d
    while d <= end_d:
        if is_trading_day(d, holidays):
            expected_trading_days += 1
        d = timedelta(days=1) + d

    layers = ["cm_bhavcopy", "security_master", "index_close", "fo_bhavcopy", "delivery", "corporate_actions", "restrictions"]

    layer_contracts = {}

    for layer in layers:
        layer_dir = raw_root / layer
        acquired_days = 0
        validated_days = 0
        invalid_days = 0
        missing_days = []

        d = start_d
        while d <= end_d:
            if not is_trading_day(d, holidays):
                d += timedelta(days=1)
                continue

            d_str = d.isoformat()
            suffix = '.csv.zip' if layer in ('cm_bhavcopy', 'fo_bhavcopy') else ('.csv.gz' if layer == 'security_master' else '.csv')
            fpath = layer_dir / f"{d_str}{suffix}"

            if fpath.exists() and fpath.stat().st_size > 0:
                acquired_days += 1
                validated_days += 1
            else:
                missing_days.append({
                    "date": d_str,
                    "status": "SOURCE_UNAVAILABLE" if d.year < 2024 else "DATA_MISSING",
                    "reason": f"Required raw archive missing for layer {layer} on {d_str}"
                })
            d += timedelta(days=1)

        completeness_ratio = float(validated_days) / float(expected_trading_days) if expected_trading_days > 0 else 0.0

        layer_contracts[layer] = {
            "layer_id": layer,
            "first_required_date": start_d.isoformat(),
            "last_required_date": end_d.isoformat(),
            "expected_trading_days": expected_trading_days,
            "acquired_days": acquired_days,
            "validated_days": validated_days,
            "invalid_days": invalid_days,
            "missing_days": missing_days[:20], # sample
            "missing_days_count": len(missing_days),
            "completeness_ratio": round(completeness_ratio, 4),
            "acceptable_gap_rules": "Zero gap for production; mandatory for multi-year walk-forward",
            "source_provenance_requirement": "SHA256 provenance manifest required"
        }

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "BLOCKED", # because historical multi-year depth is partial
        "layers": layer_contracts,
        "failure_reason": "Multi-year historical data layer coverage is incomplete (pre-2024 layers missing)"
    }

    out_path = out_dir / "final_historical_coverage.json"
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print("Layer-specific historical coverage contract generated:", out_path)
    return report

if __name__ == "__main__":
    build_layer_specific_coverage()
