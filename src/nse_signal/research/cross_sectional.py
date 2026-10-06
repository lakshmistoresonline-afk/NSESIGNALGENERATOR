"""Leakage-safe cross-sectional transforms for PIT multi-symbol panels."""
from __future__ import annotations
import numpy as np
import pandas as pd


def percentile_rank(s: pd.Series) -> pd.Series:
    return s.rank(pct=True, method='average')


def cross_sectional_features(panel: pd.DataFrame, *, timestamp_col='timestamp', symbol_col='symbol', sector_col='sector', return_col='return_1d', beta_col=None, availability_col='asof_time') -> pd.DataFrame:
    required={timestamp_col,symbol_col,return_col}
    missing=required-set(panel.columns)
    if missing: raise ValueError(f'Missing panel columns: {sorted(missing)}')
    x=panel.copy().sort_values([timestamp_col,symbol_col])
    ts=pd.to_datetime(x[timestamp_col],utc=True,errors='coerce')
    if availability_col in x.columns:
        av=pd.to_datetime(x[availability_col],utc=True,errors='coerce')
        if (av>ts).any():
            raise ValueError('cross-sectional panel contains information unavailable at its timestamp')
        x['_available']=av.le(ts)
    else:
        x['_available']=True

    def apply_cs(col, fn, group_cols=None):
        group_cols = group_cols if group_cols is not None else timestamp_col
        out = pd.Series(np.nan, index=x.index, dtype=float)
        for _, idx in x.groupby(by=group_cols, sort=False, dropna=False).groups.items():
            idx = list(idx); avail = x.loc[idx, '_available'].astype(bool); vals = x.loc[idx, col]
            vals = vals.where(avail)
            out.loc[idx] = fn(vals)
        return out

    x['cs_return_rank']=apply_cs(return_col, percentile_rank)
    x['cs_return_z']=apply_cs(return_col, lambda s: (s-s.mean())/s.std(ddof=0) if s.std(ddof=0)>0 else s*0.0)
    if 'realized_vol_20' in x: x['cs_vol_rank']=apply_cs('realized_vol_20', percentile_rank)
    if beta_col and beta_col in x: x['cs_beta_rank']=apply_cs(beta_col, percentile_rank)
    if sector_col in x:
        x['sector_return_rank']=apply_cs(return_col, percentile_rank, [timestamp_col,sector_col])
        x['sector_relative_return']=x[return_col]-apply_cs(return_col, lambda s:s.mean(), [timestamp_col,sector_col])
        x['sector_relative_rank']=apply_cs(return_col, percentile_rank, [timestamp_col,sector_col])
    x.drop(columns=['_available'],inplace=True)
    return x


def residualize_against_market(panel: pd.DataFrame, *, timestamp_col='timestamp', return_col='return_1d', market_return_col='nifty_return') -> pd.Series:
    if market_return_col not in panel or return_col not in panel: raise ValueError('market and return columns required')
    x=panel.copy()
    if 'asof_time' in x:
        ts=pd.to_datetime(x[timestamp_col],utc=True,errors='coerce'); av=pd.to_datetime(x.asof_time,utc=True,errors='coerce')
        if (av>ts).any(): raise ValueError('market residualization received unavailable observations')
    g=x.groupby(timestamp_col, sort=False)
    means=g[[return_col,market_return_col]].transform('mean')
    xm=x[return_col]-means[return_col]; mm=x[market_return_col]-means[market_return_col]
    denom=g[market_return_col].transform(lambda s: ((s-s.mean())**2).sum()).replace(0,np.nan)
    beta=xm*mm/denom
    return (xm-beta.fillna(0)*mm).rename('market_residual_return')
