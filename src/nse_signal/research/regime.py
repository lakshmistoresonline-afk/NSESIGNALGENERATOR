"""Leakage-safe Indian market regime features.
All market-wide rolling calculations are performed on one observation per
market timestamp, never on repeated per-symbol rows.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
def rolling_percentile(s,n=252):
    s=pd.Series(s,dtype=float)
    return s.rolling(int(n),min_periods=int(n)).apply(lambda z: float(np.mean(z<=z[-1])),raw=True)

def _market_series(x: pd.DataFrame):
    bench_col = "nifty_close" if "nifty_close" in x.columns else ("benchmark_close" if "benchmark_close" in x.columns else None)
    if bench_col is not None:
        v=pd.to_numeric(x[bench_col],errors="coerce")
        if "timestamp" in x.columns:
            ts=pd.to_datetime(x["timestamp"],utc=True,errors="coerce")
            one=pd.DataFrame({"ts":ts,"v":v}).dropna().groupby("ts")["v"].last().sort_index()
            return one, ("nifty_close" if bench_col=="nifty_close" else "benchmark:benchmark_close")
        return v, ("nifty_close" if bench_col=="nifty_close" else "benchmark:benchmark_close")
    if "nifty_return" in x.columns and "timestamp" in x.columns:
        ts=pd.to_datetime(x["timestamp"],utc=True,errors="coerce")
        r=pd.to_numeric(x["nifty_return"],errors="coerce")
        one=pd.DataFrame({"ts":ts,"r":r}).dropna().groupby("ts")["r"].last().sort_index()
        return (1.0+one).cumprod()*100.0, "nifty_return"
    if {"timestamp","return_1d"}.issubset(x.columns):
        ts=pd.to_datetime(x["timestamp"],utc=True,errors="coerce")
        r=pd.to_numeric(x["return_1d"],errors="coerce")
        one=pd.DataFrame({"ts":ts,"r":r}).dropna().groupby("ts")["r"].median().sort_index()
        return (1.0+one).cumprod()*100.0, "cross_section_median_return_proxy"
    if "close" in x.columns:
        return pd.to_numeric(x["close"],errors="coerce"), "stock_proxy"
    return pd.Series(dtype=float), "missing_market_context"

def _timestamp_map(x, series):
    if "timestamp" not in x.columns:
        if isinstance(series,pd.Series) and len(series)==len(x):
            return pd.Series(series.to_numpy(dtype=float),index=x.index)
        return pd.Series(np.nan,index=x.index,dtype=float)
    ts=pd.to_datetime(x["timestamp"],utc=True,errors="coerce")
    if isinstance(series,pd.Series) and isinstance(series.index,pd.DatetimeIndex):
        return ts.map(series)
    return pd.Series(np.nan,index=x.index,dtype=float)

def _unique_context(x, col):
    if col not in x.columns or "timestamp" not in x.columns:
        return pd.Series(dtype=float)
    ts=pd.to_datetime(x["timestamp"],utc=True,errors="coerce")
    v=pd.to_numeric(x[col],errors="coerce")
    return pd.DataFrame({"ts":ts,"v":v}).dropna().groupby("ts")["v"].last().sort_index()

def add_regime_features(df: pd.DataFrame) -> pd.DataFrame:
    x=df.copy()
    if "timestamp" in x.columns:
        x["timestamp"]=pd.to_datetime(x["timestamp"],utc=True,errors="coerce")
    market, source = _market_series(x)
    if "timestamp" in x.columns:
        m=_timestamp_map(x, market if isinstance(market,pd.Series) else pd.Series(dtype=float))
        market_ts = market if isinstance(market,pd.Series) else pd.Series(dtype=float)
        market_ts=market_ts.sort_index()
    else:
        m=pd.to_numeric(market,errors="coerce")
        market_ts=pd.Series(m.to_numpy(),index=x.index)
    x["market_context_source"]=source
    # Compute each market statistic once per timestamp, then broadcast.
    if not market_ts.empty:
        sma=market_ts.rolling(200,min_periods=200).mean()
        ret=market_ts.pct_change()
        vol=ret.rolling(20,min_periods=10).std()*np.sqrt(252)
        vp=rolling_percentile(vol,252)
        trend_slope=ret.rolling(63,min_periods=30).mean()
        regime=pd.DataFrame({
            "market_sma_200_gap":market_ts/sma-1.0,
            "market_trend_slope_63":trend_slope,
            "market_realized_vol_20":vol,
            "market_vol_percentile_252":vp,
        })
        x["market_sma_200_gap"]=_timestamp_map(x,regime.market_sma_200_gap)
        x["market_trend_slope_63"]=_timestamp_map(x,regime.market_trend_slope_63)
        x["market_realized_vol_20"]=_timestamp_map(x,regime.market_realized_vol_20)
        x["market_vol_percentile_252"]=_timestamp_map(x,regime.market_vol_percentile_252)
    else:
        for c in ["market_sma_200_gap","market_trend_slope_63","market_realized_vol_20","market_vol_percentile_252"]:
            x[c]=np.nan
    # Market context series must also be de-duplicated before rolling.
    v=_unique_context(x,"india_vix")
    if not v.empty:
        x["india_vix_percentile_252"]=_timestamp_map(x,rolling_percentile(v,252))
        x["india_vix_change_5"]=_timestamp_map(x,v.pct_change(5))
    if "advance_decline_ratio" in x.columns:
        a=_unique_context(x,"advance_decline_ratio")
        if not a.empty:
            az=(a-a.rolling(20,min_periods=20).mean())/a.rolling(20,min_periods=20).std()
            x["breadth_z20"]=_timestamp_map(x,az)
    if "nifty_return" in x.columns:
        nr=_unique_context(x,"nifty_return")
        if not nr.empty:
            x["nifty_regime_return_20"]=_timestamp_map(x,nr.rolling(20,min_periods=20).sum())
    x["regime_trend"]=np.select([x.market_sma_200_gap>0.03,x.market_sma_200_gap<-0.03],[1,-1],default=0)
    x["regime_vol"]=pd.cut(x.market_realized_vol_20,bins=[-np.inf,.15,.30,np.inf],labels=[0,1,2]).astype(float)
    x["regime_id"]=x.regime_trend*3+x.regime_vol.fillna(1)
    return x
