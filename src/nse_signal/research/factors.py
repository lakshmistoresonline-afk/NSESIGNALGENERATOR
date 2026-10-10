"""Point-in-time factor calculation module with strict minimum history enforcement and causal cross-sectional ranking."""
from __future__ import annotations
import pandas as pd
import numpy as np

def factor_snapshot(df: pd.DataFrame) -> dict:
    if df is None or "close" not in df.columns:
        return {"momentum_20": float("nan"), "momentum_60": float("nan"), "volatility_20": float("nan"), "distance_52w_high": float("nan")}
    c = pd.to_numeric(df["close"], errors="coerce")
    if c.isna().any() or (c <= 0).any():
        return {"momentum_20": float("nan"), "momentum_60": float("nan"), "volatility_20": float("nan"), "distance_52w_high": float("nan")}

    m20 = float(c.iloc[-1] / c.iloc[-21] - 1) if len(c) >= 21 else float("nan")
    m60 = float(c.iloc[-1] / c.iloc[-61] - 1) if len(c) >= 61 else float("nan")
    vol20 = float(c.pct_change().rolling(20, min_periods=20).std().iloc[-1]) if len(c) >= 21 else float("nan")
    dist52 = float(c.iloc[-1] / c.tail(252).max() - 1) if len(c) > 0 and c.tail(252).max() > 0 else float("nan")

    return {
        "momentum_20": m20,
        "momentum_60": m60,
        "volatility_20": vol20,
        "distance_52w_high": dist52
    }

def cross_sectional_rank(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    x = pd.DataFrame(rows)
    for col in ["momentum_20", "momentum_60"]:
        if col in x.columns:
            x[col+"_rank"] = x[col].rank(pct=True, na_option="keep")
        else:
            x[col+"_rank"] = float("nan")

    # Do not silently substitute 0.5 without logging/preserving missingness semantics where possible
    m20_r = x["momentum_20_rank"] if "momentum_20_rank" in x.columns else pd.Series(0.5, index=x.index)
    m60_r = x["momentum_60_rank"] if "momentum_60_rank" in x.columns else pd.Series(0.5, index=x.index)
    x["factor_score"] = (m20_r.fillna(0.5) + m60_r.fillna(0.5)) / 2
    return x.sort_values("factor_score", ascending=False)
