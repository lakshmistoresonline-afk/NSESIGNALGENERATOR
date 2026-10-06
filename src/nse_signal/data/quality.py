"""Market-data integrity checks required before research or publication."""
from __future__ import annotations
import numpy as np
import pandas as pd


def validate_ohlcv(df: pd.DataFrame, max_gap_days=10) -> dict:
    req={'open','high','low','close','volume'}
    missing=sorted(req-set(df.columns))
    x=df.copy().sort_index()
    duplicate_index=int(x.index.duplicated().sum())
    if missing:
        return {
            'missing_columns': missing, 'rows': int(len(x)),
            'duplicate_timestamps': duplicate_index, 'bad_ohlc_rows': 0,
            'nonpositive_price_rows': 0, 'negative_volume_rows': 0,
            'suspicious_calendar_gaps': 0, 'pass': False,
        }
    for c in ['open','high','low','close','volume']:
        x[c]=pd.to_numeric(x[c],errors='coerce')
    bad_ohlc=int(((x.high < x.low) | (x.high < x.open) | (x.high < x.close) | (x.low > x.open) | (x.low > x.close) | x[['open','high','low','close']].isna().any(axis=1)).sum())
    nonpositive=int(((x[['open','high','low','close']]<=0).any(axis=1)).sum())
    negative_volume=int((x.volume<0).sum())
    gaps=x.index.to_series().diff().dt.total_seconds().div(86400).dropna()
    suspicious_gaps=int((gaps>max_gap_days).sum())
    return {
        'missing_columns':missing,'rows':int(len(x)),'duplicate_timestamps':duplicate_index,
        'bad_ohlc_rows':bad_ohlc,'nonpositive_price_rows':nonpositive,'negative_volume_rows':negative_volume,
        'suspicious_calendar_gaps':suspicious_gaps,'pass':not missing and duplicate_index==0 and bad_ohlc==0 and nonpositive==0 and negative_volume==0,
    }


def clean_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    r=validate_ohlcv(df)
    if r['missing_columns']: raise ValueError(f"Missing OHLCV columns: {r['missing_columns']}")
    x=df.copy().sort_index()
    x=x[~x.index.duplicated(keep='last')]
    x=x[(x.high>=x.low)&(x.high>=x.open)&(x.high>=x.close)&(x.low<=x.open)&(x.low<=x.close)]
    x=x[(x[['open','high','low','close']]>0).all(axis=1)&(x.volume>=0)]
    return x
