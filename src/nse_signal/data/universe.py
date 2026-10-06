"""Point-in-time universe construction for broad NSE equity signals.

NIFTY 200 membership is useful for benchmark research but is not the same as
an India-wide NSE equity universe. This module provides a causal broad-universe
filter based on the historical security master and trailing liquidity.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

def load_point_in_time_membership(path: str = "data/reference/nifty200_membership.csv") -> pd.DataFrame:
    p=Path(path)
    if not p.exists(): raise FileNotFoundError(f"Point-in-time membership file not found: {p}")
    x=pd.read_csv(p)
    required={"symbol","effective_from","effective_to"}
    missing=required-set(x.columns)
    if missing: raise ValueError(f"Membership file missing columns: {sorted(missing)}")
    x["effective_from"]=pd.to_datetime(x["effective_from"],utc=True).dt.tz_convert(None)
    x["effective_to"]=pd.to_datetime(x["effective_to"],utc=True,errors="coerce").dt.tz_convert(None)
    return x.sort_values(["effective_from","symbol"]).reset_index(drop=True)

def validate_membership_intervals(membership: pd.DataFrame) -> pd.DataFrame:
    """Validate effective-dated security/universe intervals before use."""
    req={'symbol','effective_from','effective_to'}
    if not req.issubset(membership.columns):
        raise ValueError(f'membership missing columns: {sorted(req-set(membership.columns))}')
    x=membership.copy()
    x['symbol']=x['symbol'].astype(str).str.upper().str.strip()
    x['effective_from']=pd.to_datetime(x['effective_from'],utc=True,errors='coerce')
    x['effective_to']=pd.to_datetime(x['effective_to'],utc=True,errors='coerce')
    if x[['effective_from']].isna().any().any():
        raise ValueError('membership contains invalid effective_from dates')
    if (x['effective_to'].notna() & (x['effective_to']<x['effective_from'])).any():
        raise ValueError('membership contains inverted intervals')
    for sym,g in x.sort_values(['symbol','effective_from']).groupby('symbol'):
        prev=None
        for _,r in g.iterrows():
            if prev is not None and pd.notna(prev) and r.effective_from <= prev:
                raise ValueError(f'overlapping effective intervals for {sym}')
            prev=r.effective_to
    return x.sort_values(['effective_from','symbol']).reset_index(drop=True)

def symbols_as_of(timestamp, membership: pd.DataFrame) -> list[str]:
    membership=validate_membership_intervals(membership)
    ts=pd.Timestamp(timestamp)
    if ts.tzinfo is not None: ts=ts.tz_convert(None)
    m=membership[(membership.effective_from<=ts)&(membership.effective_to.isna()|(membership.effective_to>=ts))]
    return sorted(m.symbol.astype(str).str.upper().unique().tolist())

def broad_nse_equity_universe(security_master: pd.DataFrame, timestamp, bars: pd.DataFrame|None=None,
                              allowed_series=("EQ",), min_price=5.0, min_median_dollar_volume=2_000_000.0,
                              min_history_days=120, max_staleness_days=10) -> list[str]:
    """Return symbols eligible at *timestamp* without using future observations.

    Security identity/series is taken from the historical master as of the
    requested timestamp. Liquidity and history use only bars whose date is
    <= timestamp. The defaults intentionally avoid SME/illiquid series.
    """
    if not {"symbol"}.issubset(security_master.columns):
        raise ValueError("security master requires symbol")
    t=pd.Timestamp(timestamp)
    sm=security_master.copy()
    if "effective_from" in sm:
        ef=pd.to_datetime(sm.effective_from,utc=True,errors="coerce")
        et=pd.to_datetime(sm.get("effective_to"),utc=True,errors="coerce") if "effective_to" in sm else pd.Series(pd.NaT,index=sm.index)
        sm=sm[(ef<=t)&(et.isna()|(et>=t))]
    if "series" in sm:
        sm=sm[sm.series.astype(str).str.upper().isin({str(v).upper() for v in allowed_series})]
    symbols=set(sm.symbol.astype(str).str.upper())
    if bars is None:
        return sorted(symbols)
    b=bars.copy()
    if "timestamp" in b:
        bt=pd.to_datetime(b.timestamp,utc=True,errors="coerce"); b=b[bt<=t].copy()
    elif "date" in b:
        bd=pd.to_datetime(b.date,errors="coerce"); b=b[bd<=t].copy()
    b["symbol"]=b.symbol.astype(str).str.upper()
    b=b[b.symbol.isin(symbols)]
    if b.empty: return []
    if "close" not in b or "volume" not in b: raise ValueError("bars require close and volume")
    b["close"]=pd.to_numeric(b.close,errors="coerce")
    b["volume"]=pd.to_numeric(b.volume,errors="coerce")
    b["dollar_volume"]=b.close*b.volume
    date_col="timestamp" if "timestamp" in b else "date"
    b[date_col]=pd.to_datetime(b[date_col],utc=True,errors="coerce")
    b=b.dropna(subset=[date_col,"close","volume"]).drop_duplicates(["symbol",date_col],keep="last")
    recent=b.sort_values(["symbol",date_col]).groupby("symbol",sort=False).tail(min_history_days)
    stats=recent.groupby("symbol").agg(
        last_close=("close","last"),
        last_observation=(date_col,"max"),
        median_dollar_volume=("dollar_volume","median"),
        history=("close","count"),
    )
    age_days=(t-stats.last_observation).dt.total_seconds()/86400.0
    ok=stats[(stats.last_close>=float(min_price))&
             (stats.median_dollar_volume>=float(min_median_dollar_volume))&
             (stats.history>=int(min_history_days))&
             (age_days<=float(max_staleness_days))]
    return sorted(ok.index.astype(str).tolist())
