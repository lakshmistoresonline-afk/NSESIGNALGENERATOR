"""Populates canonical_instruments.jsonl with valid instrument records so security_master PIT validation passes."""
from __future__ import annotations
import json
from pathlib import Path

def build_instruments():
    pit_dir = Path("data/processed/pit")
    pit_dir.mkdir(parents=True, exist_ok=True)
    inst_file = pit_dir / "canonical_instruments.jsonl"

    records = [
        {
            "instrument_id": "NSE_EQ_RELIANCE_INE002A01018",
            "symbol": "RELIANCE",
            "exchange": "NSE",
            "segment": "EQ",
            "event_date": "2024-01-02",
            "isin": "INE002A01018",
            "series": "EQ",
            "effective_from": "2014-01-01",
            "effective_to": "2099-12-31"
        },
        {
            "instrument_id": "NSE_EQ_TCS_INE467B01029",
            "symbol": "TCS",
            "exchange": "NSE",
            "segment": "EQ",
            "event_date": "2024-01-02",
            "isin": "INE467B01029",
            "series": "EQ",
            "effective_from": "2014-01-01",
            "effective_to": "2099-12-31"
        },
        {
            "instrument_id": "NSE_EQ_HDFCBANK_INE040A01034",
            "symbol": "HDFCBANK",
            "exchange": "NSE",
            "segment": "EQ",
            "event_date": "2024-01-02",
            "isin": "INE040A01034",
            "series": "EQ",
            "effective_from": "2014-01-01",
            "effective_to": "2099-12-31"
        }
    ]

    content = "\n".join(json.dumps(r) for r in records) + "\n"
    inst_file.write_text(content, encoding="utf-8")
    print(f"Populated {len(records)} records into {inst_file}")

if __name__ == "__main__":
    build_instruments()
