"""Time-ordered probability calibration and selective prediction."""
from __future__ import annotations
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss


class TimeOrderedCalibrator:
    def __init__(self, min_calibration=50):
        self.min_calibration = int(min_calibration)
        self.model = LogisticRegression(solver="lbfgs")
        self.fitted = False

    def fit(self, raw_probability, y):
        p = np.clip(np.asarray(raw_probability, dtype=float), 1e-6, 1 - 1e-6)
        z = np.log(p / (1 - p)).reshape(-1, 1)
        y = np.asarray(y, dtype=int)
        if len(y) < self.min_calibration or len(np.unique(y)) < 2:
            self.fitted = False
            return self
        self.model.fit(z, y)
        self.fitted = True
        return self

    def predict(self, raw_probability):
        p = np.clip(np.asarray(raw_probability, dtype=float), 1e-6, 1 - 1e-6)
        if not self.fitted:
            return p
        z = np.log(p / (1 - p)).reshape(-1, 1)
        return self.model.predict_proba(z)[:, 1]


def calibration_metrics(y, p):
    y = np.asarray(y, dtype=int)
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    return {
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
        "mean_confidence": float(np.mean(np.maximum(p, 1-p))),
    }


def selective_threshold(p, minimum=0.55, target_coverage=0.20):
    p = np.asarray(p, dtype=float)
    confidence = np.maximum(p, 1-p)
    q = float(np.quantile(confidence, max(0.0, min(1.0, 1-target_coverage)))) if len(p) else minimum
    return max(float(minimum), q)


def calibration_curve_metrics(y, p, bins=10):
    """ECE, maximum calibration error, and calibration slope/intercept diagnostics."""
    from sklearn.linear_model import LogisticRegression
    y=np.asarray(y,dtype=int); p=np.clip(np.asarray(p,dtype=float),1e-6,1-1e-6)
    edges=np.linspace(0,1,bins+1); ece=0.0; mce=0.0
    for lo,hi in zip(edges[:-1],edges[1:]):
        mask=(p>=lo)&(p<hi if hi<1 else p<=hi)
        if not mask.any(): continue
        gap=abs(float(y[mask].mean())-float(p[mask].mean()))
        ece += float(mask.mean())*gap; mce=max(mce,gap)
    z=np.log(p/(1-p)).reshape(-1,1)
    slope=intercept=float('nan')
    if len(y)>=20 and len(np.unique(y))==2:
        lr=LogisticRegression(solver='lbfgs').fit(z,y)
        slope=float(lr.coef_[0,0]); intercept=float(lr.intercept_[0])
    return {"ece":float(ece),"mce":float(mce),"calibration_slope":slope,"calibration_intercept":intercept}
