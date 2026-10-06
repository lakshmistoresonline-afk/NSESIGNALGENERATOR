"""Causal market-state transforms for financial ML.

These are deliberately optional research features. They never use future observations.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def fractional_difference(series: pd.Series, d: float = 0.4, window: int = 50, threshold: float = 1e-5) -> pd.Series:
    """Fixed-window fractional differentiation using only observations <= t.

    Fractional differentiation can preserve more low-frequency information than
    ordinary differencing while improving stationarity. The implementation is
    causal: weights are applied only to the current and historical values.
    """
    if not 0 <= d <= 1:
        raise ValueError("d must be in [0, 1]")
    if window < 2:
        raise ValueError("window must be >= 2")
    x = pd.Series(series, copy=False).astype(float)
    w = [1.0]
    for k in range(1, window):
        w.append(-w[-1] * (d - k + 1) / k)
    weights = np.asarray(w, dtype=float)
    weights[np.abs(weights) < threshold] = 0.0
    out = np.full(len(x), np.nan, dtype=float)
    a = x.to_numpy(dtype=float)
    for i in range(window - 1, len(a)):
        z = a[i - window + 1:i + 1]
        if np.isfinite(z).all():
            out[i] = float(np.dot(weights[::-1], z))
    return pd.Series(out, index=x.index, name=f"fracdiff_{d:g}_{window}")


def volume_bars(df: pd.DataFrame, volume_target: float) -> pd.DataFrame:
    """Aggregate OHLCV rows into causal volume bars.

    The bar closes as soon as cumulative volume reaches the target. This is a
    research sampling utility; no resampling across future timestamps occurs.
    """
    if volume_target <= 0:
        raise ValueError("volume_target must be positive")
    required = {"open", "high", "low", "close", "volume"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    rows=[]; start=None; v=0.0
    for ts, r in df.iterrows():
        if start is None: start=ts
        v += float(r.volume)
        rows.append(r)
        if v >= volume_target:
            x=pd.DataFrame(rows)
            rows=[]
            rows_dict={"timestamp":ts,"open":x.open.iloc[0],"high":x.high.max(),"low":x.low.min(),"close":x.close.iloc[-1],"volume":x.volume.sum()}
            rows_dict["bars_in_bucket"]=len(x)
            rows_dict["start_timestamp"]=start
            rows_dict["end_timestamp"]=ts
            yield_row=rows_dict
            yield_rows = yield_row
            yield_rows["volume_overshoot"] = float(v-volume_target)
            rows_out = yield_rows
            # Append after construction to avoid mutating source rows.
            if 'out' not in locals(): out=[]
            out.append(rows_out)
            start=None; v=0.0
    if 'out' not in locals():
        return pd.DataFrame(columns=["timestamp","open","high","low","close","volume","bars_in_bucket","start_timestamp","end_timestamp","volume_overshoot"])
    return pd.DataFrame(out).set_index("timestamp")
