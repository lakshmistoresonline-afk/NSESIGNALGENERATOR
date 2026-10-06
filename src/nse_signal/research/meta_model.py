"""Meta-label gate for primary OOS predictions.

The meta model answers a narrower question: given an already-generated primary
prediction, should it be published? It must be trained only on genuinely OOS
primary predictions to avoid stacking leakage.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline


def meta_features(predictions: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "p_up", "model_dispersion", "conformal_confidence", "horizon_dispersion",
        "signal_stability", "expected_cost_bps", "atr_pct", "volume_ratio",
    ]
    out = pd.DataFrame(index=predictions.index)
    for c in cols:
        out[c] = predictions[c] if c in predictions else 0.0
    out["primary_confidence"] = (2 * (out["p_up"] - 0.5).abs()).clip(0, 1)
    return out.replace([np.inf, -np.inf], np.nan).fillna(0.0)


def fit_meta_gate(oos_predictions: pd.DataFrame, target_col: str = "meta_target", min_rows: int = 80):
    """Fit a calibration-style meta gate from OOS primary predictions only."""
    if target_col not in oos_predictions:
        raise ValueError(f"missing {target_col}")
    x=meta_features(oos_predictions)
    y=oos_predictions[target_col].astype(int)
    if len(x) < min_rows or y.nunique() < 2:
        raise ValueError("insufficient meta-label observations")
    model=make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced", C=.5))
    model.fit(x, y)
    return model


def meta_probability(model, predictions: pd.DataFrame) -> np.ndarray:
    return model.predict_proba(meta_features(predictions))[:,1]
