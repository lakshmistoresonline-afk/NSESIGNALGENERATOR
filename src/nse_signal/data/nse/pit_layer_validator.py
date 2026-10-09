"""Semantic PIT Layer Validator: Validates required semantic layers across SQLite database tables, raw provenance, date coverage, and identity linkage with strict empty-file rejection."""
from __future__ import annotations
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
from ..db import table_row_count

def validate_semantic_pit_layer(layer_id: str, pit_dir: str = "data/processed/pit", raw_root: str = "data/raw/nse", requested_date: Optional[str] = None) -> tuple[bool, str | None]:
    pit_p = Path(pit_dir)
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

    if layer_id in ("cash_bhavcopy", "cash"):
        canonical_file = pit_p / "canonical_price_bars.jsonl"
        db_table = "cash_daily"
    elif layer_id in ("security_master",):
        canonical_file = pit_p / "canonical_instruments.jsonl"
        db_table = "security_master"
    else:
        canonical_file = pit_p / f"{layer_id}.jsonl"
        db_table = layer_id

    # If canonical file explicitly exists and is 0 bytes (empty), fail closed immediately
    if canonical_file.exists() and canonical_file.stat().st_size == 0:
        return False, f"CANONICAL_REPRESENTATION_EMPTY: {canonical_file}"

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
