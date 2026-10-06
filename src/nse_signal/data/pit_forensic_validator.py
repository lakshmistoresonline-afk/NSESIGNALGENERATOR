"""V31 True Clean-Room Forensic Validator: Independently recomputes source accounting, duplicates, conflicts, observation-to-interval mappings, and temporal intervals from raw NSE archives without importing builder logic."""
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

def run_forensic_validation(pit_dir="data/processed/pit", raw_manifest_path="data/reference/raw_manifest.json") -> dict:
    pit_p = Path(pit_dir)
    pit_p.mkdir(parents=True, exist_ok=True)
    man_p = Path(raw_manifest_path)

    if not man_p.exists():
        raise FileNotFoundError("Raw manifest missing for forensic validation.")

    raw_manifest = json.loads(man_p.read_text(encoding="utf-8"))
    successful = [m for m in raw_manifest if m.get("http_status") == 200 and m.get("parse_status") == "PASS"]

    forensic_dataset_stats = {}
    forensic_duplicates = []
    forensic_price_bars = []
    forensic_instrument_obs = []

    for m in successful:
        ds = m.get("dataset")
        ev_date = m.get("event_date")
        raw_file = m.get("raw_file_path")
        file_hash = m.get("sha256", "nohash")
        if not raw_file or not Path(raw_file).exists():
            raise FileNotFoundError(f"Forensic Audit Error: Raw file missing: {raw_file}")

        key = (ds, ev_date)
        forensic_dataset_stats[key] = {
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
            "equation_valid": False
        }
        acc = forensic_dataset_stats[key]

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

        df = pd.read_csv(io.TextIOWrapper(io.BytesIO(csv_bytes), encoding="utf-8", errors="replace"), low_memory=False)
        norm_count = len(df)
        acc["normalized_rows"] = norm_count

        if ds == "cash_bhavcopy":
            seen_pks = {}
            for idx, row in df.iterrows():
                row_dict = row.to_dict()
                fp = _full_row_fingerprint(ds, ev_date, file_hash, idx, row_dict)
                p_hash = _payload_hash(row_dict)
                symbol = _safe_str(row.get("TckrSymb") or row.get("SYMBOL") or row.get("Symbol"))
                try:
                    close_p, c_class = _safe_float(row.get("ClsPric") or row.get("CLOSE") or row.get("Close"))
                    open_p, o_class = _safe_float(row.get("OpnPric") or row.get("OPEN") or row.get("Open"), close_p)
                    high_p, h_class = _safe_float(row.get("HghPric") or row.get("HIGH") or row.get("High"), close_p)
                    low_p, l_class = _safe_float(row.get("LwPric") or row.get("LOW") or row.get("Low"), close_p)
                    vol, v_class = _safe_float(row.get("TtlTradgVol") or row.get("TOTTRDQTY") or row.get("Volume"))

                    if c_class != "VALID_NUMBER" or o_class != "VALID_NUMBER" or h_class != "VALID_NUMBER" or l_class != "VALID_NUMBER" or v_class != "VALID_NUMBER":
                        acc["rejected_rows"] += 1
                        continue
                    if symbol == "UNKNOWN" or close_p <= 0 or open_p <= 0 or high_p <= 0 or low_p <= 0 or high_p < low_p or vol < 0:
                        acc["rejected_rows"] += 1
                        continue

                    pk = (symbol, ev_date)
                    if pk in seen_pks:
                        existing_hash = seen_pks[pk]
                        if existing_hash == p_hash:
                            acc["exact_duplicate_observations"] += 1
                        else:
                            acc["conflict_observations"] += 1
                            forensic_duplicates.append({"dataset": ds, "event_date": ev_date, "identity": str(pk), "fingerprint": fp})
                        continue
                    seen_pks[pk] = p_hash

                    acc["canonical_observations"] += 1
                    forensic_price_bars.append({
                        "instrument_id": f"NSE_EQ_{symbol}",
                        "symbol": symbol,
                        "event_date": ev_date,
                        "source_row_fingerprint": fp
                    })
                except Exception:
                    acc["error_rows"] += 1

        elif ds == "security_master":
            seen_inst = {}
            for idx, row in df.iterrows():
                row_dict = row.to_dict()
                fp = _full_row_fingerprint(ds, ev_date, file_hash, idx, row_dict)
                p_hash = _payload_hash(row_dict)
                symbol = _safe_str(row.get("TckrSymb") or row.get("SYMBOL"))
                isin = _safe_str(row.get("ISIN"))
                series = _safe_str(row.get("SctySrs") or row.get("Series"))
                list_dt = _safe_str(row.get("ListgDt") or row.get("IsseDt"))
                if list_dt == "UNKNOWN": list_dt = ev_date

                if symbol == "UNKNOWN" or isin == "UNKNOWN":
                    acc["rejected_rows"] += 1
                    continue

                pk = (symbol, isin, series, ev_date)
                if pk in seen_inst:
                    existing_hash = seen_inst[pk]
                    if existing_hash == p_hash:
                        acc["exact_duplicate_observations"] += 1
                    else:
                        acc["conflict_observations"] += 1
                    continue
                seen_inst[pk] = p_hash

                acc["canonical_observations"] += 1
                forensic_instrument_obs.append({
                    "symbol": symbol, "isin": isin, "series": series,
                    "event_date": ev_date, "effective_from": list_dt, "source_row_fingerprint": fp
                })

        acc["unaccounted_rows"] = acc["normalized_rows"] - (acc["canonical_observations"] + acc["exact_duplicate_observations"] + acc["conflict_observations"] + acc["rejected_rows"] + acc["error_rows"])
        acc["equation_valid"] = (acc["unaccounted_rows"] == 0)

    # Independent Temporal Intervals Reconstruction
    forensic_intervals = []
    inst_groups = {}
    for obs in forensic_instrument_obs:
        identity_key = ("NSE", "CASH", obs["symbol"], obs["isin"], obs["series"])
        identity_key in inst_groups and inst_groups[identity_key].append(obs) or inst_groups.setdefault(identity_key, []).append(obs)

    mapped_obs_count = 0
    obs_to_interval_mapping = []

    for k, group in inst_groups.items():
        ex, seg, symbol, isin, series = k
        sorted_g = sorted(group, key=lambda x: x["effective_from"])
        unique_int = []
        for g in sorted_g:
            if not unique_int or unique_int[-1]["effective_from"] != g["effective_from"]:
                unique_int.append(g)

        for i, obs in enumerate(unique_int):
            eff_from = obs["effective_from"]
            eff_to = None
            if i + 1 < len(unique_int):
                eff_to = unique_int[i + 1]["effective_from"]

            int_id = f"FORENSIC_INT_{symbol}_{isin}_{series}_{eff_from}"
            forensic_intervals.append({
                "instrument_id": f"NSE_EQ_{symbol}_{isin}",
                "symbol": symbol,
                "effective_from": eff_from,
                "effective_to": eff_to,
                "interval_id": int_id,
                "source_row_fingerprint": obs["source_row_fingerprint"]
            })
            obs_to_interval_mapping.append({
                "source_row_fingerprint": obs["source_row_fingerprint"],
                "interval_id": int_id
            })
            mapped_obs_count += 1

    total_canonical_obs = sum(s["canonical_observations"] for s in forensic_dataset_stats.values())
    unmapped_obs = total_canonical_obs - mapped_obs_count - len(forensic_price_bars)

    forensic_recon = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_stats": {f"{k[0]}_{k[1]}": v for k, v in forensic_dataset_stats.items()},
        "total_source_observations": sum(s["source_rows"] for s in forensic_dataset_stats.values()),
        "total_normalized_observations": sum(s["normalized_rows"] for s in forensic_dataset_stats.values()),
        "total_canonical_observations": total_canonical_obs,
        "total_physical_intervals": len(forensic_intervals),
        "all_equations_valid": all(s["equation_valid"] for s in forensic_dataset_stats.values())
    }

    # Write Independent Forensic Artifacts
    (pit_p / "FORENSIC_SOURCE_RECONCILIATION.json").write_text(json.dumps(forensic_recon, indent=2, sort_keys=True), encoding="utf-8")
    (pit_p / "FORENSIC_DUPLICATE_ANALYSIS.json").write_text(json.dumps(forensic_duplicates, indent=2, sort_keys=True), encoding="utf-8")
    (pit_p / "OBSERVATION_INTERVAL_MAPPING.json").write_text(json.dumps(obs_to_interval_mapping, indent=2, sort_keys=True), encoding="utf-8")
    (pit_p / "FORENSIC_INTERVAL_ACCOUNTING.json").write_text(json.dumps({
        "canonical_observations": len(forensic_instrument_obs),
        "intervals_created": len(forensic_intervals),
        "observations_mapped": mapped_obs_count,
        "unmapped_observations": unmapped_obs,
        "status": "PASS" if unmapped_obs == 0 else "FAIL"
    }, indent=2, sort_keys=True), encoding="utf-8")

    return forensic_recon

if __name__ == "__main__":
    res = run_forensic_validation()
    print("Clean-Room Forensic Validation Result:", json.dumps(res, indent=2))
