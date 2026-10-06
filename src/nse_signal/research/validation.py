"""Dependence-aware validation and multiple-testing controls."""
from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class CPCVSplit:
    train: np.ndarray
    test: np.ndarray


def combinatorial_purged_splits(n_samples: int, n_groups: int = 6, test_groups: int = 2,
                                 purge_bars: int = 10, embargo_bars: int = 10) -> list[CPCVSplit]:
    """Generate CPCV splits with a time purge around every test block.

    Groups are contiguous and chronological. Purging is performed by index,
    making the splitter independent of the feature/model implementation.
    """
    if n_samples <= 0 or n_groups < 2 or not 1 <= test_groups < n_groups:
        raise ValueError("invalid CPCV dimensions")
    if purge_bars < 0 or embargo_bars < 0:
        raise ValueError("purge/embargo must be non-negative")
    groups = [g for g in np.array_split(np.arange(n_samples), n_groups) if len(g)]
    out: list[CPCVSplit] = []
    for chosen in combinations(range(len(groups)), test_groups):
        test = np.concatenate([groups[g] for g in chosen])
        test_mask = np.zeros(n_samples, dtype=bool)
        test_mask[test] = True
        blocked = test_mask.copy()
        for g in chosen:
            lo, hi = int(groups[g][0]), int(groups[g][-1])
            a = max(0, lo - purge_bars)
            b = min(n_samples, hi + 1 + purge_bars)
            blocked[a:b] = True
            # Embargo is applied after each test block as an additional future buffer.
            e0 = min(n_samples, hi + 1 + purge_bars)
            e1 = min(n_samples, e0 + embargo_bars)
            blocked[e0:e1] = True
        train = np.flatnonzero(~blocked)
        if len(train) and len(test):
            out.append(CPCVSplit(train=train, test=np.sort(test)))
    return out


def pbo_from_paths(in_sample_scores: np.ndarray, out_sample_scores: np.ndarray) -> float:
    """Estimate PBO from paired IS/OOS candidate score matrices.

    Rows are validation paths and columns are candidate models/parameter sets.
    For each path, the in-sample winner is located and its OOS percentile rank
    is measured. PBO is the fraction of paths where that winner falls below
    the OOS median.
    """
    ins = np.asarray(in_sample_scores, dtype=float)
    oos = np.asarray(out_sample_scores, dtype=float)
    if ins.ndim != 2 or oos.shape != ins.shape or min(ins.shape) < 2:
        raise ValueError("IS/OOS score matrices must have the same 2-D shape")
    bad = []
    for i in range(ins.shape[0]):
        if np.all(~np.isfinite(ins[i])) or np.all(~np.isfinite(oos[i])):
            continue
        winner = int(np.nanargmax(ins[i]))
        vals = oos[i][np.isfinite(oos[i])]
        if not np.isfinite(oos[i, winner]):
            continue
        bad.append(float(oos[i, winner] < np.nanmedian(vals)))
    return float(np.mean(bad)) if bad else float("nan")


def multiple_testing_summary(observed_sharpe: float, trial_sharpes: list[float] | np.ndarray) -> dict:
    """Selection-aware summary for a finite trial registry."""
    vals = np.asarray(trial_sharpes, dtype=float)
    vals = vals[np.isfinite(vals)]
    if not len(vals) or not np.isfinite(observed_sharpe):
        return {"trials": int(len(vals)), "best_sharpe": float("nan"), "rank_percentile": float("nan"), "selection_adjusted": False}
    rank = float(np.mean(vals <= observed_sharpe))
    return {"trials": int(len(vals)), "best_sharpe": float(np.max(vals)), "rank_percentile": rank, "selection_adjusted": len(vals) > 1}


def combinatorial_purged_panel_splits(timestamps, n_groups: int = 6, test_groups: int = 2,
                                     purge_bars: int = 10, embargo_bars: int = 10) -> list[CPCVSplit]:
    """CPCV over unique timestamps, returning row positions for a panel.

    Never split individual securities into train/test by row number. All
    securities at a timestamp belong to the same temporal fold.
    """
    ts=pd.Series(pd.to_datetime(timestamps,utc=True,errors='coerce'))
    if ts.isna().any():
        raise ValueError('timestamps contain invalid values')
    unique=np.array(sorted(ts.unique()))
    base=combinatorial_purged_splits(len(unique),n_groups,test_groups,purge_bars,embargo_bars)
    out=[]
    arr=ts.to_numpy()
    for sp in base:
        train_times=set(unique[sp.train]); test_times=set(unique[sp.test])
        train=np.flatnonzero(np.isin(arr,list(train_times)))
        test=np.flatnonzero(np.isin(arr,list(test_times)))
        if len(train) and len(test):
            out.append(CPCVSplit(train=train,test=test))
    return out
