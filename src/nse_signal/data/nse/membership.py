"""Canonical Effective-Dated Interval Implementation for Universe Membership."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
from typing import Tuple, List, Optional

REQUIRED = {'symbol', 'effective_from', 'effective_to', 'source', 'source_asof'}

class MembershipError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code

def validate_half_open_membership(df: pd.DataFrame) -> pd.DataFrame:
    """Canonical half-open interval validation [effective_from, effective_to) without overlaps or inverted dates."""
    req = {'symbol', 'effective_from', 'effective_to'}
    if not req.issubset(df.columns):
        missing = sorted(req - set(df.columns))
        raise MembershipError("INCOMPLETE_SCHEMA", f"Membership file missing columns: {missing}")
    if df.empty:
        raise MembershipError("EMPTY_DATASET", "NIFTY 200 PIT membership is empty; refusing production/backtest use")

    x = df.copy()
    x['symbol'] = x['symbol'].astype(str).str.strip().str.upper()
    x['effective_from'] = pd.to_datetime(x['effective_from'], utc=True, errors='coerce').dt.tz_convert(None)
    x['effective_to'] = pd.to_datetime(x['effective_to'], utc=True, errors='coerce').dt.tz_convert(None)

    if x[['symbol', 'effective_from']].isna().any().any():
        raise MembershipError("MALFORMED_DATA", "Membership contains invalid identifiers or null effective_from dates")

    if (x['effective_to'].notna() & (x['effective_to'] <= x['effective_from'])).any():
        raise MembershipError("INVALID_INTERVAL", "Membership contains inverted or zero-length intervals where effective_to <= effective_from")

    for sym, g in x.sort_values(['symbol', 'effective_from']).groupby('symbol'):
        g_sorted = g.sort_values('effective_from').reset_index(drop=True)
        for i in range(len(g_sorted)):
            curr_to = g_sorted.loc[i, 'effective_to']
            for j in range(i + 1, len(g_sorted)):
                next_from = g_sorted.loc[j, 'effective_from']
                next_to = g_sorted.loc[j, 'effective_to']
                if pd.notna(curr_to) and next_from < curr_to:
                    cur_from = g_sorted.loc[i, 'effective_from']
                    if max(cur_from, next_from) < min(curr_to, next_to if pd.notna(next_to) else pd.Timestamp("2099-12-31")):
                        raise MembershipError("INTERVAL_OVERLAP", f"Overlapping effective intervals for symbol {sym}")

    return x.sort_values(['symbol', 'effective_from']).reset_index(drop=True)

def load_membership(path='data/reference/nifty200_membership.csv', allow_empty=False):
    p = Path(path)
    if not p.exists():
        raise MembershipError("UNAVAILABLE", f"Point-in-time membership file not found: {p}")
    df = pd.read_csv(p)
    if df.empty and not allow_empty:
        raise MembershipError("EMPTY_DATASET", "NIFTY 200 PIT membership is empty; refusing production/backtest use")

    validated = validate_half_open_membership(df)
    return validated

def membership_asof(membership, timestamp):
    t = pd.Timestamp(timestamp)
    if t.tzinfo is not None: t = t.tz_convert(None)
    # Half-open interval [effective_from, effective_to)
    x = membership[membership.effective_from <= t]
    return x[x.effective_to.isna() | (x.effective_to > t)].copy()

def assert_no_overlap(membership):
    validate_half_open_membership(membership)
    return True
