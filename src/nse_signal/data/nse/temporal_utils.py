"""Strict Temporal Utilities: Half-open interval semantics [effective_from, effective_to) and point-in-time causality checks."""
from __future__ import annotations
import pandas as pd
from datetime import datetime, date, timezone
from typing import Optional, Any, Tuple, List

def interval_contains(effective_from: Any, effective_to: Any, timestamp: Any) -> bool:
    """Check if timestamp falls within half-open interval [effective_from, effective_to)."""
    t = pd.Timestamp(timestamp)
    f = pd.Timestamp(effective_from)
    if t.tzinfo is not None and f.tzinfo is None:
        t = t.tz_convert(None)
    elif t.tzinfo is None and f.tzinfo is not None:
        f = f.tz_convert(None)

    if t < f:
        return False

    if pd.isna(effective_to) or effective_to is None:
        return True

    to = pd.Timestamp(effective_to)
    if t.tzinfo is not None and to.tzinfo is None:
        to = to.tz_convert(None)
    elif t.tzinfo is None and to.tzinfo is not None:
        to = to.tz_convert(None)

    return t < to

def interval_overlaps(f1: Any, t1: Any, f2: Any, t2: Any) -> bool:
    """Check if half-open intervals [f1, t1) and [f2, t2) overlap."""
    s1 = pd.Timestamp(f1)
    e1 = pd.Timestamp(t1) if pd.notna(t1) else pd.Timestamp("2099-12-31")
    s2 = pd.Timestamp(f2)
    e2 = pd.Timestamp(t2) if pd.notna(t2) else pd.Timestamp("2099-12-31")

    return max(s1, s2) < min(e1, e2)

def validate_half_open_intervals(df: pd.DataFrame, date_cols: Tuple[str, str] = ("effective_from", "effective_to")) -> Tuple[bool, List[str]]:
    """Validate that interval data conforms strictly to [effective_from, effective_to) without overlaps or inverted dates."""
    errors = []
    f_col, t_col = date_cols
    if not {f_col}.issubset(df.columns):
        return False, [f"Missing start column {f_col}"]

    x = df.copy()
    x[f_col] = pd.to_datetime(x[f_col], utc=True, errors="coerce")
    if t_col in x.columns:
        x[t_col] = pd.to_datetime(x[t_col], utc=True, errors="coerce")

    if x[f_col].isna().any():
        errors.append("Found null effective_from values")

    if t_col in x.columns:
        inverted = (x[t_col].notna() & (x[t_col] <= x[f_col]))
        if inverted.any():
            errors.append(f"Found {inverted.sum()} inverted or zero-length intervals where effective_to <= effective_from")

    if "symbol" in x.columns:
        for sym, g in x.sort_values([f_col]).groupby("symbol"):
            g_sorted = g.sort_values(f_col).reset_index(drop=True)
            for i in range(len(g_sorted) - 1):
                cur_to = g_sorted.loc[i, t_col] if t_col in g_sorted.columns else pd.NaT
                nxt_from = g_sorted.loc[i+1, f_col]
                if pd.notna(cur_to) and cur_to > nxt_from:
                    errors.append(f"Overlapping interval for {sym}: interval ends at {cur_to} but next starts at {nxt_from}")

    return len(errors) == 0, errors

def availability_is_causal(source_available_at: Any, decision_timestamp: Any) -> bool:
    """Enforce source_available_at <= decision_timestamp."""
    avail = pd.Timestamp(source_available_at)
    dec = pd.Timestamp(decision_timestamp)
    if avail.tzinfo is not None and dec.tzinfo is None:
        avail = avail.tz_convert(None)
    elif avail.tzinfo is None and dec.tzinfo is not None:
        dec = dec.tz_convert(None)
    return avail <= dec

def asof_join(left: pd.DataFrame, right: pd.DataFrame, on_col: str = "symbol", time_col: str = "timestamp", left_time: str = "decision_time", right_start: str = "effective_from", right_end: str = "effective_to") -> pd.DataFrame:
    """Perform a strict half-open point-in-time asof join using [right_start, right_end)."""
    # implementation using interval_contains or pandas merge_asof with half-open constraints
    res_rows = []
    for _, l_row in left.iterrows():
        t = l_row[left_time]
        sym = l_row[on_col]
        r_matches = right[(right[on_col] == sym) & (right[right_start] <= t) & (right[right_end].isna() | (right[right_end] > t))]
        if not r_matches.empty:
            for _, r_row in r_matches.iterrows():
                combined = {**l_row.to_dict(), **r_row.to_dict()}
                res_rows.append(combined)
    return pd.DataFrame(res_rows)
