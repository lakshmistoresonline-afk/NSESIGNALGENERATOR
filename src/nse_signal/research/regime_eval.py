"""Regime-conditional evaluation and stability gates."""
from __future__ import annotations
import numpy as np
import pandas as pd


def regime_report(predictions: pd.DataFrame, probability_col='p_up', target_col='target'):
    x=predictions.copy()
    if 'regime' not in x: return {}
    rows={}
    for regime,g in x.groupby('regime'):
        if len(g)<10: continue
        p=g[probability_col].clip(1e-6,1-1e-6); y=g[target_col].astype(int)
        brier=float(np.mean((p-y)**2))
        hit=float(np.mean(np.where(p>=.5,y==1,y==0)))
        rows[str(regime)]={'n':int(len(g)),'brier':brier,'directional_accuracy':hit}
    return rows


def regime_stability_gate(report, max_brier=.26, min_accuracy=.50, min_n=20):
    failures=[]
    for regime,m in report.items():
        if m['n']>=min_n and m['brier']>max_brier: failures.append(f'{regime}:brier')
        if m['n']>=min_n and m['directional_accuracy']<min_accuracy: failures.append(f'{regime}:accuracy')
    return {'pass':not failures,'failures':failures}
