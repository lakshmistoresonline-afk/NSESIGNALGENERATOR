"""V31 Real PIT Builder: Two-tier accounting with synchronized payload-hash conflict vs exact duplicate classification between builder and forensic validator."""
from __future__ import annotations
import json
import io
import zipfile
import gzip
import hashlib
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

def _safe_str(val) -> str:
    if val is None:
        return "UNKNOWN"
    if pd.isna(val):
        return "UNKNOWN"
    s = str(val).strip()
    if s.lower() in ("nan", "nat", "none", "", "null", "undefined"):
        return "UNKNOWN"
    return s

def _safe_float(val, default=0.0) -> tuple[float, str]:
    if val is None:
        return default, "MISSING"
    if pd.isna(val):
        return default, "NaN"
    s = str(val).strip()
    if s.lower() in ("nan", "nat", "none", "", "null", "undefined"):
        return default, "MISSING"
    try:
        f = float(val)
        if pd.isna(f):
            return default, "NaN"
        return f, "VALID_NUMBER"
    except Exception:
        return default, "INVALID_NUMERIC"

def _full_row_fingerprint(dataset: str, event_date: str, file_hash: str, row_number: int, row_dict: dict) -> str:
    cleaned = {str(k): str(v) for k, v in row_dict.items() if not pd.isna(v)}
    content_str = json.dumps(cleaned, sort_keys=True, default=str)
    content_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()
    raw_sig = f"{dataset}|{event_date}|{file_hash}|{row_number}|{content_hash}"
    return hashlib.sha256(raw_sig.encode("utf-8")).hexdigest()

def _payload_hash(row_dict: dict) -> str:
    cleaned = {str(k): str(v) for k, v in row_dict.items() if not pd.isna(v)}
    return hashlib.sha256(json.dumps(cleaned, sort_keys=True, default=str).encode("utf-8")).hexdigest()

def build_pit_dataset(raw_manifest_path="data/reference/raw_manifest.json", output_dir="data/processed/pit") -> dict:
    out_p = Path(output_dir)
    out_p.mkdir(parents=True, exist_ok=True)
    manifest_p = Path(raw_manifest_path)

    raw_manifest = []
    if manifest_p.exists():
        try:
            raw_manifest = json.loads(manifest_p.read_text(encoding="utf-8"))
        except Exception as e:
            raise RuntimeError(f"Failed to load raw manifest: {e}")

    successful = [m for m in raw_manifest if m.get("http_status") == 200 and m.get("parse_status") == "PASS"]

    dataset_stats = {}
    price_bars = []
    raw_instrument_observations = []
    transformation_errors = []
    row_transformation_ledger = []
    duplicate_analysis_records = []

    for m in successful:
        ds = m.get("dataset")
        ev_date = m.get("event_date")
        raw_file = m.get("raw_file_path")
        file_hash = m.get("sha256", "nohash")
        if not raw_file or not Path(raw_file).exists():
            raise FileNotFoundError(f"CRITICAL: Raw file missing for {ds} at {ev_date}: {raw_file}")

        key = (ds, ev_date)
        if key not in dataset_stats:
            dataset_stats[key] = {
                "dataset": ds,
                "event_date": ev_date,
                "source_rows": m.get("rows", 0),
                "normalized_rows": 0,
                "canonical_observations": 0,
                "exact_duplicate_observations": 0,
                "conflict_observations": 0,
                "rejected_rows": 0,
                "error_rows": 0,
                "unaccounted_rows": 0,
                "reconciliation_status": "PENDING"
            }
        else:
            dataset_stats[key]["source_rows"] += m.get("rows", 0)

        acc = dataset_stats[key]

        try:
            content = Path(raw_file).read_bytes()
            csv_bytes = None
            if raw_file.endswith(".zip") or content.startswith(b"PK\x03\x04"):
                with zipfile.ZipFile(io.BytesIO(content)) as z:
                    nl = z.namelist()
                    if nl: csv_bytes = z.read(nl[0])
            elif raw_file.endswith(".gz") or content.startswith(b"\x1f\x8b"):
                with gzip.GzipFile(fileobj=io.BytesIO(content)) as gz:
                    csv_bytes = gz.read()
            else:
                csv_bytes = content

            if not csv_bytes:
                continue

            text_wrapper = io.TextIOWrapper(io.BytesIO(csv_bytes), encoding="utf-8", errors="replace")
            df = pd.read_csv(text_wrapper, low_memory=False)
            norm_count = len(df)
            acc["normalized_rows"] = norm_count

            if ds == "cash_bhavcopy":
                seen_pks = {}
                for idx, row in df.iterrows():
                    row_dict = row.to_dict()
                    fp = _full_row_fingerprint(ds, ev_date, file_hash, idx, row_dict)
                    p_hash = _payload_hash(row_dict)
                    symbol = _safe_str(row.get("TckrSymb") or row.get("SYMBOL") or row.get("Symbol"))
                    logical_key = f"CASH_{symbol}_{ev_date}"
                    try:
                        close_p, c_class = _safe_float(row.get("ClsPric") or row.get("CLOSE") or row.get("Close"))
                        open_p, o_class = _safe_float(row.get("OpnPric") or row.get("OPEN") or row.get("Open"), close_p)
                        high_p, h_class = _safe_float(row.get("HghPric") or row.get("HIGH") or row.get("High"), close_p)
                        low_p, l_class = _safe_float(row.get("LwPric") or row.get("LOW") or row.get("Low"), close_p)
                        vol, v_class = _safe_float(row.get("TtlTradgVol") or row.get("TOTTRDQTY") or row.get("Volume"))

                        if c_class != "VALID_NUMBER" or o_class != "VALID_NUMBER" or h_class != "VALID_NUMBER" or l_class != "VALID_NUMBER" or v_class != "VALID_NUMBER":
                            acc["rejected_rows"] += 1
                            row_transformation_ledger.append({
                                "dataset": ds, "source_file": raw_file, "source_hash": file_hash, "source_row_number": idx,
                                "source_row_fingerprint": fp, "logical_key": logical_key, "event_date": ev_date, "classification": "REJECTED",
                                "canonical_record_id": None, "temporal_interval_id": None,
                                "transformation_reason": "Invalid numeric fields", "transformation_version": "v31.9"
                            })
                            continue

                        if symbol == "UNKNOWN" or close_p <= 0 or open_p <= 0 or high_p <= 0 or low_p <= 0 or high_p < low_p or vol < 0:
                            acc["rejected_rows"] += 1
                            row_transformation_ledger.append({
                                "dataset": ds, "source_file": raw_file, "source_hash": file_hash, "source_row_number": idx,
                                "source_row_fingerprint": fp, "logical_key": logical_key, "event_date": ev_date, "classification": "REJECTED",
                                "canonical_record_id": None, "temporal_interval_id": None,
                                "transformation_reason": "Out of bounds OHLC or unknown symbol", "transformation_version": "v31.9"
                            })
                            continue

                        pk = (symbol, ev_date)
                        if pk in seen_pks:
                            existing_hash = seen_pks[pk]
                            if existing_hash == p_hash:
                                acc["exact_duplicate_observations"] += 1
                                classif = "EXACT_DUPLICATE"
                            else:
                                acc["conflict_observations"] += 1
                                classif = "CONFLICT"
                                duplicate_analysis_records.append({
                                    "dataset": ds, "event_date": ev_date, "identity_key": str(pk),
                                    "classification": classif, "row_index": idx, "fingerprint": fp
                                })
                            row_transformation_ledger.append({
                                "dataset": ds, "source_file": raw_file, "source_hash": file_hash, "source_row_number": idx,
                                "source_row_fingerprint": fp, "logical_key": logical_key, "event_date": ev_date, "classification": classif,
                                "canonical_record_id": None, "temporal_interval_id": None,
                                "transformation_reason": f"Payload analysis: {classif}", "transformation_version": "v31.9"
                            })
                            continue
                        seen_pks[pk] = p_hash

                        acc["canonical_observations"] += 1
                        rec_id = f"BAR_{symbol}_{ev_date}"

                        bar = {
                            "instrument_id": f"NSE_EQ_{symbol}",
                            "symbol": symbol,
                            "exchange": "NSE",
                            "segment": "CASH",
                            "event_date": ev_date,
                            "effective_from": ev_date,
                            "effective_to": ev_date,
                            "ingested_at": datetime.now(timezone.utc).isoformat(),
                            "source": "nse_public",
                            "source_type": "exchange_origin",
                            "source_url_or_identifier": m.get("url"),
                            "retrieval_timestamp": m.get("retrieval_timestamp"),
                            "raw_file_hash": file_hash,
                            "quality_status": "AUTHORITATIVE_PUBLIC",
                            "reconstruction_status": "CANONICALIZED",
                            "source_row_index": idx,
                            "source_row_fingerprint": fp,
                            "open": open_p,
                            "high": high_p,
                            "low": low_p,
                            "close": close_p,
                            "volume": vol
                        }
                        price_bars.append(bar)
                        row_transformation_ledger.append({
                            "dataset": ds, "source_file": raw_file, "source_hash": file_hash, "source_row_number": idx,
                            "source_row_fingerprint": fp, "logical_key": logical_key, "event_date": ev_date, "classification": "CANONICAL_OBSERVATION",
                            "canonical_record_id": rec_id, "temporal_interval_id": rec_id,
                            "transformation_reason": "Canonical PriceBar observation", "transformation_version": "v31.9"
                        })
                    except Exception as row_exc:
                        acc["error_rows"] += 1
                        row_transformation_ledger.append({
                            "dataset": ds, "source_file": raw_file, "source_hash": file_hash, "source_row_number": idx,
                            "source_row_fingerprint": fp, "logical_key": logical_key, "event_date": ev_date, "classification": "TRANSFORMATION_ERROR",
                            "canonical_record_id": None, "temporal_interval_id": None,
                            "transformation_reason": str(row_exc), "transformation_version": "v31.9"
                        })
                        transformation_errors.append({
                            "dataset": ds, "event_date": ev_date, "source_file": raw_file,
                            "stage": "price_bar_canonicalization", "exception_type": type(row_exc).__name__,
                            "message": str(row_exc), "row_index": idx
                        })

            elif ds == "security_master":
                seen_inst_keys = {}
                for idx, row in df.iterrows():
                    row_dict = row.to_dict()
                    fp = _full_row_fingerprint(ds, ev_date, file_hash, idx, row_dict)
                    p_hash = _payload_hash(row_dict)
                    symbol = _safe_str(row.get("TckrSymb") or row.get("SYMBOL"))
                    isin = _safe_str(row.get("ISIN"))
                    series = _safe_str(row.get("SctySrs") or row.get("Series"))
                    logical_key = f"SEC_{symbol}_{isin}_{series}_{ev_date}"
                    try:
                        list_dt = _safe_str(row.get("ListgDt") or row.get("IsseDt"))
                        if list_dt == "UNKNOWN":
                            list_dt = ev_date

                        if symbol == "UNKNOWN" or isin == "UNKNOWN":
                            acc["rejected_rows"] += 1
                            row_transformation_ledger.append({
                                "dataset": ds, "source_file": raw_file, "source_hash": file_hash, "source_row_number": idx,
                                "source_row_fingerprint": fp, "logical_key": logical_key, "event_date": ev_date, "classification": "REJECTED",
                                "canonical_record_id": None, "temporal_interval_id": None,
                                "transformation_reason": "Unknown symbol or ISIN", "transformation_version": "v31.9"
                            })
                            continue

                        pk = (symbol, isin, series, ev_date)
                        if pk in seen_inst_keys:
                            existing_hash = seen_inst_keys[pk]
                            if existing_hash == p_hash:
                                acc["exact_duplicate_observations"] += 1
                                classif = "EXACT_DUPLICATE"
                            else:
                                acc["conflict_observations"] += 1
                                classif = "CONFLICT"
                                duplicate_analysis_records.append({
                                    "dataset": ds, "event_date": ev_date, "identity_key": str(pk),
                                    "classification": classif, "row_index": idx, "fingerprint": fp
                                })
                            row_transformation_ledger.append({
                                "dataset": ds, "source_file": raw_file, "source_hash": file_hash, "source_row_number": idx,
                                "source_row_fingerprint": fp, "logical_key": logical_key, "event_date": ev_date, "classification": classif,
                                "canonical_record_id": None, "temporal_interval_id": None,
                                "transformation_reason": f"Payload analysis: {classif}", "transformation_version": "v31.9"
                            })
                            continue
                        seen_inst_keys[pk] = p_hash

                        acc["canonical_observations"] += 1
                        rec_id = f"INST_OBS_{symbol}_{isin}_{series}_{ev_date}"

                        inst_obs = {
                            "symbol": symbol,
                            "exchange": "NSE",
                            "segment": "CASH",
                            "event_date": ev_date,
                            "effective_from": list_dt,
                            "ingested_at": datetime.now(timezone.utc).isoformat(),
                            "source": "nse_public",
                            "source_type": "exchange_origin",
                            "source_url_or_identifier": m.get("url"),
                            "retrieval_timestamp": m.get("retrieval_timestamp"),
                            "raw_file_hash": file_hash,
                            "quality_status": "AUTHORITATIVE_PUBLIC",
                            "reconstruction_status": "CANONICALIZED",
                            "source_row_index": idx,
                            "source_row_fingerprint": fp,
                            "isin": isin,
                            "series": series
                        }
                        raw_instrument_observations.append((inst_obs, rec_id, raw_file, file_hash, idx, fp))
                        row_transformation_ledger.append({
                            "dataset": ds, "source_file": raw_file, "source_hash": file_hash, "source_row_number": idx,
                            "source_row_fingerprint": fp, "logical_key": logical_key, "event_date": ev_date, "classification": "CANONICAL_OBSERVATION",
                            "canonical_record_id": rec_id, "temporal_interval_id": None,
                            "transformation_reason": "Security master canonical observation", "transformation_version": "v31.9"
                        })
                    except Exception as row_exc:
                        acc["error_rows"] += 1
                        row_transformation_ledger.append({
                            "dataset": ds, "source_file": raw_file, "source_hash": file_hash, "source_row_number": idx,
                            "source_row_fingerprint": fp, "logical_key": logical_key, "event_date": ev_date, "classification": "TRANSFORMATION_ERROR",
                            "canonical_record_id": None, "temporal_interval_id": None,
                            "transformation_reason": str(row_exc), "transformation_version": "v31.9"
                        })
                        transformation_errors.append({
                            "dataset": ds, "event_date": ev_date, "source_file": raw_file,
                            "stage": "instrument_pit_canonicalization", "exception_type": type(row_exc).__name__,
                            "message": str(row_exc), "row_index": idx
                        })

            # Exact two-tier accounting verification equation:
            # normalized_rows == canonical_observations + exact_duplicate_observations + conflict_observations + rejected_rows + error_rows
            acc["unaccounted_rows"] = acc["normalized_rows"] - (acc["canonical_observations"] + acc["exact_duplicate_observations"] + acc["conflict_observations"] + acc["rejected_rows"] + acc["error_rows"])
            acc["reconciliation_status"] = "PASS" if acc["unaccounted_rows"] == 0 else "FAIL"

        except Exception as file_exc:
            if key in dataset_stats:
                dataset_stats[key]["error_rows"] += 1
            transformation_errors.append({
                "dataset": ds,
                "event_date": ev_date,
                "source_file": raw_file,
                "stage": "file_processing",
                "exception_type": type(file_exc).__name__,
                "message": str(file_exc),
                "row_index": -1
            })

    # Construct true non-overlapping temporal effective intervals using composite identity (exchange, segment, symbol, isin, series)
    instruments = []
    symbol_groups = {}
    for obs, rec_id, raw_file, sha, row_idx, fp in raw_instrument_observations:
        identity_key = (obs["exchange"], obs["segment"], obs["symbol"], obs["isin"], obs["series"])
        if identity_key not in symbol_groups:
            symbol_groups[identity_key] = []
        symbol_groups[identity_key].append(obs)

    for identity_key, obs_list in symbol_groups.items():
        ex, seg, symbol, isin, series = identity_key
        sorted_obs = sorted(obs_list, key=lambda x: x["effective_from"])
        unique_intervals = []
        for obs in sorted_obs:
            if not unique_intervals or unique_intervals[-1]["effective_from"] != obs["effective_from"]:
                unique_intervals.append(obs)

        for i, obs in enumerate(unique_intervals):
            eff_from = obs["effective_from"]
            eff_to = None
            if i + 1 < len(unique_intervals):
                eff_to = unique_intervals[i + 1]["effective_from"]

            interval_id = f"INT_{symbol}_{isin}_{series}_{eff_from}"
            inst_record = {
                "instrument_id": f"NSE_EQ_{symbol}_{isin}",
                "symbol": symbol,
                "exchange": obs["exchange"],
                "segment": obs["segment"],
                "event_date": obs["event_date"],
                "effective_from": eff_from,
                "effective_to": eff_to,
                "ingested_at": obs["ingested_at"],
                "source": obs["source"],
                "source_type": obs["source_type"],
                "source_url_or_identifier": obs["source_url_or_identifier"],
                "retrieval_timestamp": obs["retrieval_timestamp"],
                "raw_file_hash": obs["raw_file_hash"],
                "quality_status": obs["quality_status"],
                "reconstruction_status": obs["reconstruction_status"],
                "source_row_index": obs["source_row_index"],
                "source_row_fingerprint": obs.get("source_row_fingerprint"),
                "isin": isin,
                "series": series,
                "interval_id": interval_id
            }
            instruments.append(inst_record)

    # Persist dataset-specific canonical files
    bars_file = out_p / "canonical_price_bars.jsonl"
    with open(bars_file, "w", encoding="utf-8") as f:
        for b in price_bars:
            f.write(json.dumps(b) + "\n")

    inst_file = out_p / "canonical_instruments.jsonl"
    with open(inst_file, "w", encoding="utf-8") as f:
        for i in instruments:
            f.write(json.dumps(i) + "\n")

    ledger_file = out_p / "row_transformation_ledger.jsonl"
    with open(ledger_file, "w", encoding="utf-8") as f:
        for item in row_transformation_ledger:
            f.write(json.dumps(item) + "\n")

    dup_file = out_p / "CHK10_DUPLICATE_ANALYSIS.json"
    dup_file.write_text(json.dumps(duplicate_analysis_records, indent=2, sort_keys=True), encoding="utf-8")

    err_file = out_p / "transformation_errors.json"
    err_file.write_text(json.dumps(transformation_errors, indent=2, sort_keys=True), encoding="utf-8")

    total_canonical_obs = sum(s["canonical_observations"] for s in dataset_stats.values())
    total_intervals = len(instruments)
    total_rejected = sum(s["rejected_rows"] for s in dataset_stats.values())
    total_errors = sum(s["error_rows"] for s in dataset_stats.values())
    total_normalized = sum(s["normalized_rows"] for s in dataset_stats.values())
    total_source = sum(s["source_rows"] for s in dataset_stats.values())

    all_reconciled = all(s["reconciliation_status"] == "PASS" for s in dataset_stats.values())

    pit_manifest = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "datasets_processed": len(successful),
        "dataset_accounting": {f"{k[0]}_{k[1]}": v for k, v in dataset_stats.items()},
        "source_rows": total_source,
        "normalized_rows": total_normalized,
        "canonical_observations": total_canonical_obs,
        "temporal_intervals": total_intervals,
        "canonical_rows": total_canonical_obs,
        "rejected_rows": total_rejected,
        "error_rows": total_errors,
        "reconciliation_matched": all_reconciled,
        "status": "PIT_RECONSTRUCTION_PARTIAL",
        "production_gate": "BLOCKED"
    }

    manifest_out = out_p / "pit_manifest.json"
    manifest_out.write_text(json.dumps(pit_manifest, indent=2, sort_keys=True), encoding="utf-8")

    accounting_state_path = out_p / "row_accounting.json"
    accounting_state_path.write_text(json.dumps(pit_manifest, indent=2, sort_keys=True), encoding="utf-8")

    return pit_manifest
