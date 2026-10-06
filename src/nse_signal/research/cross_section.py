"""Cross-sectional ranking, sector neutrality and optional fundamental context."""
from __future__ import annotations
import numpy as np
import pandas as pd


def winsorize(s, q=.02):
    lo,hi=s.quantile(q),s.quantile(1-q)
    return s.clip(lo,hi)


def rank01(s):
    return s.rank(pct=True, method='average')


def cross_sectional_score(df: pd.DataFrame, positive=None, negative=None) -> pd.DataFrame:
    x=df.copy()
    positive=positive or ['return_20d','return_60d','relative_strength_nifty','relative_strength_sector']
    negative=negative or ['realized_vol_20','beta_60']
    parts=[]
    for c in positive:
        if c in x: parts.append(rank01(winsorize(x[c])).rename(c))
    for c in negative:
        if c in x: parts.append((1-rank01(winsorize(x[c]))).rename(c))
    if parts:
        z=pd.concat(parts,axis=1)
        x['cross_sectional_score']=z.mean(axis=1)
    else:
        x['cross_sectional_score']=.5
    if 'sector' in x.columns:
        x['sector_rank']=x.groupby('sector')['cross_sectional_score'].rank(pct=True)
        x['sector_neutral_score']=x['sector_rank']
    else:
        x['sector_neutral_score']=x.cross_sectional_score
    return x
