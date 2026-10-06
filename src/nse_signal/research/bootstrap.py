"""Dependence-aware bootstrap utilities for financial return series."""
from __future__ import annotations
import numpy as np
import pandas as pd


def stationary_block_bootstrap(x, *, n=2000, block_length=10, seed=42):
    x = np.asarray(pd.Series(x).dropna(), dtype=float)
    if len(x) < 5:
        return np.empty((0, 0))
    rng = np.random.default_rng(seed)
    out = np.empty((n, len(x)), dtype=float)
    p = 1.0 / max(int(block_length), 1)
    for b in range(n):
        j = 0
        while j < len(x):
            start = int(rng.integers(0, len(x)))
            length = int(rng.geometric(p))
            take = min(length, len(x) - j)
            idx = (start + np.arange(take)) % len(x)
            out[b, j:j+take] = x[idx]
            j += take
    return out


def block_bootstrap_ci(x, metric='mean', n=2000, block_length=10, alpha=.05, seed=42):
    x = pd.Series(x).dropna().astype(float).to_numpy()
    if len(x) < 5:
        return {'lower': np.nan, 'upper': np.nan}
    samples = stationary_block_bootstrap(x, n=n, block_length=block_length, seed=seed)
    vals = samples.mean(axis=1) if metric == 'mean' else np.median(samples, axis=1)
    return {'lower': float(np.quantile(vals, alpha/2)), 'upper': float(np.quantile(vals, 1-alpha/2))}
