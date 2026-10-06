"""Strict PIT dataset quality gates."""
from __future__ import annotations
import pandas as pd
import numpy as np


def audit_pit_frame(df: pd.DataFrame, *, signal_col='signal_time', asof_col='asof_time', key_cols=None, max_stale_days=None):
    key_cols=key_cols or []
    report={'rows':len(df),'duplicate_keys':0,'invalid_timestamps':0,'future_asof':0,'missing_key':0,'stale_rows':0,'pass':True}
    if signal_col in df and asof_col in df:
        s=pd.to_datetime(df[signal_col],utc=True,errors='coerce'); a=pd.to_datetime(df[asof_col],utc=True,errors='coerce')
        report['invalid_timestamps']=int((s.isna()|a.isna()).sum()); report['future_asof']=int((a>s).sum())
        if max_stale_days is not None: report['stale_rows']=int(((s-a).dt.total_seconds()>max_stale_days*86400).sum())
    if key_cols and all(c in df for c in key_cols): report['duplicate_keys']=int(df.duplicated(key_cols).sum())
    if key_cols: report['missing_key']=int(df[key_cols].isna().any(axis=1).sum())
    report['pass']=all(report[k]==0 for k in ['duplicate_keys','invalid_timestamps','future_asof','missing_key','stale_rows'])
    return report


def dedupe_latest(df, keys, asof_col='asof_time'):
    if not set(keys).issubset(df.columns): raise ValueError(f'missing dedupe keys: {sorted(set(keys)-set(df.columns))}')
    x=df.copy(); x[asof_col]=pd.to_datetime(x[asof_col],utc=True,errors='coerce')
    return x.sort_values(asof_col).drop_duplicates(keys,keep='last').reset_index(drop=True)
