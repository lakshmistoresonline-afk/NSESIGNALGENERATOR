"""Pooled multi-symbol, time-based walk-forward evaluation."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, log_loss, brier_score_loss, accuracy_score
from .walk_forward import _select_features, _fit_ensemble, _predict
from ..features.build import feature_columns
from ..research.calibration import TimeOrderedCalibrator
from ..research.panel_labels import execution_consistent_target_panel


def panel_walk_forward(df: pd.DataFrame, *, min_train_times=80, step_times=5, horizon=5, embargo_times=10, max_features=80, calibration_times=20, random_state=42, pt_atr=2.0, sl_atr=1.0, timeout_policy='directional'):
    req={'timestamp','symbol'}
    if not req.issubset(df.columns): raise ValueError('panel_walk_forward requires timestamp and symbol columns')
    x=execution_consistent_target_panel(df,horizon=horizon,pt_atr=pt_atr,sl_atr=sl_atr,timeout_policy=timeout_policy)
    x=x.replace([np.inf,-np.inf],np.nan)
    times=np.array(sorted(pd.Series(x.timestamp).dropna().unique()))
    cols=feature_columns(x)
    if len(times)<=min_train_times+step_times: raise ValueError('not enough panel time periods')
    preds=[]; histories=[]
    for i in range(min_train_times,len(times)-horizon,step_times):
        test_times=times[i:min(i+step_times,len(times)-horizon)]
        if len(test_times)==0: continue
        test_start=test_times[0]
        cutoff_idx=max(0,i-embargo_times-max(int(horizon),1))
        train_times=times[:cutoff_idx]
        train=x[x.timestamp.isin(train_times)].dropna(subset=['target']).copy()
        test=x[x.timestamp.isin(test_times)].dropna(subset=['target']).copy()
        if len(train)<50 or train.target.nunique()<2 or test.empty: continue
        features=_select_features(train,cols,max_features=max_features)
        if len(features)<5: continue
        cal_unique=sorted(train.timestamp.unique())
        cal_n=min(calibration_times,max(10,len(cal_unique)//4))
        cal_start=max(1,len(cal_unique)-cal_n)
        cal_set=cal_unique[cal_start:]
        # Purge the training/calibration boundary because labels consume future
        # bars. Then purge again between probability calibration and conformal
        # calibration. This prevents future label information crossing either
        # boundary in a panel setting.
        purge_n=max(int(horizon)+1,1)
        core_end=max(1,cal_start-purge_n)
        core_times=set(cal_unique[:core_end])
        core=train[train.timestamp.isin(core_times)] if cal_set else train
        cal=train[train.timestamp.isin(set(cal_set))] if cal_set else train
        if len(core)<30 or core.target.nunique()<2 or cal.target.nunique()<2: continue
        cal_times_sorted=sorted(cal.timestamp.unique())
        split=max(2,len(cal_times_sorted)//2)
        fit_end=max(1,split-purge_n)
        cal_fit=cal[cal.timestamp.isin(cal_times_sorted[:fit_end])]
        cal_conf=cal[cal.timestamp.isin(cal_times_sorted[split:])]
        if len(cal_fit)<5 or len(cal_conf)<5 or cal_fit.target.nunique()<2 or cal_conf.target.nunique()<2:
            continue
        models,med=_fit_ensemble(core,features,random_state)
        raw_cal,_=_predict(models,med,cal_fit[features])
        calibrator=TimeOrderedCalibrator(min_calibration=min(10,len(cal_fit))).fit(raw_cal,cal_fit.target)
        raw_conf,_=_predict(models,med,cal_conf[features])
        p_conf=calibrator.predict(raw_conf)
        raw_test,disp=_predict(models,med,test[features])
        p=calibrator.predict(raw_test)
        from ..research.robustness import conformal_classification
        conf=conformal_classification(p_conf,cal_conf.target,p,alpha=.10)
        out=test[['timestamp','symbol','target']].copy(); out['p_up']=p; out['raw_p_up']=raw_test; out['model_dispersion']=disp
        out['conformal_abstain']=conf['abstain'].to_numpy(bool)
        out['conformal_confidence']=conf['conformal_confidence'].to_numpy(float)
        preds.append(out); histories.append(features)
    if not preds: raise ValueError('not enough panel observations for walk-forward')
    out=pd.concat(preds).sort_values(['timestamp','symbol']).drop_duplicates(['timestamp','symbol'])
    y=out.target.astype(int); p=out.p_up.clip(1e-6,1-1e-6)
    metrics={'auc':float(roc_auc_score(y,p)) if y.nunique()==2 else float('nan'),'accuracy':float(accuracy_score(y,p>=.5)),'log_loss':float(log_loss(y,p,labels=[0,1])),'brier':float(brier_score_loss(y,p)),'oos_rows':int(len(out)),'oos_times':int(out.timestamp.nunique()),'symbols':int(out.symbol.nunique()),'median_selected_features':int(np.median([len(f) for f in histories])),'median_model_disagreement':float(out.model_dispersion.median()),'conformal_abstention_rate':float(out.conformal_abstain.mean()),'timeout_policy':timeout_policy}
    return out,metrics
