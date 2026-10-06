"""Cross-sectional signal publication filters (no execution)."""
import numpy as np
import pandas as pd

def filter_signals(df: pd.DataFrame, min_confidence=.55, max_count=10, max_weight=.10,
                   max_sector_weight=.30, max_correlated=3, corr_threshold=.85) -> pd.DataFrame:
    if df.empty: return df.copy()
    x=df[df.confidence>=min_confidence].copy()
    if x.empty: return x
    sort_cols=[c for c in ['quality_score','confidence','factor_score'] if c in x.columns]
    x=x.sort_values(sort_cols,ascending=False).copy()
    # Do not allow highly correlated names to crowd out independent signals.
    if 'correlation_to_selected' in x.columns:
        selected=[]; accepted=[]
        for idx,row in x.iterrows():
            corr=float(row.get('correlation_to_selected',0) or 0)
            if corr < corr_threshold or len(selected) < max_correlated:
                selected.append(idx); accepted.append(idx)
        x=x.loc[accepted]
    x=x.head(max_count).copy()
    x['weight']=min(float(max_weight),1/max(len(x),1))
    if 'sector' in x.columns and len(x):
        cap=max(1,int(max_sector_weight/max(x.weight.iloc[0],1e-9)))
        x=x.groupby('sector',dropna=False,sort=False).head(cap).copy()
    return x
