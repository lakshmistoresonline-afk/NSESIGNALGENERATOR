import numpy as np
import pandas as pd

def test_panel_regime_uses_one_window_per_timestamp():
    from nse_signal.research.regime import add_regime_features
    ts=pd.date_range("2020-01-01",periods=220,freq="D")
    rows=[]
    for sym in ["A","B","C"]:
        rows.append(pd.DataFrame({"timestamp":ts,"symbol":sym,"close":100+np.arange(len(ts))+ (1 if sym=="B" else 0),
                                  "return_1d":np.r_[np.nan,np.diff(np.arange(len(ts))+1)/(np.arange(len(ts)-1)+1)]}))
    x=pd.concat(rows,ignore_index=True)
    out=add_regime_features(x)
    # The 200-period market SMA must become available after 200 timestamps,
    # not after 200 repeated symbol rows.
    assert out.loc[out.timestamp==ts[199],"market_sma_200_gap"].notna().all()

def test_directional_timeout_policy_keeps_economic_timeouts():
    from nse_signal.research.labels import execution_consistent_target
    n=20
    close=np.linspace(100,102,n)
    d=pd.DataFrame({"open":close,"high":close+0.2,"low":close-0.2,"close":close,
                    "atr_14":np.full(n,10.0)})
    x=execution_consistent_target(d,horizon=3,pt_atr=10,sl_atr=10,timeout_policy="directional")
    assert x.target.notna().sum()>0

def test_broad_nse_universe_is_point_in_time_and_liquidity_filtered():
    from nse_signal.data.universe import broad_nse_equity_universe
    t=pd.Timestamp("2025-01-10",tz="UTC")
    sm=pd.DataFrame({"symbol":["AAA","BBB","CCC"],"series":["EQ","EQ","SM"]})
    dates=pd.date_range("2024-01-01",periods=130,freq="D",tz="UTC")
    rows=[]
    for s,v in [("AAA",10),("BBB",10),("CCC",10)]:
        rows.append(pd.DataFrame({"timestamp":dates,"symbol":s,"close":v,"volume":1_000_000 if s=="AAA" else 10}))
    bars=pd.concat(rows,ignore_index=True)
    assert broad_nse_equity_universe(sm,t,bars,min_price=5,min_median_dollar_volume=1_000_000,min_history_days=120)==[]

def test_champion_promotion_requires_governance_gate(tmp_path):
    from nse_signal.models.registry import ModelRegistry
    r=ModelRegistry(tmp_path/"r.json")
    r.register("m","hash",{"gate":{"pass":False}})
    r.transition("m","VALIDATED"); r.transition("m","PAPER")
    try:
        r.transition("m","CHAMPION")
        assert False
    except ValueError:
        pass
