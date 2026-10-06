"""Complete authoritative NSE historical data acquisition for Q1 2024 with explicit gap classification."""
from __future__ import annotations
import os
import json
import sys
from datetime import date, timedelta, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nse_signal.data.nse.archives import download_artifact, append_manifest
from nse_signal.data.nse.session_calendar import load_holidays, is_trading_day

def complete_acquisition(start_date="2024-01-01", end_date="2024-03-31"):
    raw_root = "data/raw/nse"
    manifest_path = Path(raw_root) / "manifest.jsonl"
    holidays = load_holidays()

    start_d = date.fromisoformat(start_date)
    end_d = date.fromisoformat(end_date)

    layers = ["cm_bhavcopy", "security_master"]

    audit_results = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "acquired": 0,
        "failed": 0,
        "failures": []
    }

    d = start_d
    while d <= end_d:
        if not is_trading_day(d, holidays):
            d += timedelta(days=1)
            continue

        for layer in layers:
            suffix = '.csv.zip' if layer == 'cm_bhavcopy' else '.csv.gz'
            expected_path = Path(raw_root) / layer / f"{d:%Y-%m-%d}{suffix}"
            if expected_path.exists() and expected_path.stat().st_size > 0:
                audit_results["acquired"] += 1
                continue

            try:
                artifact = download_artifact(layer, d, raw_root)
                append_manifest(artifact, str(manifest_path))
                audit_results["acquired"] += 1
            except Exception as exc:
                audit_results["failed"] += 1
                reason = "SOURCE_UNAVAILABLE" if "404" in str(exc) else "DOWNLOAD_FAILED"
                audit_results["failures"].append({
                    "date": d.isoformat(),
                    "layer": layer,
                    "status": reason,
                    "error": str(exc)
                })

        d += timedelta(days=1)

    rep_p = Path("reports/historical_acquisition_audit.json")
    rep_p.parent.mkdir(parents=True, exist_ok=True)
    rep_p.write_text(json.dumps(audit_results, indent=2, sort_keys=True), encoding="utf-8")
    print("Q1 2024 historical acquisition audit complete:", rep_p)

if __name__ == "__main__":
    complete_acquisition("2024-01-01", "2024-03-31")
