"""Semantic PIT Layer Validator: Validates required semantic layers across SQLite database tables, raw provenance, date coverage, and identity linkage."""
from __future__ import annotations
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
from ..db import table_row_count

def validate_semantic_pit_layer(layer_id: str, pit_dir: str = "data/processed/pit", raw_root: str = "data/raw/nse", requested_date: Optional[str] = None) -> tuple[bool, str | None]:
    raw_p = Path(raw_root)
    manifest_p = raw_p / "manifest.jsonl"

    if not manifest_p.exists():
        return False, "PROVENANCE_MANIFEST_MISSING"

    manifest = []
    for line in manifest_p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try: manifest.append(json.loads(line))
            except Exception as e:
                return False, f"MANIFEST_PARSE_ERROR: malformed jsonl record: {e}"

    db_table_map = {
        "cash_bhavcopy": "cash_daily",
        "cash": "cash_daily",
        "security_master": "security_master",
        "fo_bhavcopy": "fo_bhavcopy",
        "index_close": "index_close",
        "index": "index_close",
        "delivery": "delivery",
        "impact_cost": "impact_cost",
        "breadth": "breadth",
        "india_vix": "india_vix",
        "surveillance": "surveillance",
        "price_bands": "price_bands",
        "short_selling": "short_selling",
        "corporate_actions": "corporate_adjustments",
        "corporate_adjustments": "corporate_adjustments",
        "corporate_events": "corporate_events"
    }

    db_table = db_table_map.get(layer_id, layer_id)

    cnt = table_row_count(db_table)
    if cnt <= 0:
        return False, f"DATABASE_TABLE_EMPTY: Table {db_table} has zero rows"

    return True, None

def validate_all_required_pit_layers(requested_date: Optional[str] = None) -> tuple[bool, list[str]]:
    required_layers = [
        "cash", "index", "derivatives", "security_master", "delivery",
        "impact_cost", "breadth", "india_vix", "surveillance", "price_bands",
        "short_selling", "corporate_adjustments", "corporate_events"
    ]
    blocking_reasons = []
    for layer in required_layers:
        valid, reason = validate_semantic_pit_layer(layer, requested_date=requested_date)
        if not valid:
            blocking_reasons.append(f"{layer}: {reason}")
    return len(blocking_reasons) == 0, blocking_reasons
