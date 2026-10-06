"""Economic and statistical validation metrics."""
from __future__ import annotations
import math
import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis, norm
from .bootstrap import block_bootstrap_ci


def sharpe_ratio(r: pd.Series, annualization=252) -> float:
    x = pd.Series(r).dropna().astype(float)
    if len(x) < 2 or x.std(ddof=1) == 0: return 0.0
    return float(np.sqrt(annualization) * x.mean() / x.std(ddof=1))


def sortino_ratio(r: pd.Series, annualization=252) -> float:
    x = pd.Series(r).dropna().astype(float)
    downside = np.minimum(x, 0.0)
    dd = np.sqrt(np.mean(downside ** 2))
    return float(np.sqrt(annualization) * x.mean() / dd) if dd > 0 else 0.0


def profit_factor(r: pd.Series) -> float:
    x = pd.Series(r).dropna()
    gains, losses = x[x > 0].sum(), -x[x < 0].sum()
    return float(gains / losses) if losses > 0 else float("inf") if gains > 0 else 0.0


def deflated_sharpe_ratio(sharpe, trials, observations, skewness=0.0, excess_kurtosis=0.0, annualization=252):
    """Approximate DSR z-score, explicitly labelled as an approximation.

    It adjusts the observed Sharpe for non-normality and multiple trials.
    A full DSR should use the exact expected maximum Sharpe under the search design.
    """
    n = max(int(observations), 2)
    sr = float(sharpe)
    se = math.sqrt(max(1e-12, (1 - skewness * sr + (excess_kurtosis / 4) * sr * sr) / n))
    # Conservative Gaussian approximation for the expected maximum of trials.
    m = max(int(trials), 1)
    if m == 1:
        sr_star = 0.0
    else:
        q = norm.ppf(max(1e-9, 1 - 1 / m))
        sr_star = q * se
    return float((sr - sr_star) / se)


def expected_max_standard_normal(trials: int) -> float:
    """Numerically compute E[max(Z_1,...,Z_n)] for iid standard normals.

    This is the selection term used by the exact finite-trial DSR diagnostic.
    It is intentionally numerical rather than a ppf shortcut.
    """
    from scipy.integrate import quad
    n = max(int(trials), 1)
    if n == 1:
        return 0.0
    # E[M_n] = integral x * n*phi(x)*Phi(x)^(n-1) dx over R.
    f = lambda x: x * n * norm.pdf(x) * (norm.cdf(x) ** (n - 1))
    val, _ = quad(f, -8.0, 8.0, epsabs=1e-9, epsrel=1e-8, limit=200)
    return float(val)


def deflated_sharpe_ratio_exact(sharpe, trials, observations, skewness=0.0, excess_kurtosis=0.0):
    """Finite-trial DSR z-statistic using a numerical expected-maximum term."""
    n = max(int(observations), 2)
    sr = float(sharpe)
    se = math.sqrt(max(1e-12, (1 - skewness * sr + (excess_kurtosis / 4) * sr * sr) / n))
    selection = expected_max_standard_normal(max(int(trials), 1)) * se
    return float((sr - selection) / se)


def probabilistic_sharpe_ratio(sharpe, benchmark=0.0, observations=2, skewness=0.0, excess_kurtosis=0.0):
    n = max(int(observations), 2)
    se = math.sqrt(max(1e-12, (1 - skewness * sharpe + (excess_kurtosis / 4) * sharpe**2) / n))
    return float(norm.cdf((sharpe - benchmark) / se))


def bootstrap_ci(r: pd.Series, metric="mean", n=2000, seed=42):
    x = pd.Series(r).dropna().to_numpy(float)
    if len(x) < 5: return {"lower": np.nan, "upper": np.nan}
    rng = np.random.default_rng(seed)
    samples = rng.choice(x, size=(n, len(x)), replace=True)
    vals = samples.mean(axis=1) if metric == "mean" else np.median(samples, axis=1)
    return {"lower": float(np.quantile(vals, .025)), "upper": float(np.quantile(vals, .975))}


def performance_report(r: pd.Series, annualization=252, trials=1) -> dict:
    x = pd.Series(r).dropna().astype(float)
    equity = (1+x).cumprod()
    dd = equity / equity.cummax() - 1 if len(equity) else pd.Series(dtype=float)
    sr = sharpe_ratio(x, annualization)
    sk = float(skew(x)) if len(x) > 2 else 0.0
    exk = float(kurtosis(x, fisher=True)) if len(x) > 3 else 0.0
    return {
        "observations": int(len(x)),
        "total_return": float(equity.iloc[-1]-1) if len(equity) else 0.0,
        "annualized_sharpe": sr,
        "sortino": sortino_ratio(x, annualization),
        "profit_factor": profit_factor(x),
        "win_rate": float((x > 0).mean()) if len(x) else 0.0,
        "max_drawdown": float(dd.min()) if len(dd) else 0.0,
        "skew": sk,
        "excess_kurtosis": exk,
        "psr": probabilistic_sharpe_ratio(sr, 0.0, len(x), sk, exk),
        "dsr_z_approx": deflated_sharpe_ratio(sr, trials, len(x), sk, exk),
        "dsr_stat": deflated_sharpe_ratio_exact(sr, trials, len(x), sk, exk),
        "dsr_method": "finite_trial_expected_max_normal_numerical",
        "bootstrap_mean_ci": bootstrap_ci(x, "mean"),
        "block_bootstrap_mean_ci": block_bootstrap_ci(x, "mean", n=2000, block_length=10, alpha=.05, seed=42),
    }
