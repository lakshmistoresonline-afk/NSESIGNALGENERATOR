"""Multi-horizon agreement and stability controls."""
from __future__ import annotations
import numpy as np
import pandas as pd


def horizon_agreement(probabilities: pd.DataFrame, *, min_horizons=2, agreement=.60):
    """Return directional agreement across independently OOS horizon models."""
    cols = [c for c in probabilities.columns if c.startswith('p_up_')]
    if not cols:
        return pd.DataFrame(index=probabilities.index, data={'agreement': 0.0, 'direction': 0, 'eligible': False})
    x = probabilities[cols].astype(float)
    votes = np.where(x >= agreement, 1, np.where(x <= 1-agreement, -1, 0))
    nonzero = (votes != 0).sum(axis=1)
    pos = (votes == 1).sum(axis=1); neg = (votes == -1).sum(axis=1)
    direction = np.where(pos > neg, 1, np.where(neg > pos, -1, 0))
    agree = np.maximum(pos, neg) / np.maximum(nonzero, 1)
    eligible = (nonzero >= min_horizons) & (agree >= agreement) & (direction != 0)
    return pd.DataFrame({'agreement': agree.astype(float), 'direction': direction.astype(int), 'eligible': eligible}, index=x.index)
