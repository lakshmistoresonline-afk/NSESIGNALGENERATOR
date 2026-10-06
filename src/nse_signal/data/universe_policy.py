"""Strict Universe Architecture Policy: Separates BroadNSEEquityUniverse from Nifty200BenchmarkUniverse with explicit UNIVERSE_MODE configuration."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Literal, Optional, Dict, Any
from pathlib import Path
import pandas as pd
from datetime import datetime, timezone

UniverseMode = Literal["BROAD_NSE", "NIFTY200"]

@dataclass
class UniversePolicy:
    universe_mode: UniverseMode = "BROAD_NSE"
    allowed_series: tuple[str, ...] = ("EQ",)
    min_price: float = 5.0
    min_median_dollar_volume: float = 2_000_000.0
    min_history_days: int = 120
    max_staleness_days: int = 10
    nifty200_path: str = "data/reference/nifty200_membership.csv"

class BroadNSEEquityUniverse:
    """Broad NSE equity universe derived entirely from historical security identity and causal historical observations."""
    def __init__(self, policy: UniversePolicy):
        self.policy = policy

    def get_eligible_symbols(self, security_master: pd.DataFrame, timestamp: Any, bars: Optional[pd.DataFrame] = None) -> List[str]:
        if not {"symbol"}.issubset(security_master.columns):
            raise ValueError("security master requires symbol")
        t = pd.Timestamp(timestamp)
        if t.tzinfo is not None: t = t.tz_convert(None)

        sm = security_master.copy()
        if "effective_from" in sm.columns:
            ef = pd.to_datetime(sm.effective_from, utc=True, errors="coerce").dt.tz_convert(None)
            et = pd.to_datetime(sm.get("effective_to"), utc=True, errors="coerce").dt.tz_convert(None) if "effective_to" in sm.columns else pd.Series(pd.NaT, index=sm.index)
            # Interval contract [effective_from, effective_to)
            sm = sm[(ef <= t) & (et.isna() | (et > t))]
        if "series" in sm.columns:
            sm = sm[sm.series.astype(str).str.upper().isin({s.upper() for s in self.policy.allowed_series})]
        symbols = set(sm.symbol.astype(str).str.upper())
        if bars is None:
            return sorted(symbols)

        b = bars.copy()
        date_col = "timestamp" if "timestamp" in b.columns else ("date" if "date" in b.columns else None)
        if date_col:
            bt = pd.to_datetime(b[date_col], utc=True, errors="coerce").dt.tz_convert(None)
            b = b[bt <= t].copy()
        b["symbol"] = b.symbol.astype(str).str.upper()
        b = b[b.symbol.isin(symbols)]
        if b.empty: return []
        if "close" not in b.columns or "volume" not in b.columns:
            raise ValueError("bars require close and volume")
        b["close"] = pd.to_numeric(b.close, errors="coerce")
        b["volume"] = pd.to_numeric(b.volume, errors="coerce")
        b["dollar_volume"] = b.close * b.volume
        dc = date_col if date_col else "date"
        b[dc] = pd.to_datetime(b[dc], utc=True, errors="coerce").dt.tz_convert(None)
        b = b.dropna(subset=[dc, "close", "volume"]).drop_duplicates(["symbol", dc], keep="last")
        recent = b.sort_values(["symbol", dc]).groupby("symbol", sort=False).tail(self.policy.min_history_days)
        stats = recent.groupby("symbol").agg(
            last_close=("close", "last"),
            last_observation=(dc, "max"),
            median_dollar_volume=("dollar_volume", "median"),
            history=("close", "count"),
        )
        age_days = (t - stats.last_observation).dt.total_seconds() / 86400.0
        ok = stats[(stats.last_close >= float(self.policy.min_price)) &
                 (stats.median_dollar_volume >= float(self.policy.min_median_dollar_volume)) &
                 (stats.history >= int(self.policy.min_history_days)) &
                 (age_days <= float(self.policy.max_staleness_days))]
        return sorted(ok.index.astype(str).tolist())


class Nifty200BenchmarkUniverse:
    """Nifty 200 benchmark universe. Fails closed if historical membership is unavailable."""
    def __init__(self, policy: UniversePolicy):
        self.policy = policy

    def get_eligible_symbols(self, timestamp: Any) -> List[str]:
        p = Path(self.policy.nifty200_path)
        if not p.exists():
            raise FileNotFoundError(f"Nifty 200 benchmark membership file not found: {p}. Benchmark universe fails closed.")
        df = pd.read_csv(p)
        if df.empty:
            raise ValueError("Nifty 200 benchmark membership is empty. Fails closed.")
        req = {"symbol", "effective_from", "effective_to"}
        if not req.issubset(df.columns):
            raise ValueError(f"Nifty 200 membership missing columns: {sorted(req - set(df.columns))}")

        t = pd.Timestamp(timestamp)
        if t.tzinfo is not None: t = t.tz_convert(None)

        df['effective_from'] = pd.to_datetime(df['effective_from'], utc=True, errors='coerce').dt.tz_convert(None)
        df['effective_to'] = pd.to_datetime(df['effective_to'], utc=True, errors='coerce').dt.tz_convert(None)

        # Interval contract [effective_from, effective_to)
        active = df[(df.effective_from <= t) & (df.effective_to.isna() | (df.effective_to > t))]
        if active.empty:
            raise RuntimeError(f"Nifty 200 benchmark membership unavailable for timestamp {t}. Fails closed.")
        return sorted(active.symbol.astype(str).str.upper().unique().tolist())


def resolve_universe_symbols(policy: UniversePolicy, security_master: Optional[pd.DataFrame] = None, timestamp: Any = None, bars: Optional[pd.DataFrame] = None) -> List[str]:
    """Single universe policy router. Never infers mode."""
    if policy.universe_mode == "BROAD_NSE":
        if security_master is None or timestamp is None:
            raise ValueError("BROAD_NSE universe mode requires security_master and timestamp")
        engine = BroadNSEEquityUniverse(policy)
        return engine.get_eligible_symbols(security_master, timestamp, bars)
    elif policy.universe_mode == "NIFTY200":
        if timestamp is None:
            raise ValueError("NIFTY200 universe mode requires timestamp")
        engine = Nifty200BenchmarkUniverse(policy)
        return engine.get_eligible_symbols(timestamp)
    else:
        raise ValueError(f"Unknown UNIVERSE_MODE: {policy.universe_mode}")
