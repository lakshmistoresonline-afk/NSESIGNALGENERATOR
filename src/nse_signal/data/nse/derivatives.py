"""Point-in-time derivatives context derived from official NSE F&O rows.

Only information present in the supplied F&O report is used. No options Greeks
are invented; IV/skew fields are used only when actually present.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def _weighted_mean(g, value, weight):
    v=pd.to_numeric(g[value], errors='coerce'); w=pd.to_numeric(g[weight], errors='coerce').clip(lower=0)
    ok=v.notna() & w.notna() & (w>0)
    if not ok.any(): return np.nan
    return float(np.average(v[ok], weights=w[ok]))


def build_derivatives_context(fo: pd.DataFrame, spot: pd.DataFrame | None = None, *, timestamp_col='date') -> pd.DataFrame:
    req={'symbol','expiry','option_type','strike','close','volume','oi','oi_change'}
    miss=req-set(fo.columns)
    if miss: raise ValueError(f'F&O context missing columns: {sorted(miss)}')
    x=fo.copy()
    x[timestamp_col]=pd.to_datetime(x[timestamp_col], errors='coerce')
    x['expiry']=pd.to_datetime(x['expiry'], errors='coerce')
    for c in ['strike','close','volume','oi','oi_change','underlying','iv']:
        if c in x: x[c]=pd.to_numeric(x[c],errors='coerce')
    x=x.dropna(subset=['symbol',timestamp_col,'expiry'])
    # nearest listed expiry on each trade date; never use a later observation.
    x['days_to_expiry']=(x['expiry']-x[timestamp_col]).dt.days
    x=x[x.days_to_expiry>=0].copy()
    nearest=x.groupby([timestamp_col,'symbol'])['days_to_expiry'].transform('min')
    x=x[x.days_to_expiry==nearest].copy()
    opt=x[x.option_type.astype(str).str.upper().isin(['CE','PE','CALL','PUT'])].copy()
    if opt.empty: return pd.DataFrame(columns=['symbol','date'])
    opt['is_put']=opt.option_type.astype(str).str.upper().isin(['PE','PUT'])
    rows=[]
    for (d,sym),g in opt.groupby([timestamp_col,'symbol'],sort=False):
        put=g[g.is_put]; call=g[~g.is_put]
        row={'date':d,'symbol':sym,
             'nearest_expiry':g.expiry.min(),
             'nearest_dte':float(g.days_to_expiry.min()),
             'put_oi':float(put.oi.sum()),'call_oi':float(call.oi.sum()),
             'put_volume':float(put.volume.sum()),'call_volume':float(call.volume.sum()),
             'put_oi_change':float(put.oi_change.sum()),'call_oi_change':float(call.oi_change.sum())}
        row['pcr_oi']=row['put_oi']/row['call_oi'] if row['call_oi']>0 else np.nan
        row['pcr_volume']=row['put_volume']/row['call_volume'] if row['call_volume']>0 else np.nan
        row['pcr_oi_change']=row['put_oi_change']/row['call_oi_change'] if row['call_oi_change']!=0 else np.nan
        if 'iv' in g:
            row['weighted_iv']=_weighted_mean(g,'iv','oi')
            row['put_iv']=_weighted_mean(put,'iv','oi')
            row['call_iv']=_weighted_mean(call,'iv','oi')
            row['iv_skew_put_minus_call']=row['put_iv']-row['call_iv'] if np.isfinite(row['put_iv']) and np.isfinite(row['call_iv']) else np.nan
        rows.append(row)
    out=pd.DataFrame(rows)
    if spot is not None and not out.empty and {'symbol','date','close'}.issubset(spot.columns):
        sp=spot[['symbol','date','close']].copy(); sp['date']=pd.to_datetime(sp['date'],errors='coerce')
        sp=sp.rename(columns={'close':'spot_close'})
        out=out.merge(sp,on=['symbol','date'],how='left')
        # nearest strike OI concentration around spot, computed within the available chain.
        conc=[]
        for (d,sym),g in opt.groupby([timestamp_col,'symbol'],sort=False):
            spotv=out.loc[(out.date==d)&(out.symbol==sym),'spot_close']
            sv=float(spotv.iloc[0]) if len(spotv) and pd.notna(spotv.iloc[0]) else np.nan
            if not np.isfinite(sv): conc.append((d,sym,np.nan)); continue
            strike_oi=g.groupby('strike',dropna=True).oi.sum()
            total=float(strike_oi.sum())
            top=float(strike_oi.iloc[(strike_oi.index.to_numpy()-sv).__abs__().argmin()]) if len(strike_oi) else np.nan
            conc.append((d,sym,top/total if total>0 else np.nan))
        cdf=pd.DataFrame(conc,columns=['date','symbol','atm_strike_oi_share'])
        out=out.merge(cdf,on=['date','symbol'],how='left')
    # Nearest-expiry futures basis is kept separate from option metrics.
    fut= x[~x.option_type.astype(str).str.upper().isin(['CE','PE','CALL','PUT'])].copy()
    if not fut.empty and spot is not None and {'symbol','date','close'}.issubset(spot.columns):
        fs=fut.sort_values(['date','symbol','days_to_expiry']).drop_duplicates(['date','symbol'])[['date','symbol','close']].rename(columns={'close':'futures_close'})
        sp=spot[['symbol','date','close']].copy().rename(columns={'close':'spot_close'}); sp['date']=pd.to_datetime(sp.date,errors='coerce')
        fs=fs.merge(sp,on=['symbol','date'],how='left'); fs['futures_basis']=fs.futures_close/fs.spot_close-1.0
        out=out.merge(fs[['date','symbol','futures_basis']],on=['date','symbol'],how='left')
    return out.sort_values(['date','symbol']).reset_index(drop=True)
