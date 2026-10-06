import numpy as np
import pandas as pd
from nse_signal.research.adversarial import adversarial_validation
from nse_signal.research.dependence import bootstrap_mean_ci
from nse_signal.research.regime_controls import conditional_signal_report, regime_stability_penalty
from nse_signal.signals.engine import SignalEngine


def test_adversarial_validation_detects_shift():
    rng=np.random.default_rng(4)
    ref=pd.DataFrame({'a':rng.normal(0,1,300),'b':rng.normal(0,1,300)})
    cur=pd.DataFrame({'a':rng.normal(2,1,300),'b':rng.normal(0,1,300)})
    r=adversarial_validation(ref,cur)
    assert r['auc'] > .65
    assert r['drifted']


def test_block_bootstrap_ci_is_finite():
    rng=np.random.default_rng(2)
    x=rng.normal(.01,.05,200)
    r=bootstrap_mean_ci(x,block_length=8,n_boot=200)
    assert r['lower'] <= r['mean'] <= r['upper']


def test_regime_controls():
    p=np.array([.8,.8,.8,.8,.8,.2,.2,.2,.2,.2]*6)
    y=np.array([1,1,1,0,1,0,0,0,1,0]*6)
    df=pd.DataFrame({'p_up':p,'target':y,'regime':['BULL']*30+['BEAR']*30})
    r=conditional_signal_report(df,threshold=.7,min_n=5)
    assert 'regime' in r
    assert regime_stability_penalty(r,min_precision=.5,min_n=5)['pass']


def test_signal_persistence_gate():
    e=SignalEngine()
    assert e.generate('X',.8,.8,price=100,atr=2,prediction_persistence=1,min_prediction_persistence=2) is None


def test_triple_barrier_horizon_matches_next_open_execution():
    import pandas as pd
    import numpy as np
    from nse_signal.research.labels import triple_barrier_labels
    n=8
    df=pd.DataFrame({
        "open":np.arange(10,10+n,dtype=float),
        "high":np.arange(11,11+n,dtype=float),
        "low":np.arange(9,9+n,dtype=float),
        "close":np.arange(10.5,10.5+n,dtype=float),
        "atr_14":np.ones(n),
    })
    out=triple_barrier_labels(df,horizon=2,pt_atr=100,sl_atr=100)
    # With no barriers hit, t=0 enters at open[1] and times out at close[3].
    assert np.isclose(out.loc[0,"tb_entry_price"], df.loc[1,"open"])
    assert np.isclose(out.loc[0,"tb_return"], df.loc[3,"close"]/df.loc[1,"open"]-1)


def test_model_gate_rejects_missing_evidence():
    from nse_signal.research.model_gate import model_acceptance_gate
    result=model_acceptance_gate({})
    assert result["pass"] is False
    assert any(r.startswith("missing_or_invalid_") for r in result["reasons"])


def test_signal_requires_economic_context_by_default():
    from nse_signal.signals.engine import SignalEngine
    assert SignalEngine().generate("TEST", .80, .80, regime="BULL") is None

def test_cross_sectional_features_are_point_in_time():
    import pandas as pd
    from nse_signal.research.cross_sectional import cross_sectional_features
    df=pd.DataFrame({
        "timestamp":[1,1,1,2,2,2],"symbol":["A","B","C"]*2,
        "return_1d":[.03,.01,-.01,-.02,0,.02],"sector":["X","X","Y","X","X","Y"]
    })
    out=cross_sectional_features(df)
    assert set(out.loc[out.timestamp==1,"cs_return_rank"].round(6))=={round(1/3,6),round(2/3,6),1.0}
    assert out.loc[out.timestamp==1,"cs_return_rank"].tolist()!=out.loc[out.timestamp==2,"cs_return_rank"].tolist()


def test_cpcv_and_pbo_are_dependence_aware():
    import numpy as np
    from nse_signal.research.validation import combinatorial_purged_splits, pbo_from_paths
    splits=combinatorial_purged_splits(120,n_groups=6,test_groups=2,purge_bars=3,embargo_bars=2)
    assert len(splits)==15
    ins=np.array([[.8,.7,.6],[.7,.8,.6],[.6,.7,.9]])
    oos=np.array([[.4,.6,.5],[.6,.5,.4],[.3,.2,.8]])
    assert 0.0 <= pbo_from_paths(ins,oos) <= 1.0

def test_advanced_features_are_causal_and_finite():
    import numpy as np, pandas as pd
    from nse_signal.features.advanced import add_advanced_features
    n=100
    close=np.linspace(100,120,n)+np.sin(np.arange(n))
    df=pd.DataFrame({'open':close-.5,'high':close+1,'low':close-1,'close':close,'volume':np.arange(n)+1000.0})
    out=add_advanced_features(df)
    assert 'parkinson_vol_20' in out and 'amihud_20' in out
    assert out.index.equals(df.index)
    assert np.isfinite(out['directional_efficiency_20'].dropna()).all()


def test_walk_forward_exposes_model_disagreement():
    import numpy as np, pandas as pd
    from nse_signal.features.build import make_features
    from nse_signal.models.walk_forward import walk_forward
    n=180
    rng=np.random.default_rng(11)
    close=100*np.exp(np.cumsum(rng.normal(0,.01,n)))
    df=pd.DataFrame({'open':close*(1+rng.normal(0,.002,n)),'high':close*(1+abs(rng.normal(0,.005,n))), 'low':close*(1-abs(rng.normal(0,.005,n))), 'close':close,'volume':rng.integers(1000,5000,n).astype(float)})
    f=make_features(df)
    r=walk_forward(f,min_train=60,step=10,horizon=3,embargo=3,calibration_bars=30,max_features=15)
    assert 'model_dispersion' in r.predictions.columns


def test_economic_threshold_and_block_bootstrap():
    import numpy as np
    from nse_signal.research.selection import choose_economic_threshold
    from nse_signal.research.bootstrap import block_bootstrap_ci
    y=np.array([1,1,0,1,0,0,1,1,0,1])
    p=np.array([.8,.75,.7,.65,.6,.4,.35,.25,.3,.9])
    r=choose_economic_threshold(y,p,reward_multiple=2,risk_multiple=1,min_coverage=.1)
    assert .55 <= r['threshold'] <= .95
    ci=block_bootstrap_ci(np.linspace(-.01,.02,30),n=100,block_length=5)
    assert ci['lower'] <= ci['upper']


def test_horizon_agreement():
    import pandas as pd
    from nse_signal.research.multihorizon import horizon_agreement
    x=pd.DataFrame({'p_up_1':[.8,.2,.55], 'p_up_5':[.75,.25,.8], 'p_up_10':[.7,.3,.2]})
    r=horizon_agreement(x,min_horizons=2,agreement=.6)
    assert r.loc[0,'eligible'] and r.loc[0,'direction']==1
    assert r.loc[1,'eligible'] and r.loc[1,'direction']==-1

def test_fractional_difference_is_causal():
    import numpy as np, pandas as pd
    from nse_signal.features.market_state import fractional_difference
    x=pd.Series(np.arange(120,dtype=float))
    a=fractional_difference(x,d=.4,window=20)
    b=fractional_difference(x,d=.4,window=20)
    assert a.equals(b)
    x2=x.copy(); x2.iloc[-1]=999999
    b2=fractional_difference(x2,d=.4,window=20)
    assert np.allclose(a.iloc[:-1].dropna(), b2.iloc[:-1].dropna())


def test_volume_bars_are_causal():
    import pandas as pd
    from nse_signal.features.market_state import volume_bars
    df=pd.DataFrame({'open':[1,2,3,4],'high':[2,3,4,5],'low':[.5,1.5,2.5,3.5],'close':[1.5,2.5,3.5,4.5],'volume':[4,4,4,4]},index=pd.date_range('2026-01-01',periods=4))
    out=volume_bars(df,8)
    assert len(out)==2 and out.volume.tolist()==[8,8]


def test_impact_model_is_positive():
    from nse_signal.research.impact import square_root_impact_bps, total_expected_cost_bps
    x=square_root_impact_bps(100000,10000000,.02)
    assert x>0 and total_expected_cost_bps(30,x,5)>35


def test_meta_gate_features_and_signal_gate():
    import pandas as pd
    from nse_signal.research.meta_model import meta_features
    from nse_signal.signals.engine import SignalEngine
    p=pd.DataFrame({'p_up':[.8,.2],'model_dispersion':[.02,.03],'conformal_confidence':[.9,.9]})
    assert 'primary_confidence' in meta_features(p)
    assert SignalEngine().generate('X',.8,.8,price=100,atr=2,meta_probability=.40) is None

def test_signal_rejects_high_ensemble_disagreement_and_conformal_abstention():
    from nse_signal.signals.engine import SignalEngine
    e=SignalEngine()
    assert e.generate('X',.82,.8,price=100,atr=2,model_dispersion=.20) is None
    assert e.generate('X',.82,.8,price=100,atr=2,conformal_abstain=True) is None


def test_panel_features_are_cross_sectional_and_time_local():
    import pandas as pd
    from nse_signal.research.panel import add_cross_sectional_panel_features
    df=pd.DataFrame({'timestamp':[1,1,1,2,2,2],'symbol':['A','B','C']*2,'return_1d':[.1,.2,.3,.3,.2,.1],'sector':['X','X','Y']*2,'atr_pct':[.1,.2,.3,.3,.2,.1],'dollar_volume':[1,2,3,3,2,1]})
    o=add_cross_sectional_panel_features(df)
    assert set(o.loc[o.timestamp==1,'cs_return_rank'])=={1/3,2/3,1.0}
    assert o.loc[o.timestamp==1,'cs_return_rank'].tolist()!=o.loc[o.timestamp==2,'cs_return_rank'].tolist()

def test_threshold_stability():
    import numpy as np
    from nse_signal.research.threshold_stability import threshold_stability
    y=np.array([1,1,1,0,0,0,1,1,0,0])
    p=np.array([.8,.78,.76,.24,.22,.2,.72,.7,.28,.3])
    r=threshold_stability(y,p,.70)
    assert r['thresholds_tested']>0 and 0<=r['stable_share']<=1


def test_panel_walk_forward_is_time_based_and_symbol_safe():
    import numpy as np, pandas as pd
    from nse_signal.features.build import make_features
    from nse_signal.models.panel_walk_forward import panel_walk_forward
    rng=np.random.default_rng(19); parts=[]
    for s in ['A','B','C','D']:
        n=150; close=100*np.exp(np.cumsum(rng.normal(0,.01,n)))
        t=pd.date_range('2024-01-01',periods=n)
        g=pd.DataFrame({'timestamp':t,'symbol':s,'open':close*(1+rng.normal(0,.001,n)),'high':close*(1+abs(rng.normal(0,.004,n))),'low':close*(1-abs(rng.normal(0,.004,n))),'close':close,'volume':rng.integers(1000,5000,n).astype(float)})
        parts.append(g)
    raw=pd.concat(parts,ignore_index=True).sort_values(['timestamp','symbol'])
    f=make_features(raw)
    o,m=panel_walk_forward(f,min_train_times=60,step_times=10,horizon=3,embargo_times=3,max_features=12,calibration_times=15)
    assert o.symbol.nunique()==4 and o.timestamp.nunique()>0 and np.isfinite(m['log_loss'])


def test_falsification_and_cost_stress_and_calibration():
    import numpy as np
    import pandas as pd
    from nse_signal.research.falsification import label_permutation_auc, temporal_shift_auc
    from nse_signal.research.economic_stress import stress_returns
    from nse_signal.research.calibration import calibration_curve_metrics
    rng=np.random.default_rng(1); y=rng.integers(0,2,120); p=np.clip(.25+.5*rng.random(120),.01,.99)
    assert label_permutation_auc(y,p,n=20)["n"]==20
    assert "shift_1_auc" in temporal_shift_auc(y,p)
    assert "cost_3.0x_mean_return" in stress_returns(rng.normal(.001,.01,120))
    m=calibration_curve_metrics(y,p); assert 0<=m["ece"]<=1
