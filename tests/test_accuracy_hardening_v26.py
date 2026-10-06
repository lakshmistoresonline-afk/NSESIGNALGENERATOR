import numpy as np, pandas as pd
from nse_signal.features.build import make_features
from nse_signal.research.labels import triple_barrier_labels
from nse_signal.research.regime import add_regime_features
from nse_signal.models.walk_forward import walk_forward

def panel(n=180):
    ts=pd.date_range("2024-01-01",periods=n,freq="B",tz="UTC")
    rows=[]
    for j,s in enumerate(["AAA","BBB"]):
        c=100+j*10+np.arange(n)*.2+np.sin(np.arange(n)/7)
        rows.extend({"timestamp":ts[i],"symbol":s,"open":c[i],"high":c[i]+1,"low":c[i]-1,"close":c[i]+.1,"volume":100000+j*1000} for i in range(n))
    return pd.DataFrame(rows)

def test_panel_features_do_not_cross_symbols():
    d=panel(180)
    f=make_features(d)
    a=f[f.symbol=="AAA"].sort_values("timestamp").reset_index(drop=True)
    b=f[f.symbol=="BBB"].sort_values("timestamp").reset_index(drop=True)
    # A constant shift in BBB must not alter AAA's within-symbol rolling features.
    d2=d.copy(); d2.loc[d2.symbol=="BBB","close"]*=50
    f2=make_features(d2)
    a2=f2[f2.symbol=="AAA"].sort_values("timestamp").reset_index(drop=True)
    pd.testing.assert_series_equal(a["sma_20"],a2["sma_20"],check_names=False)

def test_market_regime_uses_explicit_benchmark():
    d=pd.DataFrame({"close":np.arange(300)+100,"benchmark_close":np.arange(300)+200})
    r=add_regime_features(d)
    assert r["market_context_source"].iloc[-1]=="benchmark:benchmark_close"
    assert np.isfinite(r["market_sma_200_gap"].iloc[-1])

def test_gap_through_barrier_uses_actual_open():
    idx=pd.date_range("2024-01-01",periods=8,freq="B")
    d=pd.DataFrame({"open":[100,100,94,94,94,94,94,94],
                    "high":[101,101,95,95,95,95,95,95],
                    "low":[99,99,93,93,93,93,93,93],
                    "close":[100,100,94,94,94,94,94,94],
                    "atr_14":[5]*8},index=idx)
    y=triple_barrier_labels(d,horizon=3,pt_atr=1,sl_atr=1)
    assert y.tb_event.iloc[0] in {"stop_gap_at_entry","stop_gap"}
    # The realized return must use the actual gap price (94), not the barrier (95).
    assert abs(y.tb_return.iloc[0] + .06)<1e-9
