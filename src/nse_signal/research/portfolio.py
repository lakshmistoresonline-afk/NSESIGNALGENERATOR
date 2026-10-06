"""Cross-sectional signal portfolio constraints; signal-only, no execution."""
from __future__ import annotations
import numpy as np
import pandas as pd


def rank_signals(df, score_col='quality_score', max_names=10, max_single_name=.10, max_sector=.30):
    x=df.copy()
    if x.empty: return x
    x=x.sort_values(score_col,ascending=False).copy()
    x['weight']=np.minimum(max_single_name,1.0/max(1,min(max_names,len(x))))
    if 'sector' in x:
        sector_weight=x.groupby('sector')['weight'].transform('sum')
        scale=np.minimum(1.0, max_sector/sector_weight.replace(0,np.nan)).fillna(1.0)
        x['weight']*=scale
    total=x.weight.sum()
    if total>0: x['weight']/=total
    return x.head(max_names)


def concentration_metrics(weights):
    w=pd.Series(weights,dtype=float).dropna()
    if w.empty:return {'hhi':0.0,'effective_names':0.0,'max_weight':0.0}
    hhi=float((w**2).sum())
    return {'hhi':hhi,'effective_names':float(1/hhi) if hhi>0 else 0.0,'max_weight':float(w.max())}
