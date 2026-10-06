"""Leakage-aware event uniqueness and sample weighting."""
from __future__ import annotations
import numpy as np
import pandas as pd


def average_uniqueness(event_start: pd.DatetimeIndex, event_end: pd.DatetimeIndex) -> pd.Series:
    if len(event_start) != len(event_end):
        raise ValueError("event_start and event_end must have equal length")
    if len(event_start) == 0:
        return pd.Series(dtype=float)
    starts = pd.DatetimeIndex(event_start)
    ends = pd.DatetimeIndex(event_end)
    timeline = pd.date_range(min(starts.min(), ends.min()), max(starts.max(), ends.max()), freq='D')
    concurrency = pd.Series(0.0, index=timeline)
    masks = []
    for s, e in zip(starts, ends):
        mask = (timeline >= s) & (timeline <= e)
        concurrency.loc[mask] += 1.0
        masks.append(mask)
    weights = []
    for mask in masks:
        c = concurrency.loc[mask]
        weights.append(float((1.0 / c).mean()) if len(c) else 0.0)
    return pd.Series(weights, index=event_start)


def horizon_uniqueness(index, horizon: int) -> pd.Series:
    """Fast bar-based uniqueness for equally spaced labels.

    For a horizon-H label at t, the event occupies [t, t+H].
    Each sample receives the mean inverse concurrency over that interval.
    """
    n = len(index)
    if n == 0:
        return pd.Series(dtype=float, index=index)
    h = max(1, int(horizon))
    diff = np.zeros(n + h + 2, dtype=float)
    end = np.minimum(np.arange(n) + h, n - 1)
    diff[np.arange(n)] += 1.0
    diff[end + 1] -= 1.0
    concurrency = np.cumsum(diff)[:n]
    inv = np.divide(1.0, concurrency, out=np.zeros_like(concurrency), where=concurrency > 0)
    prefix = np.concatenate([[0.0], np.cumsum(inv)])
    weights = np.array([(prefix[e + 1] - prefix[i]) / (e - i + 1) for i, e in enumerate(end)])
    return pd.Series(weights, index=index)
