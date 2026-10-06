
import numpy as np
import pandas as pd
import pytest

from nse_signal.features.build import make_labels
from nse_signal.data.universe import broad_nse_equity_universe, validate_membership_intervals
from nse_signal.research.validation import combinatorial_purged_panel_splits
from nse_signal.research.panel import add_market_structure_features

def panel():
    ts=pd.date_range("2024-01-01", periods=12, freq="D", tz="UTC")
    rows=[]
    for s,base in [("AAA",100),("BBB",200),("CCC",300)]:
        for i,t in enumerate(ts):
            c=base+i+(0.1 if s=="BBB" else 0)
            rows.append({"timestamp":t,"symbol":s,"close":c,"open":c,"high":c+1,"low":c-1,
                         "volume":10000,"return_1d":0.01 if i%2 else -0.005,
                         "nifty_return":0.002 if i%3 else -0.001,"sector":"IT" if s!="CCC" else "BANK"})
    return pd.DataFrame(rows)

def test_panel_labels_never_cross_symbols():
    x=panel()
    y=make_labels(x,horizon=2)
    for s,g in y.sort_values(["symbol","timestamp"]).groupby("symbol"):
        expected=g.close.shift(-2)/g.close-1
        assert np.allclose(g.future_return.dropna(), expected.dropna())

def test_panel_cpcv_keeps_timestamps_disjoint():
    x=panel()
    splits=combinatorial_purged_panel_splits(x.timestamp,n_groups=4,test_groups=1,purge_bars=1,embargo_bars=1)
    for sp in splits:
        assert set(x.iloc[sp.train].timestamp).isdisjoint(set(x.iloc[sp.test].timestamp))

def test_market_structure_has_one_breadth_value_per_timestamp():
    out=add_market_structure_features(panel())
    n=out.groupby("timestamp").market_breadth_up_share.nunique(dropna=True)
    assert (n<=1).all()
    assert "market_return_dispersion" in out

def test_membership_overlap_rejected():
    x=pd.DataFrame({
        "symbol":["AAA","AAA"],
        "effective_from":pd.to_datetime(["2024-01-01","2024-06-01"],utc=True),
        "effective_to":pd.to_datetime(["2024-12-31","2025-01-01"],utc=True)
    })
    with pytest.raises(ValueError):
        validate_membership_intervals(x)

def test_universe_rejects_stale_security():
    sm=pd.DataFrame({"symbol":["AAA"],"series":["EQ"],
                     "effective_from":pd.to_datetime(["2024-01-01"],utc=True),
                     "effective_to":pd.to_datetime([None],utc=True)})
    bars=pd.DataFrame({"symbol":["AAA"]*120,"timestamp":pd.date_range("2024-01-01",periods=120,tz="UTC"),
                       "close":[100]*120,"volume":[10000]*120})
    assert broad_nse_equity_universe(sm,pd.Timestamp("2025-01-01",tz="UTC"),bars,min_history_days=120,max_staleness_days=10)==[]
