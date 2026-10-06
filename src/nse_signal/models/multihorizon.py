"""Multi-horizon OOS ensemble. Horizon disagreement is treated as uncertainty."""
from __future__ import annotations
import numpy as np
import pandas as pd
from .walk_forward import walk_forward


def multi_horizon_predictions(df, horizons=(1,3,5,10), min_train=300, step=10, embargo=10):
    results={}
    for h in horizons:
        results[h]=walk_forward(df,min_train=min_train,step=step,horizon=h,embargo=max(embargo,h)).predictions
    joined=[]
    for h,p in results.items():
        z=p[['p_up']].rename(columns={'p_up':f'p_up_{h}'})
        joined.append(z)
    out=pd.concat(joined,axis=1).dropna(how='all')
    cols=[c for c in out.columns if c.startswith('p_up_')]
    out['p_up_mean']=out[cols].mean(axis=1)
    out['horizon_dispersion']=out[cols].std(axis=1).fillna(0.0)
    out['agreement']=1-out['horizon_dispersion']*2
    return out.clip({'agreement':(0,1)})
