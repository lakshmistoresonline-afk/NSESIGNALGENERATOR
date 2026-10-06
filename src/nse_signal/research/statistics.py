import numpy as np
import pandas as pd

def permutation_pvalue(returns: pd.Series, n=1000, seed=42) -> float:
    r = returns.dropna().to_numpy()
    if len(r) < 5:
        return float("nan")
    rng = np.random.default_rng(seed)
    observed = r.mean()
    null = np.empty(n)
    for i in range(n):
        signs = rng.choice([-1, 1], size=len(r))
        null[i] = (r * signs).mean()
    return float((np.abs(null) >= abs(observed)).mean())

def deflated_sharpe_proxy(sharpe: float, trials: int, observations: int) -> float:
    if observations <= 1 or trials <= 1:
        return float(sharpe)
    penalty = np.sqrt(2*np.log(max(trials,2)) / max(observations,2))
    return float(sharpe - penalty)
