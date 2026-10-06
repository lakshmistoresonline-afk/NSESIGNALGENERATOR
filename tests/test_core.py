import numpy as np
import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from nse_signal.data.market import synthetic_symbol
from nse_signal.features.build import make_features, FEATURES
from nse_signal.models.walk_forward import walk_forward
from nse_signal.backtest.engine import backtest_oos
from nse_signal.signals.engine import SignalEngine


def test_features_are_prefix_stable():
    raw=synthetic_symbol(n=500)
    a=make_features(raw)
    b=make_features(raw.iloc[:400])
    cols=FEATURES
    import numpy as np
    left=a.loc[b.index[-1], cols].to_numpy(dtype=float)
    right=b.loc[b.index[-1], cols].to_numpy(dtype=float)
    assert np.allclose(left, right, rtol=1e-10, atol=1e-12, equal_nan=True)


def test_walk_forward_is_oos():
    oos=walk_forward(make_features(synthetic_symbol(n=450)), min_train=180, step=80, max_features=40)
    assert len(oos.predictions)>0
    assert oos.predictions.index.min() > synthetic_symbol(n=450).index[250]


def test_backtest_outputs():
    oos=walk_forward(make_features(synthetic_symbol(n=450)), min_train=180, step=80, max_features=40)
    _, stats=backtest_oos(oos.predictions)
    assert "max_drawdown" in stats


def test_real_trading_is_rejected():
    try:
        SignalEngine(real_trading=True)
        assert False
    except RuntimeError:
        pass


def test_labels_do_not_create_fake_tail_targets():
    from nse_signal.features.build import make_labels
    raw=synthetic_symbol(n=100)
    lab=make_labels(raw,horizon=5)
    assert lab.target.tail(5).isna().all()


def test_triple_barrier_is_causal_and_collision_is_pessimistic():
    import pandas as pd
    from nse_signal.research.labels import triple_barrier_labels
    raw=synthetic_symbol(n=30)
    raw['atr_14']=1.0
    # Force both barriers on the next bar for a long event.
    raw.iloc[11, raw.columns.get_loc('high')]=raw.iloc[10].close+3
    raw.iloc[11, raw.columns.get_loc('low')]=raw.iloc[10].close-2
    side=pd.Series(0.0,index=raw.index); side.iloc[10]=1
    out=triple_barrier_labels(raw,horizon=3,pt_atr=2,sl_atr=1,side=side)
    assert out.tb_label.iloc[10] == -1
    assert pd.isna(out.tb_label.iloc[0])


def test_signal_engine_is_symmetric_and_signal_only():
    e=SignalEngine()
    buy=e.generate('X',.72,.70,price=100,atr=2,atr_pct=.02,regime='BULL')
    sell=e.generate('X',.28,.70,price=100,atr=2,atr_pct=.02,regime='BEAR')
    assert buy is not None and buy.side=='BUY' and buy.real_trading is False
    assert sell is not None and sell.side=='SELL' and sell.real_trading is False


def test_data_quality_gate():
    from nse_signal.data.quality import validate_ohlcv
    raw=synthetic_symbol(n=50)
    raw.iloc[5,raw.columns.get_loc('high')]=raw.iloc[5].low-1
    assert validate_ohlcv(raw)['pass'] is False


def test_triple_barrier_uses_next_bar_execution_price():
    from nse_signal.research.labels import triple_barrier_labels
    raw=synthetic_symbol(n=40)
    raw['atr_14']=1.0
    raw.iloc[11,raw.columns.get_loc('open')]=raw.iloc[10].close*1.10
    raw.iloc[11,raw.columns.get_loc('high')]=raw.iloc[11].open*1.01
    raw.iloc[11,raw.columns.get_loc('low')]=raw.iloc[11].open*.99
    side=pd.Series(0.0,index=raw.index); side.iloc[10]=1
    out=triple_barrier_labels(raw,horizon=3,pt_atr=2,sl_atr=1,side=side)
    assert np.isclose(out.tb_entry_price.iloc[10],raw.open.iloc[11])


def test_cpcv_is_purged_and_time_grouped():
    from nse_signal.research.robustness import combinatorial_purged_splits
    splits=list(combinatorial_purged_splits(120,n_groups=6,test_groups=2,purge=3,embargo=2))
    assert len(splits)==15
    for tr,te in splits:
        assert set(tr).isdisjoint(set(te))
        assert len(tr)>0 and len(te)>0


def test_conformal_abstains_on_ambiguous_sets():
    from nse_signal.research.robustness import conformal_classification
    p=np.array([.5,.52,.9,.1,.7,.3]*10); y=np.array([0,1,1,0,1,0]*10)
    out=conformal_classification(p,y,np.array([.5,.51,.99,.01]),alpha=.1)
    assert len(out)==4
    assert out.abstain.iloc[0]


def test_psi_zero_for_identical_distribution():
    from nse_signal.research.robustness import population_stability_index
    x=np.linspace(-1,1,100)
    assert population_stability_index(x,x) < 1e-12


def test_asof_validation_rejects_future_provider_data():
    import pandas as pd
    from nse_signal.data.provenance import validate_asof_data
    x=pd.DataFrame({'signal_time':['2026-01-01T10:00:00Z'],'asof_time':['2026-01-01T10:01:00Z']})
    assert validate_asof_data(x)['pass'] is False


def test_validation_threshold_is_bounded():
    from nse_signal.research.thresholds import choose_threshold
    y=np.array([0,1]*100); p=np.linspace(.01,.99,200)
    out=choose_threshold(y,p)
    assert .55 <= out['threshold'] <= .95


def test_portfolio_caps_concentration():
    from nse_signal.research.portfolio import rank_signals, concentration_metrics
    x=pd.DataFrame({'symbol':['A','B','C'],'quality_score':[.9,.8,.7],'sector':['X','X','Y']})
    out=rank_signals(x,max_names=3,max_single_name=.5,max_sector=.6)
    m=concentration_metrics(out.weight)
    assert m['max_weight'] <= .5 + 1e-12

def test_governance_and_uniqueness():
    from nse_signal.research.uniqueness import horizon_uniqueness
    from nse_signal.research.model_gate import model_acceptance_gate
    idx=pd.date_range('2020-01-01', periods=20, freq='D')
    w=horizon_uniqueness(idx,5)
    assert len(w)==20 and (w>0).all()
    gate=model_acceptance_gate({'auc':.55,'brier':.20,'baseline_logloss':.70,'baseline_brier':.25,'log_loss':.68,'coverage':.2,'feature_stability':.8,'max_psi':.05,'profit_factor':1.2,'max_drawdown':-.2,'cpcv_paths':10,'pbo':.20,'dsr_stat':1.2,'multiple_testing_trials':3,'validation_method':'CPCV_CSCV_PBO','dsr_method':'finite_trial_expected_max_normal_numerical'})
    assert gate['pass']
