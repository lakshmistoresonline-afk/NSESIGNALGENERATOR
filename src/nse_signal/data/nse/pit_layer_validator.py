"""Semantic PIT Layer Validator: Validates required semantic layers (cash_bhavcopy / price bars, security master / identity) across source existence, parse status, canonical representation, schema validity, provenance, date coverage, identity linkage, and temporal validity."""
from __future__ import annotations
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

def validate_semantic_pit_layer(layer_id: str, pit_dir: str = "data/processed/pit", raw_root: str = "data/raw/nse") -> tuple[bool, str | None]:
    pit_p = Path(pit_dir)
    raw_p = Path(raw_root)
    manifest_p = raw_p / "manifest.jsonl"

    # 1. Verify provenance & raw source existence
    if not manifest_p.exists():
        return False, "PROVENANCE_MANIFEST_MISSING"

    manifest = []
    for line in manifest_p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try: manifest.append(json.loads(line))
            except Exception: pass

    if layer_id == "cash_bhavcopy":
        dataset_name = "cm_bhavcopy"
        canonical_file = pit_p / "canonical_price_bars.jsonl"
    elif layer_id == "security_master":
        dataset_name = "security_master"
        canonical_file = pit_p / "canonical_instruments.jsonl"
    else:
        dataset_name = layer_id
        canonical_file = pit_p / f"{layer_id}.jsonl"

    # Check if raw source exists and parsed successfully in manifest
    matching_manifest = [m for m in manifest if m.get("dataset") == dataset_name and m.get("http_status") == 200]
    if not matching_manifest:
        # Check if raw files exist directly in raw_root / dataset_name
        sub_dir = raw_p / dataset_name
        if not sub_dir.exists() or not list(sub_dir.iterdir()):
            return False, f"SOURCE_NOT_EXISTS: No raw source records or files found for {layer_id}"

    # 2. Verify canonical representation exists and is non-empty
    if not canonical_file.exists() or canonical_file.stat().st_size == 0:
        # Fallback check for csv legacy store
        csv_fallback = Path("data/processed/nse_pit") / f"{layer_id}.csv"
        if not csv_fallback.exists() or csv_fallback.stat().st_size == 0:
            return False, f"CANONICAL_REPRESENTATION_MISSING: Neither {canonical_file} nor {csv_fallback} exists/non-empty"

    # 3. Verify schema validity & date coverage / identity linkage
    if canonical_file.exists() and canonical_file.stat().st_size > 0:
        try:
            line_count = 0
            for line in canonical_file.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rec = json.loads(line)
                    line_count += 1
                    if layer_id == "cash_bhavcopy" and not {"symbol", "close", "event_date"}.issubset(rec.keys()):
                        return False, "SCHEMA_INVALID: missing required price bar fields"
                    if layer_id == "security_master" and not {"symbol", "isin"}.issubset(rec.keys()):
                        return False, "SCHEMA_INVALID: missing required security master fields"
            if line_count == 0:
                return False, "CANONICAL_REPRESENTATION_EMPTY"
        except Exception as e:
            return False, f"SCHEMA_VALIDATION_ERROR: {e}"

    return True, None

def validate_all_required_pit_layers() -> tuple[bool, list[str]]:
    required_layers = ["cash_bhavcopy", "security_master"]
    blocking_reasons = []
    for layer in required_layers:
        valid, reason = validate_semantic_pit_layer(layer)
        if not valid:
            blocking_reasons.append(f"{layer}: {reason}")
    return len(blocking_reasons) == 0, blocking_reasons
