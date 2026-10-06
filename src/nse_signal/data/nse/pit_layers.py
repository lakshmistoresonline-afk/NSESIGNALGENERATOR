"""PIT adapters for secondary NSE market/report layers.

These adapters normalize locally acquired official NSE files. They never invent
availability timestamps: a caller must provide the actual publication/as-of time
or the adapter uses a conservative end-of-day availability timestamp documented
by the source contract.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
from .session_calendar import next_trading_day, session_open_utc, session_close_utc


def _read(path):
    p=Path(path)
    if p.suffix.lower()=='.zip':
        import zipfile
        with zipfile.ZipFile(p) as z:
            names=[n for n in z.namelist() if n.lower().endswith(('.csv','.txt'))]
            if not names: raise ValueError(f'No CSV/TXT in {p}')
            return pd.read_csv(z.open(names[0]), low_memory=False)
    return pd.read_csv(p, low_memory=False)


def _num(df, cols):
    for c in cols:
        if c in df: df[c]=pd.to_numeric(df[c].astype(str).str.replace(',','',regex=False),errors='coerce')
    return df


def _asof(df, date_col, asof_time=None, availability_policy='next_session_open'):
    d=pd.to_datetime(df[date_col],errors='coerce')
    if d.isna().any(): raise ValueError(f"invalid {date_col} values")
    df['market_time']=d.map(session_close_utc)
    if asof_time is not None:
        a=pd.to_datetime(asof_time,utc=True)
        if not isinstance(a,pd.Series): a=pd.Series(a,index=df.index)
    elif availability_policy == 'next_session_open':
        # Conservative rule for EOD reports with no embedded publication timestamp.
        a=d.map(next_trading_day).map(session_open_utc)
    else:
        raise ValueError(f'unknown availability policy: {availability_policy}')
    df['date']=d; df['signal_time']=a; df['asof_time']=a
    return df


def normalize_delivery(path, asof_time=None):
    df=_read(path); ren={}
    aliases={'symbol':['SYMBOL','Symbol','TckrSymb'],'series':['SERIES','Series','SctySrs'],
             'date':['DATE','Date','TradDt'],'deliverable_qty':['DELIV_QTY','Deliverable Qty','DlyQty'],
             'delivery_pct':['DELIV_PER','% Dly Qt to Traded Qty','DlyQtyPct'],'volume':['TOTTRDQTY','Total Traded Quantity','TtlTradgVol']}
    for t,cs in aliases.items():
        for c in cs:
            if c in df: ren[c]=t; break
    df=df.rename(columns=ren)
    need=['symbol','date','deliverable_qty','delivery_pct']
    miss=[c for c in need if c not in df]
    if miss: raise ValueError(f'delivery report missing {miss}')
    df=_num(df,['deliverable_qty','delivery_pct','volume']); df=_asof(df,'date',asof_time)
    return df[['symbol','series','date','deliverable_qty','delivery_pct','volume','signal_time','asof_time']].copy() if 'series' in df else df[['symbol','date','deliverable_qty','delivery_pct','volume','signal_time','asof_time']].copy()


def normalize_impact_cost(path, asof_time=None):
    df=_read(path); ren={}
    aliases={'symbol':['SYMBOL','Symbol','Scrip','Security'],'impact_cost':['IMPACT_COST','Impact Cost','ImpactCost'],
             'date':['DATE','Date','TradDt']}
    for t,cs in aliases.items():
        for c in cs:
            if c in df: ren[c]=t; break
    df=df.rename(columns=ren)
    if 'symbol' not in df or 'impact_cost' not in df: raise ValueError('impact-cost report requires symbol and impact_cost')
    if 'date' not in df: df['date']=pd.NaT
    df=_num(df,['impact_cost']); df=_asof(df,'date',asof_time)
    return df[['symbol','date','impact_cost','signal_time','asof_time']]


def normalize_breadth(path, asof_time=None):
    df=_read(path); ren={}
    aliases={'date':['DATE','Date','TradDt'],'advances':['ADVANCES','Advances','Adv'],'declines':['DECLINES','Declines','Dec'],'unchanged':['UNCHANGED','Unchanged']}
    for t,cs in aliases.items():
        for c in cs:
            if c in df: ren[c]=t; break
    df=df.rename(columns=ren)
    if 'date' not in df or 'advances' not in df or 'declines' not in df: raise ValueError('breadth report requires date, advances, declines')
    df=_num(df,['advances','declines','unchanged']); df['ad_ratio']=df['advances']/df['declines'].replace(0,pd.NA); df['net_breadth']=df['advances']-df['declines']; df=_asof(df,'date',asof_time)
    df['symbol']='__MARKET__'; return df[['symbol','date','advances','declines','unchanged','ad_ratio','net_breadth','signal_time','asof_time']]


def normalize_vix(path, asof_time=None):
    df=_read(path); ren={}
    aliases={'date':['DATE','Date','TradDt'],'open':['OPEN','Open'],'high':['HIGH','High'],'low':['LOW','Low'],'close':['CLOSE','Close'],'prev_close':['PREV_CLOSE','Prev. Close'],'change':['CHANGE','Change'],'pct_change':['PERCENT_CHANGE','% Change']}
    for t,cs in aliases.items():
        for c in cs:
            if c in df: ren[c]=t; break
    df=df.rename(columns=ren)
    if 'date' not in df or 'close' not in df: raise ValueError('India VIX report requires date and close')
    df=_num(df,['open','high','low','close','prev_close','change','pct_change']); df=_asof(df,'date',asof_time)
    for c in ['open','high','low','prev_close','change','pct_change']:
        if c not in df: df[c]=pd.NA
    df['symbol']='__INDIA_VIX__'; return df[['symbol','date','open','high','low','close','prev_close','change','pct_change','signal_time','asof_time']]


def normalize_corporate_events(path, asof_col='announcement_time', event_time_col=None):
    df=_read(path); ren={}
    aliases={'symbol':['SYMBOL','Symbol'],'event_type':['PURPOSE','Purpose','SUBJECT','Subject','Event Type'],
             'announcement_time':['Broadcast Date','Announcement Date','ANNOUNCEMENT_DATE','BroadcastDt'],
             'ex_date':['EX-DATE','EX_DATE','Ex-Date'],'record_date':['RECORD DATE','RECORD_DATE','Record Date'],
             'event_time':['event_time','EVENT_TIME']}
    for t,cs in aliases.items():
        for c in cs:
            if c in df: ren[c]=t; break
    df=df.rename(columns=ren)
    if 'symbol' not in df or 'event_type' not in df: raise ValueError('corporate event report requires symbol and event_type')
    if 'announcement_time' not in df: raise ValueError('corporate event must contain true announcement/broadcast time')
    raw=df['announcement_time'].astype(str)
    if raw.str.match(r'^\d{1,2}[-/]\d{1,2}[-/]\d{4}$|^\d{4}-\d{2}-\d{2}$').any():
        raise ValueError('corporate events contain date-only announcement times; refusing PIT use without true broadcast/availability timestamp')
    df['announcement_time']=pd.to_datetime(df['announcement_time'],utc=True,errors='coerce')
    if df['announcement_time'].isna().any(): raise ValueError('corporate event has invalid announcement timestamps')
    df['asof_time']=df['announcement_time']; df['signal_time']=df['announcement_time']
    for c in ['ex_date','record_date']:
        if c in df: df[c]=pd.to_datetime(df[c],errors='coerce')
    return df[['symbol','event_type','announcement_time','ex_date','record_date','signal_time','asof_time']].copy()


def normalize_pit_fundamentals(path, asof_col='available_at'):
    df=_read(path)
    if 'symbol' not in df: raise ValueError('fundamentals require symbol')
    if asof_col not in df: raise ValueError(f'fundamentals require true {asof_col} timestamp; refusing date-only fundamentals')
    df['asof_time']=pd.to_datetime(df[asof_col],utc=True,errors='coerce')
    if df['asof_time'].isna().any(): raise ValueError('fundamentals contain invalid availability timestamps')
    if 'period_end' in df: df['period_end']=pd.to_datetime(df['period_end'],errors='coerce')
    return df


def _generic_report(path, aliases, required, numeric=(), date_key='date', asof_time=None):
    df=_read(path); ren={}
    for target, candidates in aliases.items():
        for c in candidates:
            if c in df: ren[c]=target; break
    df=df.rename(columns=ren)
    missing=[c for c in required if c not in df.columns]
    if missing: raise ValueError(f'report missing {missing}')
    df=_num(df,list(numeric)); df=_asof(df,date_key,asof_time)
    return df


def normalize_participant_oi(path, asof_time=None):
    return _generic_report(path, {
        'date':['DATE','Date','TradDt'],'participant':['PARTICIPANT','Participant','Client Type','CLIENT_TYPE'],
        'futures_oi':['FUTURES_OI','Futures OI','Future OI'],'options_oi':['OPTIONS_OI','Options OI'],
        'total_oi':['TOTAL_OI','Total OI'],'oi_change':['OI_CHANGE','Change in OI']},
        ['date','participant'], ['futures_oi','options_oi','total_oi','oi_change'], asof_time=asof_time)


def normalize_fii_derivatives(path, asof_time=None):
    return _generic_report(path, {
        'date':['DATE','Date','TradDt'],'segment':['SEGMENT','Segment'],'buy_value':['BUY_VALUE','Buy Value','BUY VALUE'],
        'sell_value':['SELL_VALUE','Sell Value','SELL VALUE'],'open_interest':['OPEN_INTEREST','Open Interest','OI']},
        ['date'], ['buy_value','sell_value','open_interest'], asof_time=asof_time)


def normalize_daily_volatility(path, asof_time=None):
    return _generic_report(path, {
        'symbol':['SYMBOL','Symbol','TckrSymb'],'date':['DATE','Date','TradDt'],
        'daily_volatility':['DAILY_VOLATILITY','Daily Volatility','Volatility']},
        ['symbol','date','daily_volatility'], ['daily_volatility'], asof_time=asof_time)
