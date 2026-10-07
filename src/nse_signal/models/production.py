"""Production model artifact lifecycle for signal-only NSE research with hardened metadata, feature schema hash, dataset manifest hash, and fail-closed version checks.
No broker execution is implemented here.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import hashlib, json, os, time
import joblib
import numpy as np
import pandas as pd
from ..research.calibration import TimeOrderedCalibrator
from .walk_forward import _select_features, _fit_ensemble, _predict

@dataclass
class ProductionArtifact:
    model_id: str
    features: list[str]
    median_values: dict
    models: list
    calibrator: TimeOrderedCalibrator
    trained_through: str
    contract_hash: str
    conformal_quantile: float | None = None
    conformal_scores_0: list[float] | None = None
    conformal_scores_1: list[float] | None = None
    conformal_alpha: float = 0.10
    conformal_version: int = 2
    publication_threshold: float = 0.55
    source_data_hash: str = "PENDING"
    model_data_hash: str = "PENDING"
    config_hash: str = "PENDING"
    feature_schema_version: str = "v3.1"
    feature_schema_hash: str = "PENDING"
    dataset_manifest_hash: str = "PENDING"
    validator_version: str = "3.1.0"
    model_version: str = "3.1.0"
    training_interval: str = "PENDING"
    created_at: float = field(default_factory=time.time)

def fit_production_model(df: pd.DataFrame, *, horizon=5, pt_atr=2.0, sl_atr=1.0,
                         calibration_bars=80, max_features=80, random_state=42, timeout_policy='directional',
                         model_id="nse-production", source_data_hash="PENDING", config_hash="PENDING", dataset_manifest_hash="PENDING") -> ProductionArtifact:
    """Fit only on labels whose full future event is already observable.
    The newest unlabeled row is reserved for prediction.
    """
    from ..features.build import feature_columns
    if {"timestamp","symbol"}.issubset(df.columns):
        from ..research.panel_labels import execution_consistent_target_panel
        x=execution_consistent_target_panel(df.sort_values(["timestamp","symbol"]),horizon=horizon,pt_atr=pt_atr,sl_atr=sl_atr,timeout_policy=timeout_policy)
    else:
        from ..research.labels import execution_consistent_target
        x=execution_consistent_target(df.sort_index(),horizon=horizon,pt_atr=pt_atr,sl_atr=sl_atr,timeout_policy=timeout_policy)
    x=x.replace([np.inf,-np.inf],np.nan).dropna(subset=['target'])
    if len(x)<300 or x.target.nunique()<2: raise ValueError('insufficient labeled observations')
    cols=feature_columns(x)
    features=_select_features(x,cols,max_features=max_features)
    if len(features)<5: raise ValueError('insufficient stable production features')
    cal_n=min(calibration_bars,max(40,len(x)//5))
    purge_bars=max(int(horizon)+1,1)
    if {'timestamp','symbol'}.issubset(x.columns):
        unique_times=sorted(pd.to_datetime(x.timestamp,utc=True).dropna().unique())
        cal_start=max(1,len(unique_times)-cal_n)
        core_end=max(1,cal_start-purge_bars)
        core_times=set(unique_times[:core_end])
        cal_times=set(unique_times[cal_start:])
        core=x[x.timestamp.isin(core_times)].copy(); cal=x[x.timestamp.isin(cal_times)].copy()
    else:
        cal_start=max(1,len(x)-cal_n)
        core_end=max(1,cal_start-purge_bars)
        core=x.iloc[:core_end].copy(); cal=x.iloc[cal_start:].copy()
    if core.target.nunique()<2 or cal.target.nunique()<2: raise ValueError('calibration tail lacks both classes')
    models,med=_fit_ensemble(core,features,random_state)
    if {'timestamp','symbol'}.issubset(x.columns):
        ct=sorted(pd.to_datetime(cal.timestamp,utc=True).dropna().unique())
        split=max(1,len(ct)//2)
        fit_end=max(1, split-purge_bars)
        fit_times=set(ct[:fit_end]); conf_times=set(ct[split:])
        cal_fit=cal[cal.timestamp.isin(fit_times)]; cal_conf=cal[cal.timestamp.isin(conf_times)]
    else:
        split=max(20,len(cal)//2)
        fit_end=max(1, split-purge_bars)
        cal_fit=cal.iloc[:fit_end]; cal_conf=cal.iloc[split:]
    if len(cal_fit)<20 or len(cal_conf)<10 or cal_fit.target.nunique()<2 or cal_conf.target.nunique()<2:
        raise ValueError('two-stage calibration tail lacks both classes')
    raw_cal,_=_predict(models,med,cal_fit[features])
    calibrator=TimeOrderedCalibrator(min_calibration=min(30,len(cal_fit))).fit(raw_cal,cal_fit.target)
    raw_conf,_=_predict(models,med,cal_conf[features])
    p_conf=calibrator.predict(raw_conf)
    from ..research.robustness import threshold_from_validation
    publication_threshold=float(threshold_from_validation(
        cal_conf.target.to_numpy(dtype=int), p_conf,
        min_threshold=.55, max_threshold=.90, min_coverage=.05))
    conf_y=cal_conf.target.to_numpy(dtype=int)
    scores0=(1-p_conf[conf_y==0]).astype(float).tolist()
    scores1=p_conf[conf_y==1].astype(float).tolist()
    conformal_q=None
    trained_through=str(x.timestamp.max() if 'timestamp' in x.columns else x.index.max())
    contract={'horizon':horizon,'pt_atr':pt_atr,'sl_atr':sl_atr,'features':features,
              'calibration_bars':cal_n,'random_state':random_state,'timeout_policy':timeout_policy,'publication_threshold':publication_threshold,'conformal_version':2}
    ch=hashlib.sha256(json.dumps(contract,sort_keys=True).encode()).hexdigest()
    model_data_hash=hashlib.sha256(str(models).encode()).hexdigest()
    feature_schema_hash=hashlib.sha256(json.dumps(sorted(features)).encode()).hexdigest()
    training_interval = f"{x.timestamp.min()} -> {trained_through}" if 'timestamp' in x.columns else f"{x.index.min()} -> {trained_through}"
    return ProductionArtifact(model_id,features,{k:float(v) for k,v in med.to_dict().items()},models,calibrator,trained_through,ch,conformal_q,scores0,scores1,0.10,2,publication_threshold,source_data_hash,model_data_hash,config_hash,"v3.1",feature_schema_hash,dataset_manifest_hash,"3.1.0","3.1.0",training_interval,time.time())

def save_artifact(artifact: ProductionArtifact, path: str) -> Path:
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(p.suffix+'.tmp')
    joblib.dump(artifact,tmp)
    os.replace(tmp,p)
    return p

def load_artifact(path: str) -> ProductionArtifact:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Model artifact not found: {path}")
    a=joblib.load(path)
    if not isinstance(a,ProductionArtifact):
        raise ValueError('Incompatible artifact format: not a ProductionArtifact instance')
    if a.conformal_version < 2:
        raise ValueError('Incompatible artifact version: conformal_version < 2')
    return a

def predict_latest(artifact: ProductionArtifact, df: pd.DataFrame) -> dict:
    missing=set(artifact.features)-set(df.columns)
    if missing: raise ValueError(f'missing production features: {sorted(missing)}')
    x=df.iloc[[-1]].copy()
    med=pd.Series(artifact.median_values)
    raw,_=_predict(artifact.models,med,x[artifact.features])
    p=float(artifact.calibrator.predict(raw)[0])
    if artifact.conformal_version < 2 or not artifact.conformal_scores_0 or not artifact.conformal_scores_1:
        conformal_abstain=True; pv0=pv1=0.0
    else:
        scores0=np.asarray(artifact.conformal_scores_0,dtype=float)
        scores1=np.asarray(artifact.conformal_scores_1,dtype=float)
        pv0=float((1+np.sum(scores0 >= (1-p)))/(len(scores0)+1))
        pv1=float((1+np.sum(scores1 >= p))/(len(scores1)+1))
        include0=pv0>float(artifact.conformal_alpha); include1=pv1>float(artifact.conformal_alpha)
        conformal_abstain=(int(include0)+int(include1))!=1
    return {'probability_up':p,'raw_probability_up':float(raw[0]),
            'model_dispersion':float(_predict(artifact.models,med,x[artifact.features])[1][0]),
            'conformal_abstain':conformal_abstain,
            'conformal_p_value_0':pv0,'conformal_p_value_1':pv1,
            'conformal_alpha':float(artifact.conformal_alpha),
            'conformal_version':int(artifact.conformal_version),
            'publication_threshold':float(artifact.publication_threshold),
            'model_id':artifact.model_id,'trained_through':artifact.trained_through,
            'contract_hash':artifact.contract_hash,
            'source_data_hash':artifact.source_data_hash,
            'model_data_hash':artifact.model_data_hash,
            'config_hash':artifact.config_hash,
            'feature_schema_version':artifact.feature_schema_version,
            'feature_schema_hash':artifact.feature_schema_hash,
            'dataset_manifest_hash':artifact.dataset_manifest_hash,
            'validator_version':artifact.validator_version,
            'model_version':artifact.model_version,
            'training_interval':artifact.training_interval,
            'created_at':artifact.created_at}
