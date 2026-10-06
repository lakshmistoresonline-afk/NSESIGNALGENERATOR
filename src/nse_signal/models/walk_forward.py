"""Purged, time-ordered walk-forward model evaluation with calibration and ensembles."""
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score, log_loss, brier_score_loss
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from ..features.build import feature_columns, make_labels
from ..research.labels import execution_consistent_target
from ..research.calibration import TimeOrderedCalibrator, calibration_metrics
from ..research.metrics import performance_report
from ..research.uniqueness import horizon_uniqueness
from ..research.robustness import conformal_classification

@dataclass
class OOSResult:
    predictions: pd.DataFrame
    metrics: dict


def _select_features(train: pd.DataFrame, cols, max_features=80, corr_threshold=.97):
    x = train[list(cols)].replace([np.inf, -np.inf], np.nan)
    usable = [c for c in x.columns if x[c].notna().mean() >= .80 and x[c].nunique(dropna=True) > 5]
    if not usable: return []
    # Rank by univariate Spearman information using training data only.
    scores = {}
    y = train.target
    for c in usable:
        z = x[c]
        mask = z.notna() & y.notna()
        if mask.sum() < 50:
            continue
        scores[c] = abs(pd.Series(z[mask]).rank().corr(pd.Series(y[mask]).rank()))
    ordered = sorted(scores, key=lambda c: (scores[c], c), reverse=True)
    selected = []
    for c in ordered:
        if len(selected) >= max_features: break
        if not selected:
            selected.append(c); continue
        corr = x[selected + [c]].corr().abs()[c].drop(c)
        if corr.max() < corr_threshold:
            selected.append(c)
    return selected


def _fit_ensemble(train, features, random_state, sample_weight=None):
    x = train[features].replace([np.inf, -np.inf], np.nan).copy()
    med = x.median()
    x = x.fillna(med)
    y = train.target.astype(int)
    # Three deliberately different inductive biases.
    models = [
        make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced", C=0.5, random_state=random_state)),
        RandomForestClassifier(n_estimators=250, max_depth=6, min_samples_leaf=8, class_weight="balanced_subsample", random_state=random_state, n_jobs=-1),
        HistGradientBoostingClassifier(max_depth=3, learning_rate=.04, max_iter=150, l2_regularization=1.0, random_state=random_state),
    ]
    fitted=[]
    for m in models:
        if sample_weight is None:
            m.fit(x, y)
        elif hasattr(m, "steps"):
            m.fit(x, y, logisticregression__sample_weight=sample_weight)
        else:
            m.fit(x, y, sample_weight=sample_weight)
        fitted.append(m)
    return fitted, med


def _predict(models, med, X):
    x = X.replace([np.inf, -np.inf], np.nan).fillna(med)
    ps = np.vstack([m.predict_proba(x)[:,1] for m in models])
    return np.mean(ps, axis=0), np.std(ps, axis=0)


def walk_forward(df: pd.DataFrame, min_train=300, step=5, horizon=5, random_state=42, embargo=10, calibration_bars=60, max_features=80, label_method="triple_barrier", pt_atr=2.0, sl_atr=1.0, timeout_policy="directional") -> OOSResult:
    if {"timestamp","symbol"}.issubset(df.columns):
        raise ValueError("Panel data requires models.panel_walk_forward; row-based walk_forward is prohibited for multi-security panels")
    cols = feature_columns(df)
    if not cols:
        raise ValueError("No model features available")
    if 'target' not in df.columns:
        if label_method == 'triple_barrier':
            x = execution_consistent_target(df, horizon=horizon, pt_atr=pt_atr, sl_atr=sl_atr, timeout_policy=timeout_policy)
        elif label_method == 'directional':
            x = make_labels(df, horizon=horizon)
        else:
            raise ValueError("label_method must be triple_barrier or directional")
    else:
        x = df.copy()
    x = x.replace([np.inf, -np.inf], np.nan)
    x = x.dropna(subset=['target']).copy()
    preds=[]
    feature_history=[]
    # The label at t can consume data through t+horizon, so training must end
    # at least horizon+embargo bars before the test start.
    for i in range(min_train, len(x)-horizon, step):
        test_end=min(i+step, len(x)-horizon)
        train_end=max(0, i-horizon-embargo)
        train=x.iloc[:train_end].copy()
        test=x.iloc[i:test_end].copy()
        if len(train)<min_train or train.target.nunique()<2 or test.empty:
            continue
        features=_select_features(train, cols, max_features=max_features)
        if len(features)<5:
            continue
        # Tail calibration is strictly after model-training observations.
        cal_n=min(calibration_bars, max(40, len(train)//5))
        core=train.iloc[:-cal_n] if len(train)>cal_n+50 else train
        cal=train.iloc[-cal_n:] if len(train)>cal_n+50 else train.iloc[-min(40,len(train)):]
        if core.target.nunique()<2 or cal.target.nunique()<2:
            continue
        weights=horizon_uniqueness(core.index, horizon).to_numpy(dtype=float)
        models, med=_fit_ensemble(core, features, random_state, sample_weight=weights)
        # Split the tail calibration block: one part fits the probability map,
        # a strictly later part calibrates conformal coverage. Reusing the same
        # observations for both breaks the coverage guarantee.
        split=max(20,len(cal)//2)
        cal_fit=cal.iloc[:split]
        cal_conf=cal.iloc[split:]
        if cal_conf.target.nunique()<2 or cal_fit.target.nunique()<2:
            continue
        raw_cal_fit,_=_predict(models,med,cal_fit[features])
        calibrator=TimeOrderedCalibrator(min_calibration=min(20,len(cal_fit))).fit(raw_cal_fit,cal_fit.target)
        raw_conf,_=_predict(models,med,cal_conf[features])
        p_conf=calibrator.predict(raw_conf)
        raw_test, model_dispersion=_predict(models, med, test[features])
        p=calibrator.predict(raw_test)
        conformal = conformal_classification(p_conf, cal_conf.target, p, alpha=.10)
        # Ambiguous conformal sets are abstentions; preserve probability for diagnostics.
        conformal_abstain = conformal['abstain'].to_numpy(dtype=bool)
        pred=pd.DataFrame({'p_up':p,'raw_p_up':raw_test,'model_dispersion':model_dispersion,'conformal_abstain':conformal_abstain,'conformal_confidence':conformal['conformal_confidence'].to_numpy(float),'target':test.target.values,'close':test.close.values}, index=test.index)
        for c in ['open','high','low','volume']:
            if c in test: pred[c]=test[c].values
        if 'tb_label' in test: pred['tb_label']=test.tb_label.values
        feature_history.append(features)
        preds.append(pred)
    if not preds:
        raise ValueError('Not enough observations for purged walk-forward validation')
    out=pd.concat(preds).sort_index()
    out=out[~out.index.duplicated(keep='first')]
    y,p=out.target.astype(int),out.p_up.clip(1e-6,1-1e-6)
    metrics={
        'auc': float(roc_auc_score(y,p)) if y.nunique()==2 else float('nan'),
        'accuracy': float(accuracy_score(y,p>=.5)),
        'log_loss': float(log_loss(y,p,labels=[0,1])),
        'brier': float(brier_score_loss(y,p)),
        'oos_rows': int(len(out)),
        'purge_bars': int(horizon),
        'embargo_bars': int(embargo),
        'calibration_bars': int(calibration_bars),
        'median_selected_features': int(np.median([len(f) for f in feature_history])) if feature_history else 0,
        'unique_features_selected': int(len(set().union(*map(set, feature_history)))) if feature_history else 0,
        'baseline_50_log_loss': float(log_loss(y, np.full(len(y), .5), labels=[0,1])),
        'baseline_50_brier': float(brier_score_loss(y, np.full(len(y), .5))),
        'model_beats_50_log_loss': bool(log_loss(y,p,labels=[0,1]) < log_loss(y,np.full(len(y),.5),labels=[0,1])),
        'model_beats_50_brier': bool(brier_score_loss(y,p) < brier_score_loss(y,np.full(len(y),.5))),
        'event_uniqueness_weighting': True,
        'median_model_disagreement': float(out.model_dispersion.median()) if 'model_dispersion' in out else float('nan'),
        'high_disagreement_share': float((out.model_dispersion > .10).mean()) if 'model_dispersion' in out else float('nan'),
        'conformal_abstention_rate': float(out.conformal_abstain.mean()) if 'conformal_abstain' in out else float('nan'),
        'conformal_eligible_rate': float((~out.conformal_abstain).mean()) if 'conformal_abstain' in out else float('nan'),
        'label_method': label_method,
        'pt_atr': float(pt_atr),
        'sl_atr': float(sl_atr),
        'timeout_policy': timeout_policy,
    }
    return OOSResult(out, metrics)
