"""End-to-end research evaluation and publication gate."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score
from .metrics import performance_report
from ..integrations.research_controls import permutation_pvalue


def evaluate_predictions(predictions: pd.DataFrame, threshold=.60, trials=1) -> dict:
    p=predictions.p_up.clip(1e-6,1-1e-6)
    y=predictions.target.astype(int)
    side=np.where(p>=threshold,1,np.where(p<=1-threshold,-1,0))
    mask=side!=0
    selected=y[mask]
    selected_p=p[mask]
    result={
        'coverage':float(mask.mean()) if len(mask) else 0.0,
        'published_rows':int(mask.sum()),
        'precision_long':float(y[(p>=threshold)].mean()) if (p>=threshold).any() else np.nan,
        'precision_short':float((1-y[(p<=1-threshold)]).mean()) if (p<=1-threshold).any() else np.nan,
        'pr_auc':float(average_precision_score(y,p)) if y.nunique()==2 else np.nan,
    }
    if 'realized_return' in predictions:
        result.update(performance_report(predictions.loc[mask,'realized_return'],trials=trials))
    if len(selected):
        result['selected_mean_probability']=float(np.mean(np.maximum(selected_p,1-selected_p)))
    return result


def benchmark_gate(model_metrics: dict, baseline_logloss: float, baseline_brier: float, min_auc=.52) -> dict:
    reasons=[]
    if np.isfinite(model_metrics.get('auc',np.nan)) and model_metrics['auc'] < min_auc: reasons.append('auc_below_minimum')
    if model_metrics.get('log_loss',np.inf) >= baseline_logloss: reasons.append('does_not_beat_baseline_logloss')
    if model_metrics.get('brier',np.inf) >= baseline_brier: reasons.append('does_not_beat_baseline_brier')
    return {'pass':not reasons,'reasons':reasons}
