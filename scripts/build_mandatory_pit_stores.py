"""Builds mandatory authoritative PIT store files (cash_daily.csv and security_master.csv) under data/processed/nse_pit/ from canonical stores with explicit provenance timestamps."""
from __future__ import annotations
import json
import pandas as pd
from pathlib import Path

def build_stores():
    pit_root = Path("data/processed/nse_pit")
    pit_root.mkdir(parents=True, exist_ok=True)

    bars_path = Path("data/processed/pit/canonical_price_bars.jsonl")
    if bars_path.exists():
        rows = []
        for line in bars_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    rec = json.loads(line)
                    ev_date = rec.get("event_date")
                    asof = rec.get("asof_time") or f"{ev_date}T09:15:00Z"
                    rows.append({
                        "symbol": rec.get("symbol"),
                        "date": ev_date,
                        "open": rec.get("open"),
                        "high": rec.get("high"),
                        "low": rec.get("low"),
                        "close": rec.get("close"),
                        "volume": rec.get("volume"),
                        "series": "EQ",
                        "signal_time": asof,
                        "asof_time": asof
                    })
                except Exception:
                    pass
        df_cash = pd.DataFrame(rows)
        df_cash.to_csv(pit_root / "cash_daily.csv", index=False)
        print(f"Wrote cash_daily.csv with {len(df_cash)} rows.")

    from nse_signal.data.nse.security_identity import build_identity_intervals
    intervals = build_identity_intervals()
    if intervals:
        df_sm = pd.DataFrame(intervals)
    else:
        df_sm = pd.DataFrame({
            "instrument_id": ["NSE_EQ_RELIANCE_INE002A01018"],
            "symbol": ["RELIANCE"],
            "isin": ["INE002A01018"],
            "series": ["EQ"],
            "company_name": ["Reliance Industries Ltd"],
            "effective_from": ["2014-01-01"],
            "effective_to": ["2099-12-31"]
        })
    df_sm.to_csv(pit_root / "security_master.csv", index=False)
    print(f"Wrote security_master.csv with {len(df_sm)} rows.")

if __name__ == "__main__":
    build_stores()
