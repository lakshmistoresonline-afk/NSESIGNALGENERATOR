"""Adversarial validation and distribution-shift diagnostics."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score


def adversarial_validation(reference: pd.DataFrame, current: pd.DataFrame, columns=None, random_state=42):
    """Train a classifier to distinguish reference from current observations.

    AUC near 0.5 suggests similar distributions; high AUC indicates that the
    current population is distinguishable from the research population.
    Splitting is deterministic and uses no labels from the trading problem.
    """
    ref=pd.DataFrame(reference).copy(); cur=pd.DataFrame(current).copy()
    cols=list(columns) if columns is not None else [c for c in ref.columns if c in cur.columns]
    usable=[]
    for c in cols:
        a=pd.to_numeric(ref[c],errors='coerce'); b=pd.to_numeric(cur[c],errors='coerce')
        if a.notna().mean()>=.80 and b.notna().mean()>=.80 and a.nunique()>2 and b.nunique()>2:
            usable.append(c)
    if len(usable)<2 or len(ref)<30 or len(cur)<30:
        return {'auc':float('nan'),'features':usable,'drifted':False,'reason':'insufficient_data'}
    a=ref[usable].replace([np.inf,-np.inf],np.nan); b=cur[usable].replace([np.inf,-np.inf],np.nan)
    med=a.median(); a=a.fillna(med); b=b.fillna(med)
    X=pd.concat([a,b],axis=0); y=np.r_[np.zeros(len(a),dtype=int),np.ones(len(b),dtype=int)]
    # deterministic chronological split within each population
    cut_a=max(1,int(len(a)*.75)); cut_b=max(1,int(len(b)*.75))
    train_idx=np.r_[np.arange(cut_a),len(a)+np.arange(cut_b)]
    test_idx=np.r_[np.arange(cut_a,len(a)),len(a)+np.arange(cut_b,len(b))]
    if len(np.unique(y[train_idx]))<2 or len(test_idx)<10:
        return {'auc':float('nan'),'features':usable,'drifted':False,'reason':'insufficient_split'}
    model=HistGradientBoostingClassifier(max_depth=3,max_iter=100,learning_rate=.05,l2_regularization=1.0,random_state=random_state)
    model.fit(X.iloc[train_idx],y[train_idx]); p=model.predict_proba(X.iloc[test_idx])[:,1]
    auc=float(roc_auc_score(y[test_idx],p))
    return {'auc':auc,'features':usable,'drifted':bool(auc>=.65),'reason':'adversarial_auc'}
