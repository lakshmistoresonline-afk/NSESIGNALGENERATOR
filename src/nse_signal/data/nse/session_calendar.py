"""NSE equity session/calendar helpers with explicit holiday data.

Unknown holidays are never silently treated as business days in PIT acquisition.
The included 2026 calendar is copied from the official NSE equity holiday schedule;
additional years must be added from the corresponding official NSE schedule before
those years are used for production PIT replay.
"""
from __future__ import annotations
from datetime import date, datetime, time, timedelta
from pathlib import Path
import pandas as pd

IST="Asia/Kolkata"
REGULAR_OPEN=time(9,15); REGULAR_CLOSE=time(15,30); PREOPEN_OPEN=time(9,0); PREOPEN_CLOSE=time(9,15)

def load_holidays(path="data/reference/nse_equity_holidays.csv"):
    p=Path(path)
    if not p.exists(): raise FileNotFoundError(f"Official NSE holiday calendar missing: {p}")
    x=pd.read_csv(p); x['date']=pd.to_datetime(x['date'],errors='raise').dt.date
    return set(x['date'])

def _covered_years(holidays):
    return {d.year for d in holidays}

def assert_calendar_coverage(d, holidays=None):
    holidays=load_holidays() if holidays is None else holidays
    year=pd.Timestamp(d).year
    if year not in _covered_years(holidays):
        raise RuntimeError(f"NSE holiday calendar does not cover {year}; refusing to infer trading-day status")
    return holidays

def is_trading_day(d, holidays=None):
    d=pd.Timestamp(d).date(); holidays=assert_calendar_coverage(d, holidays)
    return d.weekday()<5 and d not in holidays

def next_trading_day(d, holidays=None):
    holidays=load_holidays() if holidays is None else holidays; x=pd.Timestamp(d).date()+timedelta(days=1)
    for _ in range(370):
        if is_trading_day(x,holidays): return x
        x+=timedelta(days=1)
    raise RuntimeError("could not find next trading day")

def previous_trading_day(d, holidays=None):
    holidays=load_holidays() if holidays is None else holidays; x=pd.Timestamp(d).date()-timedelta(days=1)
    for _ in range(370):
        if is_trading_day(x,holidays): return x
        x-=timedelta(days=1)
    raise RuntimeError("could not find previous trading day")

def session_open_utc(d):
    return pd.Timestamp(datetime.combine(pd.Timestamp(d).date(),REGULAR_OPEN),tz=IST).tz_convert('UTC')

def session_close_utc(d):
    return pd.Timestamp(datetime.combine(pd.Timestamp(d).date(),REGULAR_CLOSE),tz=IST).tz_convert('UTC')

def classify(ts, holidays=None):
    t=pd.Timestamp(ts)
    if t.tzinfo is None: t=t.tz_localize(IST)
    local=t.tz_convert(IST); d=local.date()
    if not is_trading_day(d,holidays): return 'HOLIDAY'
    tm=local.time()
    if tm < PREOPEN_OPEN: return 'CLOSED'
    if PREOPEN_OPEN <= tm < PREOPEN_CLOSE: return 'PRE_OPEN'
    if tm <= REGULAR_CLOSE: return 'REGULAR'
    if tm <= time(16,0): return 'POST_CLOSE'
    return 'CLOSED'
