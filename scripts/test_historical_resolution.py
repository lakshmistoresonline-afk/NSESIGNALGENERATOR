"""Test historical source resolution across multiple years (2019-2026)."""
from __future__ import annotations
import datetime
import urllib.request
import json
from pathlib import Path

def resolve_historical_cm_url(d: datetime.date) -> str:
    # UDiFF format started July 8, 2024
    if d >= datetime.date(2024, 7, 8):
        return f"https://archives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{d:%Y%m%d}_F_0000.csv.zip"
    else:
        month_str = d.strftime("%b").upper()
        date_str = d.strftime("%d%b%Y").upper()
        return f"https://archives.nseindia.com/content/historical/EQUITIES/{d.year}/{month_str}/cm{date_str}bhav.csv.zip"

def resolve_historical_security_master_url(d: datetime.date) -> str:
    if d >= datetime.date(2024, 7, 8):
        return f"https://archives.nseindia.com/content/cm/NSE_CM_security_{d:%d%m%Y}.csv.gz"
    else:
        return "https://archives.nseindia.com/content/equities/EQUITY_L.csv"

def test_dates():
    test_dates = [
        datetime.date(2019, 1, 2),
        datetime.date(2020, 1, 2),
        datetime.date(2021, 1, 4),
        datetime.date(2022, 3, 2),
        datetime.date(2023, 1, 3),
        datetime.date(2024, 1, 2),
        datetime.date(2024, 8, 1),
        datetime.date(2025, 1, 2)
    ]

    results = []
    for d in test_dates:
        cm_url = resolve_historical_cm_url(d)
        sm_url = resolve_historical_security_master_url(d)

        cm_ok = False
        cm_bytes = 0
        try:
            req = urllib.request.Request(cm_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    cm_ok = True
                    cm_bytes = len(resp.read())
        except Exception:
            pass

        sm_ok = False
        sm_bytes = 0
        try:
            req = urllib.request.Request(sm_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    sm_ok = True
                    sm_bytes = len(resp.read())
        except Exception:
            pass

        results.append({
            "date": d.isoformat(),
            "cm_url": cm_url,
            "cm_available": cm_ok,
            "cm_bytes": cm_bytes,
            "sm_url": sm_url,
            "sm_available": sm_ok,
            "sm_bytes": sm_bytes
        })
        print(f"Date {d}: CM={cm_ok} ({cm_bytes}b), SM={sm_ok} ({sm_bytes}b)")

    Path("historical_source_availability.json").write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")

if __name__ == "__main__":
    test_dates()
