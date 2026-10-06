"""Point-in-time/as-of data provenance checks."""
from __future__ import annotations
import pandas as pd


def validate_asof_data(df: pd.DataFrame, signal_time_col='signal_time', asof_col='asof_time') -> dict:
    """Ensure provider observations were available no later than the signal timestamp."""
    if signal_time_col not in df.columns or asof_col not in df.columns:
        return {'pass': False, 'reason': 'missing_asof_columns', 'violations': len(df)}
    s=pd.to_datetime(df[signal_time_col],utc=True,errors='coerce')
    a=pd.to_datetime(df[asof_col],utc=True,errors='coerce')
    bad=(s.isna()|a.isna()|(a>s))
    return {'pass': not bool(bad.any()), 'violations': int(bad.sum()), 'rows': int(len(df))}


def merge_point_in_time(left: pd.DataFrame, right: pd.DataFrame, left_time='signal_time', right_time='asof_time', by=None):
    """Backward as-of merge. Future observations can never satisfy the join."""
    l=left.copy(); r=right.copy()
    l[left_time]=pd.to_datetime(l[left_time],utc=True)
    r[right_time]=pd.to_datetime(r[right_time],utc=True)
    l=l.sort_values(left_time); r=r.sort_values(right_time)
    return pd.merge_asof(l,r,left_on=left_time,right_on=right_time,by=by,direction='backward',allow_exact_matches=True)
