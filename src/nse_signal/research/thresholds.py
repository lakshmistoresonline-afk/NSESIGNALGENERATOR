"""Validation-only threshold selection and signal abstention."""
from __future__ import annotations
import numpy as np


def choose_threshold(y, p, thresholds=None, min_coverage=.05):
    y=np.asarray(y,dtype=int); p=np.asarray(p,dtype=float)
    thresholds=np.asarray(thresholds if thresholds is not None else np.arange(.55,.951,.01))
    best=None
    for t in thresholds:
        side=np.where(p>=t,1,np.where(p<=1-t,-1,0)); mask=side!=0
        if mask.mean()<min_coverage: continue
        acc=np.mean(np.where(side[mask]==1,y[mask]==1,y[mask]==0))
        score=float(acc*mask.mean())
        row=(score,float(t),float(mask.mean()),float(acc))
        if best is None or row[0]>best[0]: best=row
    return {'threshold':best[1],'coverage':best[2],'selective_accuracy':best[3],'score':best[0]} if best else {'threshold':.55,'coverage':0.0,'selective_accuracy':float('nan'),'score':float('-inf')}
