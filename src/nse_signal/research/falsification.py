"""Falsification tests for detecting accidental predictability and leakage."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score


def label_permutation_auc(y, p, *, n=200, seed=42) -> dict:
    """Permutation-null AUC distribution; useful for detecting chance-fit claims."""
    y = np.asarray(y, dtype=int); p = np.asarray(p, dtype=float)
    if len(y) != len(p) or len(y) < 10 or len(np.unique(y)) < 2:
        return {"null_mean_auc": float("nan"), "null_p95_auc": float("nan"), "n": 0}
    rng = np.random.default_rng(seed)
    vals=[]
    for _ in range(int(n)):
        vals.append(roc_auc_score(rng.permutation(y), p))
    return {"null_mean_auc": float(np.mean(vals)), "null_p95_auc": float(np.quantile(vals,.95)), "n": int(len(vals))}


def temporal_shift_auc(y, p, *, shifts=(1, 5, 20)) -> dict:
    """AUC after shifting predictions forward; accidental future leakage often survives such tests."""
    y=np.asarray(y,dtype=int); p=np.asarray(p,dtype=float); out={}
    for s in shifts:
        if len(y)<=s or len(np.unique(y[s:]))<2:
            out[f"shift_{s}_auc"] = float("nan")
        else:
            out[f"shift_{s}_auc"] = float(roc_auc_score(y[s:],p[:-s]))
    return out


def feature_leakage_scan(df: pd.DataFrame, *, target_col="target", time_col="timestamp") -> pd.DataFrame:
    """Rank numeric features by correlation with a one-step future target proxy."""
    numeric=df.select_dtypes(include=[np.number]).columns
    rows=[]
    future=df[target_col].shift(-1) if target_col in df else None
    if future is None: return pd.DataFrame(columns=["feature","abs_future_corr"])
    for c in numeric:
        if c==target_col: continue
        z=pd.concat([df[c],future],axis=1).dropna()
        corr=z.iloc[:,0].corr(z.iloc[:,1]) if len(z)>5 else np.nan
        rows.append((c,abs(float(corr)) if pd.notna(corr) else np.nan))
    return pd.DataFrame(rows,columns=["feature","abs_future_corr"]).sort_values("abs_future_corr",ascending=False)
