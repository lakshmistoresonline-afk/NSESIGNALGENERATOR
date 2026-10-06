"""Regime-conditional publication controls."""
from __future__ import annotations
import numpy as np
import pandas as pd


def conditional_signal_report(predictions: pd.DataFrame, threshold=.60, min_n=30):
    """Evaluate selective signal behavior by regime and volatility bucket."""
    x=predictions.copy()
    p=x.p_up.clip(1e-6,1-1e-6); y=x.target.astype(int)
    x['_side']=np.where(p>=threshold,1,np.where(p<=1-threshold,-1,0))
    x['_correct']=np.where(x['_side']==1,y==1,np.where(x['_side']==-1,y==0,np.nan))
    groups=[]
    if 'regime' in x: groups.append(('regime',x['regime']))
    if 'atr_pct' in x:
        groups.append(('volatility_bucket',pd.qcut(x['atr_pct'],q=3,duplicates='drop').astype(str)))
    result={}
    for name,grp in groups:
        result[name]={}
        for key,g in x.groupby(grp,dropna=False):
            sig=g[g['_side']!=0]
            if len(sig)<min_n: continue
            result[name][str(key)]={'n':int(len(sig)),'coverage':float(len(sig)/len(g)),'precision':float(np.nanmean(sig['_correct'])),'mean_probability':float(np.mean(np.maximum(sig.p_up,1-sig.p_up)))}
    return result


def regime_stability_penalty(report, min_precision=.50, min_n=30):
    failures=[]
    for family,rows in report.items():
        for name,m in rows.items():
            if m['n']>=min_n and m['precision']<min_precision:
                failures.append(f'{family}:{name}:precision')
    return {'pass':not failures,'failures':failures}
