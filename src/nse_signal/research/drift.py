"""Feature-distribution drift diagnostics."""
from __future__ import annotations
import numpy as np
import pandas as pd


def psi(reference, current, bins=10):
    a=pd.Series(reference,dtype=float).replace([np.inf,-np.inf],np.nan).dropna()
    b=pd.Series(current,dtype=float).replace([np.inf,-np.inf],np.nan).dropna()
    if len(a)<30 or len(b)<10: return np.nan
    edges=np.unique(np.quantile(a,np.linspace(0,1,bins+1)))
    if len(edges)<3: return 0.0
    edges[0],edges[-1]=-np.inf,np.inf
    pa=np.histogram(a,bins=edges)[0].astype(float); pb=np.histogram(b,bins=edges)[0].astype(float)
    pa=(pa+.5)/(pa.sum()+.5*len(pa)); pb=(pb+.5)/(pb.sum()+.5*len(pb))
    return float(np.sum((pb-pa)*np.log(pb/pa)))


def frame_psi(reference: pd.DataFrame, current: pd.DataFrame, columns=None):
    columns=columns or [c for c in reference.columns if c in current.columns]
    out={c:psi(reference[c],current[c]) for c in columns}
    vals=[v for v in out.values() if np.isfinite(v)]
    return {'per_feature':out,'max_psi':float(max(vals)) if vals else 0.0,'median_psi':float(np.median(vals)) if vals else 0.0}
