"""Trading-restriction and price-band context from official NSE reports."""
from __future__ import annotations
import pandas as pd


def normalize_restrictions(path, asof_time=None):
    from .pit_layers import _read, _num, _asof
    df=_read(path); ren={}
    aliases={'symbol':['SYMBOL','Symbol','TckrSymb'],'date':['DATE','Date','TradDt'],
             'upper_band':['UPPER','Upper Band','Upper Price Band','upper_band'],
             'lower_band':['LOWER','Lower Band','Lower Price Band','lower_band'],
             'surveillance':['SURVEILLANCE','Indicator','Surveillance Indicator','REG_IND'],
             'short_selling_allowed':['SHORT_SELLING','Short Selling','ShortSellingAllowed']}
    for t,cs in aliases.items():
        for c in cs:
            if c in df: ren[c]=t; break
    df=df.rename(columns=ren)
    if 'symbol' not in df: raise ValueError('restriction report requires symbol')
    if 'date' not in df: df['date']=pd.NaT
    df=_num(df,['upper_band','lower_band']); df=_asof(df,'date',asof_time)
    if 'short_selling_allowed' in df:
        s=df['short_selling_allowed'].astype(str).str.upper().str.strip()
        df['short_selling_allowed']=s.map({'Y':True,'YES':True,'TRUE':True,'1':True,'N':False,'NO':False,'FALSE':False,'0':False})
    return df


def restriction_flags(row, price=None, side=None):
    r={'restricted':False,'near_price_band':False,'short_sale_blocked':False}
    if 'surveillance' in row and pd.notna(row.get('surveillance')):
        s=str(row.get('surveillance')).upper()
        r['restricted']=s not in {'','NONE','NAN','NORMAL','NA','N/A'}
    if price is not None:
        for key,flag in [('upper_band','near_price_band'),('lower_band','near_price_band')]:
            v=row.get(key)
            if pd.notna(v) and float(v)>0 and abs(float(price)/float(v)-1)<=0.005: r[flag]=True
    if str(side).upper()=='SELL' and row.get('short_selling_allowed') is False:
        r['short_sale_blocked']=True
    return r
