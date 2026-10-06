"""Explicit point-in-time corporate-action adjustment factors.

The system never infers split/bonus factors from price jumps. Factors must come
from an authoritative action record or a separately validated adjustment file.
"""
from __future__ import annotations
import pandas as pd


def normalize_adjustments(path):
    df=pd.read_csv(path)
    req={'symbol','effective_date','price_factor','volume_factor','available_at'}
    miss=req-set(df.columns)
    if miss: raise ValueError(f'corporate adjustment file missing {sorted(miss)}')
    df['effective_date']=pd.to_datetime(df.effective_date,errors='coerce')
    df['available_at']=pd.to_datetime(df.available_at,utc=True,errors='coerce')
    df['price_factor']=pd.to_numeric(df.price_factor,errors='coerce')
    df['volume_factor']=pd.to_numeric(df.volume_factor,errors='coerce')
    if df[['effective_date','available_at','price_factor','volume_factor']].isna().any().any():
        raise ValueError('invalid corporate adjustment values')
    if (df.price_factor<=0).any() or (df.volume_factor<=0).any(): raise ValueError('adjustment factors must be positive')
    df['signal_time']=df['available_at']; df['asof_time']=df['available_at']
    return df.sort_values(['symbol','effective_date','available_at'])


def apply_adjustments(price_df, adjustments):
    x=price_df.copy().sort_values(['symbol','date']); a=adjustments.copy()
    a['effective_date']=pd.to_datetime(a.effective_date); x['date']=pd.to_datetime(x.date)
    # Build cumulative backward factors. Each factor is applied to observations before its effective date.
    for sym,g in a.groupby('symbol'):
        mask=x.symbol.eq(sym)
        if not mask.any(): continue
        pg=x.loc[mask].copy()
        pf=1.0; vf=1.0
        for _,r in g.sort_values('effective_date',ascending=False).iterrows():
            before=pg.date < r.effective_date
            idx=pg.index[before]
            pg.loc[idx,'open']=pd.to_numeric(pg.loc[idx,'open'],errors='coerce')*float(r.price_factor)*pf
            pg.loc[idx,'high']=pd.to_numeric(pg.loc[idx,'high'],errors='coerce')*float(r.price_factor)*pf
            pg.loc[idx,'low']=pd.to_numeric(pg.loc[idx,'low'],errors='coerce')*float(r.price_factor)*pf
            pg.loc[idx,'close']=pd.to_numeric(pg.loc[idx,'close'],errors='coerce')*float(r.price_factor)*pf
            if 'volume' in pg: pg.loc[idx,'volume']=pd.to_numeric(pg.loc[idx,'volume'],errors='coerce')*float(r.volume_factor)*vf
            pf*=float(r.price_factor); vf*=float(r.volume_factor)
        x.loc[mask,pg.columns]=pg
    return x
