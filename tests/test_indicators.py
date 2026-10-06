import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import numpy as np, pandas as pd
import pytest
from nse_signal.features.build import make_features, FEATURES, feature_columns


def frame(n=500):
    rng=np.random.default_rng(7); c=100*np.exp(np.cumsum(rng.normal(0,.01,n)))
    h=c*(1+rng.uniform(0,.01,n)); l=c*(1-rng.uniform(0,.01,n)); o=c*(1+rng.normal(0,.003,n)); v=rng.integers(100000,1000000,n)
    return pd.DataFrame({'open':o,'high':h,'low':l,'close':c,'volume':v},index=pd.date_range('2024-01-01',periods=n))


def test_indicator_coverage():
    out=make_features(frame())
    missing=[f for f in FEATURES if f not in out.columns]
    assert not missing, missing
    for col in ['rsi_14','adx','atr_14','natr_14','cci_20','mfi_14','ppo','aroon_osc','ultimate_osc','smi','kst','connors_rsi','chop_14','emv_14','rvir_14']:
        assert out[col].notna().sum()>0, col


def test_no_future_feature_dependency():
    df=frame(320); a=make_features(df.iloc[:220]); b=make_features(df.iloc[:221])
    cols=['rsi_14','adx','atr_14','bb_pos','macd','volume_z','sma_200','cci_20','aroon_osc','donchian_pos_55']
    for col in cols:
        if pd.notna(a.iloc[-1][col]) and pd.notna(b.iloc[-2][col]):
            assert abs(a.iloc[-1][col]-b.iloc[-2][col]) < 1e-10, col


def test_edge_cases_are_bounded():
    n=260; c=np.full(n,100.0); df=pd.DataFrame({'open':c,'high':c,'low':c,'close':c,'volume':np.full(n,100000)},index=pd.date_range('2024-01-01',periods=n))
    out=make_features(df)
    assert np.isfinite(out[['rsi_14','mfi_14']].dropna()).all().all()
    assert out['rsi_14'].dropna().iloc[-1] == 50.0
    assert out['mfi_14'].dropna().iloc[-1] == 50.0


def test_breakout_does_not_use_current_high():
    df=frame(250); out=make_features(df)
    # A breakout feature is defined against the prior 20-bar channel, not one containing t.
    i=out.index[-1]; prior_high=df.high.iloc[-21:-1].max(); expected=int(df.close.iloc[-1] >= prior_high)
    assert int(out.loc[i,'high_20_breakout']) == expected


def test_wilder_seed_matches_sma_seed():
    from nse_signal.features.indicators import _wilder
    s=pd.Series(np.arange(1,8,dtype=float))
    out=_wilder(s,3)
    assert out.iloc[2] == 2.0
    assert abs(out.iloc[3] - (2.0 + (4.0-2.0)/3.0)) < 1e-12


def test_aroon_oldest_and_current_extremes():
    from nse_signal.features.indicators import aroon
    df=pd.DataFrame({'high':[5,4,3,2,1], 'low':[1,2,3,4,5], 'close':[3,3,3,3,3], 'volume':[1]*5})
    up,dn,osc=aroon(df,5)
    assert up.iloc[-1] == 20.0
    assert dn.iloc[-1] == 20.0
    # Current-bar extremes are 100 on the corresponding side.
    df2=df.iloc[::-1].reset_index(drop=True)
    up2,dn2,_=aroon(df2,5)
    assert up2.iloc[-1] == 100.0
    assert dn2.iloc[-1] == 100.0


def test_rvi_is_bounded_and_neutral_on_flat_data():
    from nse_signal.features.indicators import rvi
    df=pd.DataFrame({'high':[100.0]*80,'low':[100.0]*80,'close':[100.0]*80,'volume':[1000]*80})
    out=rvi(df,14,10).dropna()
    assert len(out)>0
    assert np.isfinite(out).all()
    assert (out == 50.0).all()


def test_optional_context_is_provider_driven():
    df=frame(500)
    df['nifty_return']=df.close.pct_change()*0.8
    df['sector_return']=df.close.pct_change()*0.6
    out=make_features(df)
    cols=feature_columns(out)
    for col in ['nifty_return','nifty_return_z20','sector_return','sector_return_z20','beta_60','corr_60','relative_strength_nifty','relative_strength_sector']:
        assert col in cols
        assert out[col].notna().sum()>0, col

def test_extended_talib_family_coverage():
    out=make_features(frame(500))
    cols=['wma_20','ht_trendline','aroon_osc','cmou_14','ac_5_34','kdj_k','kdj_d','kdj_j','macdext','macdext_signal','macdext_hist','macdfix','macdfix_signal','macdfix_hist','fosc_14','fractal_up','fractal_down','rocr100_20']
    for col in cols:
        assert col in out.columns, col
        assert out[col].notna().sum()>0, col

def test_fractal_is_confirmation_delayed():
    from nse_signal.features.indicators import fractal_williams
    h=[1,2,5,2,1,1,1]; l=[0,0,0,0,0,0,0]
    df=pd.DataFrame({'open':h,'high':h,'low':l,'close':h,'volume':[1]*len(h)})
    up,_=fractal_williams(df)
    assert up.iloc[2] == 0
    assert up.iloc[4] == 1


def test_features_are_causal_without_future_labels():
    out=make_features(frame(400))
    assert 'future_return' not in out.columns
    assert 'target' not in out.columns


def test_labels_are_separate_from_features():
    from nse_signal.features.build import make_labeled_features
    out=make_labeled_features(frame(400), horizon=5)
    assert 'future_return' in out.columns and 'target' in out.columns
    assert 'target' not in make_features(frame(400)).columns

def test_beta_uses_population_covariance():
    from nse_signal.features.indicators import beta_vs_market
    a=pd.Series([1.,2.,3.,4.,5.]); b=pd.Series([2.,4.,6.,8.,10.])
    out=beta_vs_market(a,b,5)
    assert abs(out.iloc[-1]-0.5)<1e-12


def test_ema_uses_sma_seed():
    from nse_signal.features.indicators import _ema
    s=pd.Series([1.,2.,3.,4.,5.,6.])
    out=_ema(s,3)
    assert out.iloc[0:2].isna().all()
    assert out.iloc[2] == 2.0
    assert abs(out.iloc[3] - (2.0 + 0.5*(4.0-2.0))) < 1e-12


def test_smi_formula_and_range():
    from nse_signal.features.indicators import stochastic_momentum_index
    df=frame(300)
    smi, sig=stochastic_momentum_index(df,13,2,25,9)
    assert smi.notna().sum() > 0
    vals=smi.dropna()
    assert ((vals >= -100.000001) & (vals <= 100.000001)).all()


def test_parameter_changes_are_wired_into_calculations():
    df=frame(400)
    base=make_features(df)
    params={'trend':{'sma':[5,10,20,50,100,200],'ema':[5,10,20,50,100,200]},
            'momentum':{'rsi':[5,14,21],'roc':[5,10,20], 'macd':{'fast':8,'slow':21,'signal':5,'ma_type':'ema'},
                        'ppo':{'fast':8,'slow':21,'signal':5,'ma_type':'ema'},
                        'stochastic':{'k_period':10,'slow_k_period':2,'slow_k_ma_type':'sma','slow_d_period':2,'slow_d_ma_type':'sma'},
                        'stochastic_rsi':{'rsi_period':10,'k_period':4,'d_period':2,'d_ma_type':'sma'},
                        'adx':{'period':10},'adxr':{'period':10},'cci':{'period':15},'williams_r':{'period':10},'mfi':{'period':10},
                        'tsi':{'long':20,'short':10},'awesome_oscillator':{'fast':4,'slow':20},'cmo':{'period':10},
                        'ultimate_oscillator':{'short':5,'medium':10,'long':20},'vortex':{'period':10},'rvi':{'period':10,'stddev_period':8},
                        'efficiency_ratio':{'period':8},'vhf':{'period':20}},
            'volatility':{'atr':[5,14,20],'realized_vol':[5,10,20,60],'bollinger':{'period':15,'stddev_up':1.5,'stddev_dn':2.5,'ma_type':'ema'},'donchian':[10,30],'keltner':{'ema_period':15,'atr_period':8,'multiplier':1.5}},
            'volume':{'volume_ratio':[10,30],'volume_zscore':[10],'obv':True,'ad_line':True,'ad_oscillator':{'fast':2,'slow':8},'cmf':{'period':15},'mfi':{'period':10},'pvt':True,'force_index':{'period':8},'market_facilitation':True,'pvi':True,'nvi':True},
            'price_structure':{},'relative':{'returns':[1,3,5,20,60,120]},'additional':{'momentum':{'macd_extended':{'fast':8,'slow':21,'signal':5,'fast_type':'ema','slow_type':'ema','signal_type':'ema'},'macdfix_signal':5,'stochastic_fast':{'k_period':4,'d_period':2,'d_ma_type':'sma'},'kdj':{'k_period':7,'k_smooth':2,'d_smooth':2,'k_ma_type':'rma','d_ma_type':'rma'}},'overlap':{'wma_period':15,'zlema_period':15,'trima_period':15,'midpoint_period':10,'midprice_period':10,'t3':{'period':4,'volume_factor':0.6}},'statistics':{'linear_regression_window':15,'percentile_window':15,'percent_rank_window':15,'stddev_window':15,'variance_window':15,'kurtosis_window':15,'median_window':15},'volatility':{'adr_period':10,'chaikin_volatility_period':8,'mass_index_ema':8,'mass_index_sum':20,'rvir_period':10},'volume':{'emv_period':10,'pvo':{'fast':8,'slow':21,'signal':5,'ma_type':'ema'},'rvol_period':15}}}
    changed=make_features(df,params=params)
    assert 'rsi_5' in changed.columns and not changed['rsi_5'].equals(base['rsi_7'])
    assert 'donchian_high_10' in changed.columns and 'donchian_high_30' in changed.columns
    assert 'macd' in changed.columns and not np.allclose(changed['macd'].dropna().tail(20),base['macd'].dropna().tail(20))
    assert not np.allclose(changed['bb_upper'].dropna().tail(20),base['bb_upper'].dropna().tail(20))


def test_talib_reference_catalog_is_complete():
    from nse_signal.features.talib_reference import all_functions
    names=all_functions()
    assert len(names) == len(set(names))
    # Current TA-Lib catalogue represented by this package: 5 cycle + 27? math
    # operator/transform + current non-pattern families + 61 candlestick patterns.
    assert len(names) == 223


def test_unsupported_ma_type_never_silently_falls_back():
    from nse_signal.features.indicators import macd
    with pytest.raises(ValueError):
        macd(frame(100).close, 12, 26, 9, 'mama')
