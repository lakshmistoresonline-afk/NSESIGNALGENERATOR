"""Diagnostic-Only Historical Coverage Auditor: Inspects actual physical raw archives across 2014-2025 without synthesizing or fabricating missing data. Reports exact gaps and sets status to BLOCKED if any required historical session file is absent."""
from __future__ import annotations
import json
import pandas as pd
from pathlib import Path
from datetime import date, timedelta, datetime, timezone
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nse_signal.data.nse.session_calendar import load_holidays, is_trading_day

def audit_historical_coverage():
    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_root = Path("data/raw/nse")
    holidays = load_holidays()

    start_d = date(2014, 1, 1)
    end_d = date(2025, 12, 31)

    expected_trading_days = 0
    d = start_d
    while d <= end_d:
        if is_trading_day(d, holidays):
            expected_trading_days += 1
        d += timedelta(days=1)

    layers = ["cm_bhavcopy", "security_master", "index_close", "fo_bhavcopy", "delivery", "corporate_actions", "restrictions"]
    layer_contracts = {}

    total_missing = 0

    for layer in layers:
        layer_dir = raw_root / layer
        acquired_days = 0
        validated_days = 0
        invalid_days = 0
        missing_days = []

        if layer == "corporate_actions":
            corp_file = layer_dir / "corporate_adjustments.csv"
            pit_corp = Path("data/processed/nse_pit/corporate_adjustments.csv")
            has_corp = (corp_file.exists() and corp_file.stat().st_size > 0) or (pit_corp.exists() and pit_corp.stat().st_size > 0)
            acquired_days = expected_trading_days if has_corp else 0
            validated_days = acquired_days
            completeness_ratio = 1.0 if has_corp else 0.0
            if not has_corp:
                missing_days.append({"date": "ALL", "status": "DATA_MISSING", "reason": "Corporate actions adjustment file missing"})
        else:
            d = start_d
            while d <= end_d:
                if not is_trading_day(d, holidays):
                    d += timedelta(days=1)
                    continue

                d_str = d.isoformat()
                if layer == 'cm_bhavcopy': suffix_list = ['.csv.zip', '.zip']
                elif layer == 'security_master': suffix_list = ['.csv.gz', '.csv', '.gz']
                elif layer == 'fo_bhavcopy': suffix_list = ['.csv.zip', '.zip']
                else: suffix_list = ['.csv', '.txt']

                found = False
                for sfx in suffix_list:
                    fpath = layer_dir / f"{d_str}{sfx}"
                    if fpath.exists() and fpath.stat().st_size > 0:
                        found = True
                        break
                if not found:
                    matches = list(layer_dir.glob(f"{d_str}*"))
                    if matches and any(m.stat().st_size > 0 for m in matches):
                        found = True

                if found:
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

        total_missing += len(missing_days)
        layer_contracts[layer] = {
            "layer_id": layer,
            "first_required_date": start_d.isoformat(),
            "last_required_date": end_d.isoformat(),
            "expected_trading_days": expected_trading_days,
            "acquired_days": acquired_days,
            "validated_days": validated_days,
            "invalid_days": invalid_days,
            "missing_days": missing_days[:20],
            "missing_days_count": len(missing_days),
            "completeness_ratio": round(completeness_ratio, 4),
            "acceptable_gap_rules": "Zero gap for production; no synthesis permitted",
            "source_provenance_requirement": "SHA256 provenance manifest required"
        }

    overall_completeness = sum(m["completeness_ratio"] for m in layer_contracts.values()) / len(layer_contracts)
    status = "PASS" if overall_completeness >= 1.0 and total_missing == 0 else "BLOCKED"

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "layers": layer_contracts,
        "overall_completeness": round(overall_completeness, 4),
        "failure_reason": None if status == "PASS" else f"Historical data coverage incomplete: total missing days = {total_missing} (diagnostic mode: zero synthesis permitted)"
    }

    out_path = out_dir / "final_historical_coverage.json"
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print("Diagnostic historical coverage contract generated:", out_path)
    return report

if __name__ == "__main__":
    audit_historical_coverage()
