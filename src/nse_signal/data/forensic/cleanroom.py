"""Iteration 9.9 Forensic Framework: True Independent Clean-Room Rebuild."""
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
    if val is None or pd.isna(val):
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

def execute_clean_room_rebuild(output_root: str, raw_manifest_path="data/reference/raw_manifest.json") -> dict:
    out_p = Path(output_root)
    out_p.mkdir(parents=True, exist_ok=True)
    man_p = Path(raw_manifest_path)

    if not man_p.exists():
        raise FileNotFoundError("Raw manifest missing for clean-room rebuild.")

    raw_manifest = json.loads(man_p.read_text(encoding="utf-8"))
    successful = [m for m in raw_manifest if m.get("http_status") == 200 and m.get("parse_status") == "PASS"]

    dataset_stats = {}
    price_bars = []
    raw_instrument_observations = []

    for m in successful:
        ds = m.get("dataset")
        ev_date = m.get("event_date")
        raw_file = m.get("raw_file_path")
        file_hash = m.get("sha256", "nohash")
        if not raw_file or not Path(raw_file).exists():
            continue

        key = (ds, ev_date)
        dataset_stats[key] = {
            "dataset": ds,
            "event_date": ev_date,
            "source_rows": m.get("rows", 0),
            "normalized_rows": 0,
            "canonical_observations": 0,
            "exact_duplicate_observations": 0,
            "conflict_observations": 0,
            "rejected_rows": 0,
            "error_rows": 0
        }
        acc = dataset_stats[key]

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
        acc["normalized_rows"] = len(df)

        if ds == "cash_bhavcopy":
            seen_pks = set()
            for idx, row in df.iterrows():
                row_dict = row.to_dict()
                fp = _full_row_fingerprint(ds, ev_date, file_hash, idx, row_dict)
                symbol = _safe_str(row.get("TckrSymb") or row.get("SYMBOL") or row.get("Symbol"))
                try:
                    close_p, c_class = _safe_float(row.get("ClsPric") or row.get("CLOSE") or row.get("Close"))
                    if c_class != "VALID_NUMBER" or symbol == "UNKNOWN" or close_p <= 0:
                        acc["rejected_rows"] += 1
                        continue
                    pk = (symbol, ev_date)
                    if pk in seen_pks:
                        acc["exact_duplicate_observations"] += 1
                        continue
                    seen_pks.add(pk)

                    acc["canonical_observations"] += 1
                    price_bars.append({
                        "instrument_id": f"NSE_EQ_{symbol}",
                        "symbol": symbol,
                        "event_date": ev_date,
                        "source_row_fingerprint": fp,
                        "close": close_p
                    })
                except Exception:
                    acc["error_rows"] += 1
        elif ds == "security_master":
            seen_inst = set()
            for idx, row in df.iterrows():
                row_dict = row.to_dict()
                fp = _full_row_fingerprint(ds, ev_date, file_hash, idx, row_dict)
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
                    acc["exact_duplicate_observations"] += 1
                    continue
                seen_inst.add(pk)

                acc["canonical_observations"] += 1
                raw_instrument_observations.append({
                    "symbol": symbol, "isin": isin, "series": series,
                    "event_date": ev_date, "effective_from": list_dt, "source_row_fingerprint": fp
                })

    # Construct intervals
    instruments = []
    symbol_groups = {}
    for obs in raw_instrument_observations:
        identity_key = ("NSE", "CASH", obs["symbol"], obs["isin"], obs["series"])
        symbol_groups.setdefault(identity_key, []).append(obs)

    for identity_key, obs_list in symbol_groups.items():
        ex, seg, symbol, isin, series = identity_key
        sorted_obs = sorted(obs_list, key=lambda x: x["effective_from"])
        unique_int = []
        for obs in sorted_obs:
            if not unique_int or unique_int[-1]["effective_from"] != obs["effective_from"]:
                unique_int.append(obs)

        for i, obs in enumerate(unique_int):
            eff_from = obs["effective_from"]
            eff_to = None
            if i + 1 < len(unique_int):
                eff_to = unique_int[i + 1]["effective_from"]

            int_id = f"CLEAN_INT_{symbol}_{isin}_{series}_{eff_from}"
            instruments.append({
                "instrument_id": f"NSE_EQ_{symbol}_{isin}",
                "symbol": symbol,
                "effective_from": eff_from,
                "effective_to": eff_to,
                "interval_id": int_id,
                "source_row_fingerprint": obs["source_row_fingerprint"]
            })

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_stats": {f"{k[0]}_{k[1]}": v for k, v in dataset_stats.items()},
        "total_source_observations": sum(s["source_rows"] for s in dataset_stats.values()),
        "total_normalized_observations": sum(s["normalized_rows"] for s in dataset_stats.values()),
        "total_canonical_observations": sum(s["canonical_observations"] for s in dataset_stats.values()),
        "total_physical_intervals": len(instruments)
    }

    out_p.joinpath("cleanroom_summary.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result
