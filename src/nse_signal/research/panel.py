"""Point-in-time multi-symbol panel features and cross-sectional targets."""
from __future__ import annotations
import numpy as np
import pandas as pd


def add_cross_sectional_panel_features(df: pd.DataFrame, *, time_col='timestamp', symbol_col='symbol', sector_col='sector') -> pd.DataFrame:
    """Add within-timestamp ranks/z-scores without looking across time.

    The function is intentionally panel-only: every transformation is performed
    inside a timestamp group. Optional sector-relative transforms are nested
    inside the same timestamp, preventing future or later cross-sectional data
    from entering a historical row.
    """
    req = {time_col, symbol_col}
    missing = req - set(df.columns)
    if missing:
        raise ValueError(f"panel requires columns: {sorted(missing)}")
    x = df.copy()
    if "asof_time" in x.columns:
        ts=pd.to_datetime(x[time_col],utc=True,errors="coerce")
        av=pd.to_datetime(x["asof_time"],utc=True,errors="coerce")
        bad=av>ts
        if bad.any():
            raise ValueError(f"panel contains {int(bad.sum())} rows whose information was unavailable at timestamp")
    def rank01(s):
        n = s.notna().sum()
        return s.rank(method='average', pct=True) if n > 1 else pd.Series(np.nan, index=s.index)
    def z(s):
        mu, sd = s.mean(), s.std(ddof=0)
        return (s-mu)/sd if np.isfinite(sd) and sd > 0 else pd.Series(0.0, index=s.index)
    for source, name in [('return_1d','cs_return_rank'),('return_5d','cs_return_5d_rank'),('return_20d','cs_return_20d_rank'),('atr_pct','cs_vol_rank'),('dollar_volume','cs_liquidity_rank')]:
        if source in x.columns:
            x[name] = x.groupby(time_col, group_keys=False)[source].transform(rank01)
            x[name.replace('_rank','_z')] = x.groupby(time_col, group_keys=False)[source].transform(z)
    if 'return_1d' in x.columns:
        x['cs_market_return'] = x.groupby(time_col)['return_1d'].transform('median')
        x['cs_market_residual_1d'] = x['return_1d'] - x['cs_market_return']
    if sector_col in x.columns and 'return_1d' in x.columns:
        sec = x.groupby([time_col, sector_col], dropna=False)['return_1d'].transform('median')
        x['cs_sector_residual_1d'] = x['return_1d'] - sec
        x['cs_sector_return_rank'] = x.groupby(time_col, group_keys=False)['cs_sector_residual_1d'].transform(rank01)
    return x


def cross_sectional_future_excess_label(df: pd.DataFrame, *, time_col='timestamp', symbol_col='symbol', horizon=1, min_cross_section=5):
    """Create an OOS-friendly future cross-sectional excess-return label.

    Future returns are calculated per symbol, then compared only against the
    cross-sectional median at the future timestamp. The result is a ranking
    target, not an execution target; use it as an auxiliary research target.
    """
    req={time_col,symbol_col,'close'}
    if not req.issubset(df.columns): raise ValueError(f"missing columns: {sorted(req-set(df.columns))}")
    x=df.copy().sort_values([symbol_col,time_col])
    future=x.groupby(symbol_col)['close'].shift(-horizon)/x['close']-1.0
    future_time=x.groupby(symbol_col)[time_col].shift(-horizon)
    x['_future_return_cs']=future
    x['_future_time_cs']=future_time
    med=x.groupby('_future_time_cs')['_future_return_cs'].transform('median')
    counts=x.groupby('_future_time_cs')['_future_return_cs'].transform('count')
    x['cs_excess_target']=np.where(counts>=min_cross_section, (x['_future_return_cs']>med).astype(float), np.nan)
    return x.drop(columns=['_future_return_cs','_future_time_cs'])



def add_market_structure_features(df: pd.DataFrame, *, time_col='timestamp',
                                  symbol_col='symbol', benchmark_return_col='nifty_return',
                                  sector_col='sector', beta_window=60) -> pd.DataFrame:
    """Add causal market/sector structure features to an NSE panel.

    Beta/residual features are estimated from each security's trailing history,
    never by regressing all securities against one market observation at the
    same timestamp.  Breadth and dispersion use only securities available at
    the current timestamp.
    """
    req={time_col,symbol_col,'return_1d'}
    if not req.issubset(df.columns):
        return df.copy()
    x=df.copy().sort_values([symbol_col,time_col])
    r=pd.to_numeric(x['return_1d'],errors='coerce')
    if benchmark_return_col in x.columns:
        m=pd.to_numeric(x[benchmark_return_col],errors='coerce')
        def _beta(g):
            rr=g['r']; mm=g['m']
            cov=rr.rolling(beta_window,min_periods=max(20,beta_window//2)).cov(mm)
            var=mm.rolling(beta_window,min_periods=max(20,beta_window//2)).var()
            return cov/var.replace(0,np.nan)
        tmp=pd.DataFrame({'r':r,'m':m},index=x.index)
        beta=tmp.groupby(x[symbol_col],sort=False,group_keys=False).apply(_beta)
        if isinstance(beta.index,pd.MultiIndex):
            beta=beta.reset_index(level=0,drop=True)
        x['beta_60']=pd.to_numeric(beta,errors='coerce').reindex(x.index)
        x['cs_market_residual_1d']=r-x['beta_60']*m
        x['relative_strength_nifty']=(
            x.groupby(symbol_col,sort=False)['return_1d'].transform(lambda z:(1+z.fillna(0)).rolling(20,min_periods=10).apply(np.prod,raw=True)-1)
        )
    # Market breadth is a timestamp statistic, not a rolling statistic over
    # repeated security rows.
    g=x.groupby(time_col,sort=False)
    x['market_breadth_up_share']=g['return_1d'].transform(lambda z: z.gt(0).mean())
    x['market_breadth_down_share']=g['return_1d'].transform(lambda z: z.lt(0).mean())
    x['market_return_dispersion']=g['return_1d'].transform(lambda z: z.std(ddof=0))
    if 'atr_pct' in x.columns:
        x['market_high_vol_share']=g['atr_pct'].transform(lambda z: z.gt(z.median()).mean())
    if sector_col in x.columns:
        sec=x.groupby([time_col,sector_col],dropna=False)['return_1d'].transform('median')
        x['sector_relative_strength_20']=(
            (1+x['return_1d'].fillna(0)).groupby(x[symbol_col],sort=False)
            .transform(lambda z:z.rolling(20,min_periods=10).apply(np.prod,raw=True)-1)
            - (1+sec.fillna(0)).groupby(x[symbol_col],sort=False)
            .transform(lambda z:z.rolling(20,min_periods=10).apply(np.prod,raw=True)-1)
        )
    return x
