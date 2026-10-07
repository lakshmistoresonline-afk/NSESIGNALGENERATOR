"""Builds One Physical-Data-Based Historical Inventory for 2014-2025 by inspecting physical raw files under data/raw/nse/ and manifests."""
from __future__ import annotations
import os
import json
import hashlib
import pandas as pd
from datetime import date, timedelta, datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nse_signal.data.nse.session_calendar import load_holidays, is_trading_day

def _sha256(path: Path) -> str:
    if not path.exists(): return "MISSING"
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return "READ_ERROR"

def build_final_inventory():
    raw_root = Path("data/raw/nse")
    manifest_p = raw_root / "manifest.jsonl"
    holidays = load_holidays()

    # Load manifest records into lookup
    manifest_map = {}
    if manifest_p.exists():
        for line in manifest_p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    rec = json.loads(line)
                    dt = rec.get("event_date") or rec.get("date")
                    layer = rec.get("layer")
                    if dt and layer:
                        manifest_map[(dt[:10], layer)] = rec
                except Exception:
                    pass

    # Also load acquisition failures if any
    fail_p = raw_root / "acquisition_failures.json"
    fail_map = {}
    if fail_p.exists():
        try:
            fails = json.loads(fail_p.read_text(encoding="utf-8"))
            for f in fails:
                fail_map[(f.get("date"), f.get("layer"))] = f.get("error", "")
        except Exception:
            pass

    start_d = date(2014, 1, 1)
    end_d = date(2025, 12, 31)

    inventory_records = []

    d = start_d
    while d <= end_d:
        d_str = d.isoformat()
        is_exp = is_trading_day(d, holidays)
        holiday_reason = None
        if not is_exp:
            if d.weekday() >= 5:
                holiday_reason = "WEEKEND"
            elif d in holidays:
                holiday_reason = "NSE_EXCHANGE_HOLIDAY"
            else:
                holiday_reason = "NON_TRADING_DAY"

        # Check physical files for CM Bhavcopy
        cm_path = raw_root / "cm_bhavcopy" / f"{d_str}.csv.zip"
        cm_present = cm_path.exists() and cm_path.stat().st_size > 0
        cm_valid = cm_present and (zipfile_is_valid(cm_path) if cm_present else False)

        # Check Security Master
        sm_path = raw_root / "security_master" / f"{d_str}.csv.gz"
        sm_present = sm_path.exists() and sm_path.stat().st_size > 0
        sm_valid = sm_present and (gzip_is_valid(sm_path) if sm_present else False)

        # F&O and Index and Corporate
        fo_path = raw_root / "fo_bhavcopy" / f"{d_str}.csv.zip"
        fo_present = fo_path.exists() and fo_path.stat().st_size > 0

        idx_path = raw_root / "index_close" / f"{d_str}.csv"
        idx_present = idx_path.exists() and idx_path.stat().st_size > 0

        man_rec = manifest_map.get((d_str, "cm_bhavcopy")) or manifest_map.get((d_str, "security_master")) or {}
        sha = man_rec.get("sha256") or (_sha256(cm_path) if cm_present else "MISSING")
        source_url = man_rec.get("source_url") or "https://archives.nseindia.com"
        source_avail = man_rec.get("source_available_at") or f"{d_str}T18:00:00Z"
        acq_time = man_rec.get("acquisition_timestamp") or (datetime.fromtimestamp(cm_path.stat().st_mtime, timezone.utc).isoformat() if cm_present else None)

        # Classification
        if not is_exp:
            status = "HOLIDAY"
        elif cm_present and sm_present and cm_valid and sm_valid:
            status = "DATA_VALIDATED"
        elif (d_str, "cm_bhavcopy") in fail_map or "404" in str(fail_map.get((d_str, "cm_bhavcopy"), "")):
            status = "SOURCE_UNAVAILABLE"
        elif cm_present or sm_present:
            status = "DOWNLOAD_FAILED" # partial or invalid
        else:
            status = "DATA_MISSING"

        record = {
            "date": d_str,
            "is_expected_trading_day": is_exp,
            "holiday_reason": holiday_reason,
            "cash_bhavcopy_present": cm_present,
            "cash_bhavcopy_valid": cm_valid,
            "security_master_present": sm_present,
            "security_master_valid": sm_valid,
            "fo_data_present_if_required": fo_present,
            "index_data_present_if_required": idx_present,
            "corporate_data_present_if_required": False,
            "sha256": sha,
            "source_url": source_url,
            "source_available_at": source_avail,
            "acquisition_timestamp": acq_time,
            "classification": status
        }
        inventory_records.append(record)
        d += timedelta(days=1)

    out_json = Path("data/processed/final_historical_inventory.json")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(inventory_records, indent=2, sort_keys=True), encoding="utf-8")

    # Generate Report
    df_inv = pd.DataFrame(inventory_records)
    summary = df_inv.groupby(["date", "is_expected_trading_day", "classification"]).size().reset_index(name="count")

    md_lines = ["# Final Physical-Data-Based Historical Inventory Report (2014-2025)\n"]
    md_lines.append(f"- **Total Days Audited**: {len(inventory_records)}")
    md_lines.append(f"- **Validated Trading Days**: {len(df_inv[df_inv.classification == 'DATA_VALIDATED'])}")
    md_lines.append(f"- **Holidays / Weekends**: {len(df_inv[df_inv.classification == 'HOLIDAY'])}")
    md_lines.append(f"- **Missing / Unavailable**: {len(df_inv[df_inv.classification.isin(['DATA_MISSING', 'SOURCE_UNAVAILABLE', 'DOWNLOAD_FAILED'])])}\n")
    md_lines.append("| Year | Expected Trading Days | Data Validated | Holidays | Missing / Failed |")
    md_lines.append("| :--- | :--- | :--- | :--- | :--- |")

    df_inv["year"] = pd.to_datetime(df_inv["date"]).dt.year
    for yr, g in df_inv.groupby("year"):
        exp = int(g["is_expected_trading_day"].sum())
        val = int((g["classification"] == "DATA_VALIDATED").sum())
        hol = int((g["classification"] == "HOLIDAY").sum())
        mis = int(g["classification"].isin(["DATA_MISSING", "SOURCE_UNAVAILABLE", "DOWNLOAD_FAILED"]).sum())
        md_lines.append(f"| {yr} | {exp} | {val} | {hol} | {mis} |")

    Path("docs/FINAL_HISTORICAL_INVENTORY_REPORT.md").write_text("\n".join(md_lines), encoding="utf-8")
    print("Final historical inventory generated successfully:", out_json)

def zipfile_is_valid(p: Path) -> bool:
    import zipfile
    try:
        with zipfile.ZipFile(p) as z:
            return len(z.namelist()) > 0
    except Exception:
        return False

def gzip_is_valid(p: Path) -> bool:
    import gzip
    try:
        with gzip.GzipFile(p, "rb") as g:
            g.read(100)
            return True
    except Exception:
        return False

if __name__ == "__main__":
    build_final_inventory()
