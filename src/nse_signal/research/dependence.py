"""Dependence-aware uncertainty estimates for financial time series."""
from __future__ import annotations
import numpy as np


def stationary_block_bootstrap(values, block_length=10, n_boot=2000, seed=42):
    """Circular moving-block bootstrap preserving short-range dependence."""
    x=np.asarray(values,dtype=float); x=x[np.isfinite(x)]
    if len(x)<2: return np.array([])
    rng=np.random.default_rng(seed); n=len(x); L=max(1,min(int(block_length),n))
    out=np.empty((n_boot,n),dtype=float)
    starts=rng.integers(0,n,size=(n_boot,int(np.ceil(n/L))))
    for b in range(n_boot):
        arr=[]
        for s in starts[b]: arr.extend(x[(s+np.arange(L))%n].tolist())
        out[b]=np.asarray(arr[:n])
    return out


def bootstrap_mean_ci(values, block_length=10, n_boot=2000, alpha=.05, seed=42):
    x=np.asarray(values,dtype=float); x=x[np.isfinite(x)]
    if len(x)<10: return {'mean':float(np.mean(x)) if len(x) else float('nan'),'lower':float('nan'),'upper':float('nan'),'n':len(x)}
    boots=stationary_block_bootstrap(x,block_length,n_boot,seed).mean(axis=1)
    lo,hi=np.quantile(boots,[alpha/2,1-alpha/2])
    return {'mean':float(x.mean()),'lower':float(lo),'upper':float(hi),'n':int(len(x))}
