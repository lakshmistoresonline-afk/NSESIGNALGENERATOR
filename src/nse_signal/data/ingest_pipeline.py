"""V31 Free/Public NSE Point-In-Time Data Reconstruction and Real Ingestion Pipeline with Date-Range Enumeration.

Strict Rule: NO hard-coded coverage numbers or fabricated download statuses.
All metrics, row counts, dates, and validation statuses must be dynamically computed
from actual execution evidence (downloaded archives, extracted CSVs, SHA256 hashes).
"""
from __future__ import annotations
import os
import json
import io
import gzip
import zipfile
import hashlib
import urllib.request
import urllib.error
from datetime import datetime, timezone, date, timedelta
from pathlib import Path
import pandas as pd
from .canonical import DataProvenance, InstrumentPIT, PriceBar, DerivativeContractPIT, OpenInterestPIT, DeliveryPIT, CorporateActionPIT, IndexMembershipPIT, SymbolHistoryPIT, MarketBreadthPIT, VolatilityPIT

def sha256_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

def download_nse_public_dataset(dataset: str, event_date: str, url: str) -> dict:
    """Attempt actual HTTP retrieval of public NSE data with immutable raw storage and archive extraction."""
    dt = datetime.strptime(event_date, "%Y-%m-%d")
    y, m, d = dt.strftime("%Y"), dt.strftime("%m"), dt.strftime("%d")
    raw_dir = Path("data/raw/nse") / dataset / y / m / d
    raw_dir.mkdir(parents=True, exist_ok=True)

    record = {
        "dataset": dataset,
        "event_date": event_date,
        "url": url,
        "http_status": None,
        "bytes": 0,
        "sha256": None,
        "rows": 0,
        "columns": [],
        "retrieval_timestamp": datetime.now(timezone.utc).isoformat(),
        "parse_status": "NOT_EXECUTED",
        "error": None
    }

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    })

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            record["http_status"] = resp.status
            content = resp.read()
            record["bytes"] = len(content)
            record["sha256"] = sha256_hash(content)

            ext = ".zip" if url.endswith(".zip") else (".gz" if url.endswith(".gz") else ".csv")
            file_path = raw_dir / f"{dataset}_{event_date}_{record['sha256'][:8]}{ext}"
            file_path.write_bytes(content)
            record["raw_file_path"] = str(file_path)

            # Real archive extraction and parsing
            try:
                csv_bytes = None
                if ext == ".zip" or content.startswith(b"PK\x03\x04"):
                    with zipfile.ZipFile(io.BytesIO(content)) as z:
                        namelist = z.namelist()
                        if namelist:
                            csv_bytes = z.read(namelist[0])
                elif ext == ".gz" or content.startswith(b"\x1f\x8b"):
                    with gzip.GzipFile(fileobj=io.BytesIO(content)) as gz:
                        csv_bytes = gz.read()
                else:
                    csv_bytes = content

                if csv_bytes:
                    text_wrapper = io.TextIOWrapper(io.BytesIO(csv_bytes), encoding="utf-8", errors="replace")
                    df = pd.read_csv(text_wrapper, low_memory=False)
                    record["rows"] = len(df)
                    record["columns"] = list(df.columns)
                    record["parse_status"] = "PASS"
                else:
                    record["parse_status"] = "EMPTY_ARCHIVE"
            except Exception as parse_exc:
                record["parse_status"] = "PARSE_ERROR"
                record["error"] = str(parse_exc)
    except urllib.error.HTTPError as he:
        record["http_status"] = he.code
        record["parse_status"] = "HTTP_ERROR"
        record["error"] = str(he)
    except Exception as exc:
        record["http_status"] = 0
        record["parse_status"] = "CONNECTION_ERROR"
        record["error"] = str(exc)

    return record

def run_real_ingestion(start_date: str, end_date: str) -> dict:
    """Run real historical ingestion across an enumerated date range (weekdays)."""
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    calendar_dates = []
    expected_trading_dates = []
    curr = start_dt
    while curr <= end_dt:
        d_str = curr.strftime("%Y-%m-%d")
        calendar_dates.append(d_str)
        if curr.weekday() < 5:  # Monday to Friday
            expected_trading_dates.append(d_str)
        curr += timedelta(days=1)

    datasets = [
        ("cash_bhavcopy", "https://archives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{YYYYMMDD}_F_0000.csv.zip"),
        ("security_master", "https://archives.nseindia.com/content/cm/NSE_CM_security_{DDMMYYYY}.csv.gz"),
    ]

    results = []
    attempted_dates = set()
    successful_dates = set()
    failed_dates = set()

    for d_str in expected_trading_dates:
        attempted_dates.add(d_str)
        dt = datetime.strptime(d_str, "%Y-%m-%d")
        dt_yyyymmdd = dt.strftime("%Y%m%d")
        dt_ddmmyyyy = dt.strftime("%d%m%Y")

        day_success = True
        for ds, url_tmpl in datasets:
            url = url_tmpl.replace("{YYYYMMDD}", dt_yyyymmdd).replace("{DDMMYYYY}", dt_ddmmyyyy)
            res = download_nse_public_dataset(ds, d_str, url)
            results.append(res)
            if res.get("http_status") != 200 or res.get("parse_status") != "PASS":
                day_success = False

        if day_success:
            successful_dates.add(d_str)
        else:
            failed_dates.add(d_str)

    missing_dates = set(expected_trading_dates) - successful_dates

    summary = {
        "requested_calendar_dates": calendar_dates,
        "expected_trading_dates": expected_trading_dates,
        "attempted_trading_dates": sorted(list(attempted_dates)),
        "successful_trading_dates": sorted(list(successful_dates)),
        "failed_trading_dates": sorted(list(failed_dates)),
        "missing_trading_dates": sorted(list(missing_dates)),
        "coverage_percentage": round(len(successful_dates) / len(expected_trading_dates) * 100, 2) if expected_trading_dates else 0.0
    }

    manifest_path = Path("data/reference/raw_manifest.json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")

    summary_path = Path("data/reference/ingestion_summary.json")
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    return summary

def assert_point_in_time_integrity(timestamp: str, instrument: str) -> bool:
    """Strict PIT verification ensuring no future leakage or unverified data."""
    ts = pd.to_datetime(timestamp, utc=True, errors="coerce")
    if pd.isna(ts):
        raise ValueError(f"PIT_INVALID: Invalid timestamp {timestamp}")
    now = datetime.now(timezone.utc)
    if ts > now:
        raise ValueError(f"PIT_INVALID: Future leakage detected for {instrument} at {timestamp}")
    return True
