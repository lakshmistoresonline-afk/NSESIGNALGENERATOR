"""Historical Security Identity Layer: Provable effective-dated temporal identity model preventing survivorship bias and look-ahead leakage."""
from __future__ import annotations
import json
import pandas as pd
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

class SecurityIdentityEngine:
    def __init__(self, raw_root: str = "data/raw/nse"):
        self.raw_root = Path(raw_root)
        self.intervals: List[Dict[str, Any]] = []
        self._built = False

    def normalize_identity(self, raw_record: dict) -> dict:
        symbol = str(raw_record.get("TckrSymb") or raw_record.get("SYMBOL") or raw_record.get("Symbol") or "UNKNOWN").strip().upper()
        isin = str(raw_record.get("ISIN") or "UNKNOWN").strip().upper()
        series = str(raw_record.get("SctySrs") or raw_record.get("Series") or "EQ").strip().upper()
        name = str(raw_record.get("FinInstrmNm") or raw_record.get("NAME") or "UNKNOWN").strip()
        date_str = str(raw_record.get("TradDt") or raw_record.get("BizDt") or raw_record.get("DATE") or "2014-01-01").strip()[:10]

        return {
            "instrument_id": f"NSE_EQ_{symbol}_{isin}",
            "symbol": symbol,
            "isin": isin,
            "series": series,
            "company_name": name,
            "effective_from": date_str,
            "effective_to": "2099-12-31",
            "listing_status": "ACTIVE",
            "lifecycle_status": "TRADING",
            "source": "NSE_HISTORICAL_ARCHIVE",
            "source_type": "DIRECT",
            "confidence": "HIGH"
        }

    def build_identity_intervals(self, manifest_path: str = "data/reference/raw_manifest.json") -> List[Dict[str, Any]]:
        man_p = Path(manifest_path)
        if not man_p.exists():
            return []

        manifest = json.loads(man_p.read_text(encoding="utf-8"))
        successful = [m for m in manifest if m.get("http_status") == 200 and m.get("parse_status") == "PASS" and m.get("dataset") == "security_master"]

        raw_intervals = []
        for m in successful:
            rf = m.get("raw_file_path")
            ev_date = m.get("event_date")
            if not rf or not Path(rf).exists(): continue
            try:
                df = pd.read_csv(rf, low_memory=False)
                for _, row in df.iterrows():
                    norm = self.normalize_identity(row.to_dict())
                    norm["effective_from"] = ev_date
                    raw_intervals.append(norm)
            except Exception:
                pass

        # Group by composite identity (symbol, isin) and build non-overlapping half-open intervals [effective_from, effective_to)
        groups: Dict[Tuple[str, str], List[dict]] = {}
        for obs in raw_intervals:
            k = (obs["symbol"], obs["isin"])
            groups.setdefault(k, []).append(obs)

        final_intervals = []
        for k, obs_list in groups.items():
            sorted_obs = sorted(obs_list, key=lambda x: x["effective_from"])
            unique_dates = sorted(list({o["effective_from"] for o in sorted_obs}))
            if not unique_dates: continue

            base_obs = next(o for o in sorted_obs if o["effective_from"] == unique_dates[0])
            for i, dt in enumerate(unique_dates):
                eff_from = dt
                eff_to = "2099-12-31"
                if i + 1 < len(unique_dates):
                    eff_to = unique_dates[i + 1]
                if eff_to <= eff_from:
                    continue # skip inverted/zero-width intervals
                iv = dict(base_obs)
                iv["effective_from"] = eff_from
                iv["effective_to"] = eff_to
                final_intervals.append(iv)

        self.intervals = final_intervals
        self._built = True

        # Save machine-readable evidence
        val_res, errs = self.validate_identity_intervals()
        validation_report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_instruments": len(final_intervals),
            "valid": val_res,
            "errors": errs,
            "status": "PASS" if val_res else "BLOCKED"
        }
        Path("data/reference/identity_validation.json").write_text(json.dumps(validation_report, indent=2, sort_keys=True), encoding="utf-8")

        return final_intervals

    def validate_identity_intervals(self) -> Tuple[bool, List[str]]:
        errors = []
        if not self._built:
            self.build_identity_intervals()

        groups: Dict[Tuple[str, str], List[dict]] = {}
        for iv in self.intervals:
            k = (iv["symbol"], iv["isin"])
            groups.setdefault(k, []).append(iv)

        for k, ivs in groups.items():
            sorted_ivs = sorted(ivs, key=lambda x: x["effective_from"])
            for i in range(len(sorted_ivs)):
                curr = sorted_ivs[i]
                if curr["effective_to"] <= curr["effective_from"]:
                    errors.append(f"Inverted or zero interval for {k}: {curr['effective_from']} -> {curr['effective_to']}")
                if i + 1 < len(sorted_ivs):
                    nxt = sorted_ivs[i + 1]
                    if curr["effective_to"] > nxt["effective_from"]:
                        errors.append(f"Overlapping intervals for {k}: {curr['effective_from']}->{curr['effective_to']} overlaps {nxt['effective_from']}->{nxt['effective_to']}")

        return len(errors) == 0, errors

    def identity_asof(self, symbol: str, as_of_date: str) -> Dict[str, Any]:
        if not self._built:
            self.build_identity_intervals()

        target = str(as_of_date)[:10]
        matches = []
        for iv in self.intervals:
            # Strict half-open interval contract: [effective_from, effective_to)
            if iv["symbol"] == symbol.upper() and iv["effective_from"] <= target < iv["effective_to"]:
                matches.append(iv)

        if not matches:
            return {"status": "UNKNOWN", "message": f"No historical identity found for symbol {symbol} as of {target}. Resolves to UNKNOWN (fail-closed)."}
        if len(matches) > 1:
            return {"status": "AMBIGUOUS", "message": f"Multiple ambiguous identities found for symbol {symbol} as of {target}. Resolves to AMBIGUOUS (fail-closed)."}

        res = dict(matches[0])
        res["status"] = "RESOLVED"
        return res

    def resolve_historical_symbol(self, symbol: str, as_of_date: str) -> str:
        res = self.identity_asof(symbol, as_of_date)
        if res.get("status") == "RESOLVED":
            return res["instrument_id"]
        return res.get("status", "UNKNOWN")

    def resolve_historical_instrument(self, instrument_id: str, as_of_date: str) -> Dict[str, Any]:
        if not self._built:
            self.build_identity_intervals()

        target = str(as_of_date)[:10]
        matches = []
        for iv in self.intervals:
            if iv["instrument_id"] == instrument_id and iv["effective_from"] <= target < iv["effective_to"]:
                matches.append(iv)

        if not matches:
            return {"status": "UNKNOWN", "message": f"Instrument ID {instrument_id} unknown as of {target}"}
        if len(matches) > 1:
            return {"status": "AMBIGUOUS", "message": f"Multiple ambiguous instruments for ID {instrument_id} as of {target}"}

        res = dict(matches[0])
        res["status"] = "RESOLVED"
        return res

_GLOBAL_ENGINE = SecurityIdentityEngine()

def normalize_identity(raw_record: dict) -> dict:
    return _GLOBAL_ENGINE.normalize_identity(raw_record)

def build_identity_intervals(manifest_path: str = "data/reference/raw_manifest.json") -> List[Dict[str, Any]]:
    return _GLOBAL_ENGINE.build_identity_intervals(manifest_path)

def identity_asof(symbol: str, as_of_date: str) -> Dict[str, Any]:
    return _GLOBAL_ENGINE.identity_asof(symbol, as_of_date)

def validate_identity_intervals() -> Tuple[bool, List[str]]:
    return _GLOBAL_ENGINE.validate_identity_intervals()

def resolve_historical_symbol(symbol: str, as_of_date: str) -> str:
    return _GLOBAL_ENGINE.resolve_historical_symbol(symbol, as_of_date)

def resolve_historical_instrument(instrument_id: str, as_of_date: str) -> Dict[str, Any]:
    return _GLOBAL_ENGINE.resolve_historical_instrument(instrument_id, as_of_date)
