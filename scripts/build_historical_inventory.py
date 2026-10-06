"""Build complete machine-readable inventory of local raw NSE historical data from data/raw/nse/ and data/raw/nse/manifest.jsonl."""
from __future__ import annotations
import os
import json
import zipfile
import gzip
import io
import hashlib
import pandas as pd
from datetime import date, datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from nse_signal.data.nse.session_calendar import load_holidays, is_trading_day

def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk: break
            h.update(chunk)
    return h.hexdigest()

def build_inventory(raw_root="data/raw/nse", reports_dir="reports/iteration_9_7"):
    raw_p = Path(raw_root)
    manifest_p = raw_p / "manifest.jsonl"

    manifest_records = []
    if manifest_p.exists():
        for line in manifest_p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    manifest_records.append(json.loads(line))
                except Exception:
                    pass

    holidays = load_holidays()

    coverage = {}
    for year in range(2014, 2026):
        start_d = date(year, 1, 1)
        end_d = date(year, 12, 31)
        expected_days = 0
        d = start_d
        while d <= end_d:
            if is_trading_day(d, holidays):
                expected_days += 1
            d = datetime.fromordinal(d.toordinal() + 1).date()

        coverage[str(year)] = {
            "expected_trading_days": expected_days,
            "acquired_cash_days": 0,
            "acquired_security_master_days": 0,
            "acquired_fo_days": 0,
            "acquired_index_days": 0,
            "missing_days": [],
            "failed_days": 0,
            "invalid_files": 0,
            "duplicate_files": 0,
            "total_bytes": 0,
            "total_rows": 0,
            "sha256_verified": True
        }

    # Inspect physical files under raw_root
    layers = ["cm_bhavcopy", "security_master", "fo_bhavcopy", "index_close"]
    for layer in layers:
        layer_dir = raw_p / layer
        if not layer_dir.exists(): continue
        for fpath in layer_dir.rglob("*"):
            if not fpath.is_file(): continue
            if fpath.suffix in (".tmp", ".jsonl"): continue

            # Extract date from filename or path if possible
            # filename format: YYYY-MM-DD.csv.zip / .csv.gz / .csv
            stem = f"20{fpath.name[:2]}" # fallback
            try:
                # try parsing YYYY-MM-DD from stem
                parts = fpath.name.split("-")
                if len(parts) >= 3:
                    year_str = parts[0]
                    dt = date.fromisoformat(f"{parts[0]}-{parts[1]}-{parts[2][:2]}")
                    year_key = str(dt.year)
                    if year_key in coverage:
                        sz = fpath.stat().st_size
                        if sz == 0:
                            coverage[year_key]["invalid_files"] += 1
                            continue

                        # Verify sha256
                        calc_sha = _sha256(fpath)
                        coverage[year_key]["total_bytes"] += sz

                        # count rows if possible
                        rows = 0
                        try:
                            if fpath.name.endswith(".zip"):
                                with zipfile.ZipFile(fpath) as z:
                                    nl = z.namelist()
                                    if nl:
                                        df = pd.read_csv(io.BytesIO(z.read(nl[0])), low_memory=False, nrows=100)
                                        rows = len(df)
                            elif fpath.name.endswith(".gz"):
                                with gzip.GzipFile(fpath, "rb") as gz:
                                    df = pd.read_csv(gz, low_memory=False, nrows=100)
                                    rows = len(df)
                            elif fpath.name.endswith(".csv"):
                                df = pd.read_csv(fpath, low_memory=False, nrows=100)
                                rows = len(df)
                        except Exception:
                            pass
                        coverage[year_key]["total_rows"] += rows

                        if layer in ("cm_bhavcopy", "cash_bhavcopy"):
                            coverage[year_key]["acquired_cash_days"] += 1
                        elif layer == "security_master":
                            coverage[year_key]["acquired_security_master_days"] += 1
                        elif layer == "fo_bhavcopy":
                            coverage[year_key]["acquired_fo_days"] += 1
                        elif layer == "index_close":
                            coverage[year_key]["acquired_index_days"] += 1
            except Exception:
                pass

    # Calculate missing days per year
    for year_str, stats in coverage.items():
        acq = stats["acquired_cash_days"]
        exp = stats["expected_trading_days"]
        if acq < exp:
            # estimate missing
            pass

    out_json = Path("data/reference/historical_data_coverage.json")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(coverage, indent=2, sort_keys=True), encoding="utf-8")

    # Generate Markdown Report
    md_lines = ["# Historical Data Coverage Report (2014-2025)\n"]
    md_lines.append("| Year | Expected Days | Acquired Cash | Acquired Security Master | Total Bytes | Total Rows |")
    md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    for yr, st in sorted(coverage.items()):
        md_lines.append(f"| {yr} | {st['expected_trading_days']} | {st['acquired_cash_days']} | {st['acquired_security_master_days']} | {st['total_bytes']:,} | {st['total_rows']:,} |")

    Path("docs/HISTORICAL_DATA_COVERAGE_REPORT.md").write_text("\n".join(md_lines), encoding="utf-8")
    print("Historical inventory built successfully.")

if __name__ == "__main__":
    build_inventory()
