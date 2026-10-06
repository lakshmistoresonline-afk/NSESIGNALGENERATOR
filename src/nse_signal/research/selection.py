"""Selection controls for selective, cost-aware signal publication."""
from __future__ import annotations
import numpy as np


def choose_economic_threshold(y, p, *, reward_multiple=2.0, risk_multiple=1.0,
                              cost_fraction=0.0, thresholds=None, min_coverage=0.05):
    """Choose a probability threshold using validation data only.

    Score is expected value per opportunity after a conservative fixed cost.
    The selected threshold must be frozen before the untouched test/production period.
    """
    y = np.asarray(y, dtype=int)
    p = np.asarray(p, dtype=float)
    thresholds = np.asarray(thresholds if thresholds is not None else np.arange(.55, .951, .01))
    best = None
    for t in thresholds:
        side = np.where(p >= t, 1, np.where(p <= 1-t, -1, 0))
        mask = side != 0
        coverage = float(mask.mean()) if len(mask) else 0.0
        if coverage < min_coverage:
            continue
        wins = np.where(side[mask] == 1, y[mask] == 1, y[mask] == 0)
        payoff = np.where(wins, reward_multiple, -risk_multiple) - float(cost_fraction)
        ev = float(np.mean(payoff))
        row = (ev, coverage, float(t), float(np.mean(wins)))
        if best is None or row[0] > best[0] or (row[0] == best[0] and row[1] > best[1]):
            best = row
    if best is None:
        return {'threshold': .55, 'coverage': 0.0, 'precision': float('nan'), 'expected_value_proxy': float('-inf')}
    return {'threshold': best[2], 'coverage': best[1], 'precision': best[3], 'expected_value_proxy': best[0]}
