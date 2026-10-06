"""Additional accuracy controls: CPCV, conformal abstention, drift and stability."""
from __future__ import annotations
import itertools
import numpy as np
import pandas as pd


def combinatorial_purged_splits(n_samples: int, n_groups: int = 6, test_groups: int = 2,
                                purge: int = 0, embargo: int = 0):
    """Yield train/test indices for CPCV-style group combinations.

    Groups are contiguous and time ordered. Purge removes observations immediately
    before/after test blocks; embargo removes observations immediately after test.
    This is a practical CPCV splitter for event-labelled financial samples.
    """
    if n_samples < 2 or n_groups < 2 or not (1 <= test_groups < n_groups):
        raise ValueError("invalid CPCV configuration")
    groups = np.array_split(np.arange(n_samples), n_groups)
    all_idx = np.arange(n_samples)
    for combo in itertools.combinations(range(n_groups), test_groups):
        test = np.concatenate([groups[g] for g in combo])
        blocked = set(test.tolist())
        for g in combo:
            if purge:
                lo = max(0, int(groups[g][0]) - purge)
                hi = min(n_samples, int(groups[g][-1]) + purge + 1)
                blocked.update(range(lo, hi))
            if embargo:
                lo = int(groups[g][-1]) + 1
                hi = min(n_samples, lo + embargo)
                blocked.update(range(lo, hi))
        train = np.array([i for i in all_idx if i not in blocked], dtype=int)
        yield train, np.sort(test)


def conformal_classification(p_cal, y_cal, p_test, alpha=.10):
    """Split-conformal binary prediction sets using class-conditional p-values.

    For each candidate class c, the nonconformity score is 1-P(Y=c|X).
    A class is included when its finite-sample conformal p-value exceeds alpha.
    The predictor abstains unless exactly one class is retained. Calibration
    observations must be strictly earlier than the predictions being tested.
    """
    p_cal=np.asarray(p_cal,dtype=float); y_cal=np.asarray(y_cal,dtype=int)
    p_test=np.asarray(p_test,dtype=float)
    if len(p_cal) < 20 or len(np.unique(y_cal)) < 2:
        lo=np.zeros(len(p_test)); hi=np.ones(len(p_test)); abst=np.ones(len(p_test),dtype=bool)
        return pd.DataFrame({'set_low':lo,'set_high':hi,'abstain':abst,'conformal_confidence':0.0,
                             'p_value_0':np.zeros(len(p_test)),'p_value_1':np.zeros(len(p_test))})
    p_cal=np.clip(p_cal,1e-6,1-1e-6); p_test=np.clip(p_test,1e-6,1-1e-6)
    scores0=1-p_cal[y_cal==0]
    scores1=p_cal[y_cal==1]
    def class_pvalues(scores, prob):
        if len(scores)==0:
            return np.zeros(len(prob))
        test_score=1-prob
        # Conservative finite-sample split-conformal p-value.
        return (1.0 + np.sum(scores[:,None] >= test_score[None,:],axis=0))/(len(scores)+1.0)
    pv0=class_pvalues(scores0,p_test)
    pv1=class_pvalues(scores1,1-p_test)
    include0=pv0>float(alpha)
    include1=pv1>float(alpha)
    abstain=(include0.astype(int)+include1.astype(int))!=1
    conf=np.where(abstain,0.0,np.maximum(pv0,pv1))
    return pd.DataFrame({'set_low':include0.astype(int),'set_high':include1.astype(int),
                         'abstain':abstain,'conformal_confidence':conf,
                         'p_value_0':pv0,'p_value_1':pv1})


def population_stability_index(reference, current, bins=10):
    """PSI for drift monitoring. Values near 0 imply little distribution drift."""
    a=pd.Series(reference).dropna().astype(float); b=pd.Series(current).dropna().astype(float)
    if len(a)<20 or len(b)<20: return float('nan')
    edges=np.unique(np.quantile(a,np.linspace(0,1,bins+1)))
    if len(edges)<3: return 0.0
    edges[0],edges[-1]=-np.inf,np.inf
    pa=np.histogram(a,edges)[0]/len(a); pb=np.histogram(b,edges)[0]/len(b)
    pa=np.clip(pa,1e-6,None); pb=np.clip(pb,1e-6,None)
    return float(np.sum((pb-pa)*np.log(pb/pa)))


def feature_stability_by_fold(fold_feature_sets):
    """Frequency a feature survives fold-local selection."""
    sets=[set(s) for s in fold_feature_sets if s]
    if not sets: return pd.Series(dtype=float)
    counts={f:sum(f in s for s in sets) for f in sorted(set().union(*sets))}
    return pd.Series({k:v/len(sets) for k,v in counts.items()}).sort_values(ascending=False)


def threshold_from_validation(y, p, min_threshold=.55, max_threshold=.95, min_coverage=.05):
    """Choose a publication threshold on validation data only, maximizing net hit-rate proxy.
    Ties prefer lower threshold; caller must keep this threshold frozen for test/live use.
    """
    y=np.asarray(y,dtype=int); p=np.asarray(p,dtype=float)
    best=float(min_threshold); best_score=-np.inf
    for t in np.arange(min_threshold,max_threshold+1e-9,.01):
        side=np.where(p>=t,1,np.where(p<=1-t,-1,0)); mask=side!=0
        if mask.mean()<min_coverage: continue
        acc=np.mean(np.where(side[mask]==1,y[mask]==1,y[mask]==0))
        score=float(acc)*float(mask.mean())
        if score>best_score: best_score=score; best=float(t)
    return best


def combinatorial_purged_panel_splits(timestamps, n_groups=6, test_groups=2, purge=10, embargo=10):
    """Timestamp-grouped CPCV for multi-security panels; never splits rows of one timestamp."""
    import pandas as pd
    from .validation import combinatorial_purged_panel_splits as _split
    return _split(timestamps, n_groups=n_groups, test_groups=test_groups,
                  purge_bars=purge, embargo_bars=embargo)
