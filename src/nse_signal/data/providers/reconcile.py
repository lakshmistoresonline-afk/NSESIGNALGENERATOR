from __future__ import annotations
import pandas as pd


def reconcile_candles(left: pd.DataFrame, right: pd.DataFrame, *, tolerance_bps: float = 5.0) -> dict:
    """Compare two secondary feeds without choosing a winner.

    Differences are diagnostics only. Neither feed becomes PIT-authoritative.
    """
    cols = ["open", "high", "low", "close", "volume"]
    a = left.copy(); b = right.copy()
    if "timestamp" not in a or "timestamp" not in b:
        raise ValueError("Both frames require timestamp")
    a["timestamp"] = pd.to_datetime(a["timestamp"], utc=True); b["timestamp"] = pd.to_datetime(b["timestamp"], utc=True)
    m = a.merge(b, on="timestamp", how="inner", suffixes=("_a", "_b"))
    if m.empty:
        return {"overlap_rows": 0, "max_abs_price_bps": None, "max_volume_pct": None, "disagreement": True}
    price_err = []
    vol_err = []
    for c in cols[:4]:
        den = m[f"{c}_a"].abs().replace(0, pd.NA)
        price_err.extend(((m[f"{c}_a"]-m[f"{c}_b"]).abs()/den*10000).dropna().tolist())
    den = m["volume_a"].abs().replace(0, pd.NA)
    vol_err = ((m["volume_a"]-m["volume_b"]).abs()/den*100).dropna().tolist()
    max_price = float(max(price_err)) if price_err else None
    max_vol = float(max(vol_err)) if vol_err else None
    return {"overlap_rows": int(len(m)), "max_abs_price_bps": max_price, "max_volume_pct": max_vol, "disagreement": bool(max_price is not None and max_price > tolerance_bps)}
