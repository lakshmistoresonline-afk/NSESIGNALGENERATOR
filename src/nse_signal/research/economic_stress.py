"""Cost and execution stress tests for signal robustness."""
from __future__ import annotations
import numpy as np


def stress_returns(gross_returns, *, base_cost_bps=40, multipliers=(0.5,1,2,3), turnover=1.0) -> dict:
    r=np.asarray(gross_returns,dtype=float); r=r[np.isfinite(r)]
    out={}
    if not len(r): return out
    for m in multipliers:
        net=r-(base_cost_bps*m/10000.0)*turnover
        mean=float(np.mean(net)); std=float(np.std(net,ddof=1)) if len(net)>1 else float('nan')
        out[f"cost_{m:.1f}x_mean_return"]=mean
        out[f"cost_{m:.1f}x_sharpe"]=(mean/std*np.sqrt(252)) if np.isfinite(std) and std>0 else float('nan')
    return out
