"""Robustness checks for publication thresholds."""
from __future__ import annotations
import numpy as np


def threshold_stability(y, p, center, *, radius=.03, step=.01, min_coverage=.05):
    y=np.asarray(y,dtype=int); p=np.asarray(p,dtype=float)
    ts=np.arange(max(.5,center-radius), min(.99,center+radius)+1e-12, step)
    rows=[]
    for t in ts:
        side=np.where(p>=t,1,np.where(p<=1-t,-1,0)); m=side!=0
        if m.mean() < min_coverage: continue
        acc=np.mean(np.where(side[m]==1,y[m]==1,y[m]==0))
        rows.append((float(t),float(acc),float(m.mean())))
    if not rows: return {'pass':False,'stable_share':0.0,'min_accuracy':np.nan,'max_accuracy':np.nan,'thresholds_tested':0}
    acc=np.array([r[1] for r in rows])
    return {'pass':bool((acc>=max(.5,acc.mean()-.02)).mean()>=.60), 'stable_share':float((acc>=max(.5,acc.mean()-.02)).mean()), 'min_accuracy':float(acc.min()), 'max_accuracy':float(acc.max()), 'thresholds_tested':len(rows)}
