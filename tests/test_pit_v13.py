import pandas as pd
import numpy as np
from nse_signal.data.nse.derivatives import build_derivatives_context
from nse_signal.data.nse.pit_quality import dedupe_latest, audit_pit_frame
from nse_signal.data.nse.membership import load_membership
from nse_signal.research.cross_sectional import cross_sectional_features
from nse_signal.signals.engine import SignalEngine


def test_derivatives_context_pcr_and_iv():
    fo=pd.DataFrame([
        {'date':'2026-09-01','symbol':'ABC','expiry':'2026-09-24','option_type':'CE','strike':100,'close':5,'volume':100,'oi':1000,'oi_change':100,'iv':20},
        {'date':'2026-09-01','symbol':'ABC','expiry':'2026-09-24','option_type':'PE','strike':100,'close':6,'volume':200,'oi':1500,'oi_change':150,'iv':25},
    ])
    x=build_derivatives_context(fo)
    assert np.isclose(x.iloc[0].pcr_oi,1.5)
    assert np.isclose(x.iloc[0].pcr_volume,2.0)
    assert x.iloc[0].iv_skew_put_minus_call > 0


def test_cross_sectional_rejects_unavailable_rows():
    x=pd.DataFrame({'timestamp':pd.to_datetime(['2026-01-01 15:30Z','2026-01-01 15:30Z']), 'symbol':['A','B'], 'return_1d':[.01,.02], 'asof_time':pd.to_datetime(['2026-01-01 15:00Z','2026-01-01 16:00Z'])})
    try: cross_sectional_features(x)
    except ValueError: return
    assert False


def test_dedupe_latest():
    x=pd.DataFrame({'symbol':['A','A'],'date':['2026-01-01','2026-01-01'],'asof_time':pd.to_datetime(['2026-01-01 10:00Z','2026-01-01 11:00Z']),'v':[1,2]})
    y=dedupe_latest(x,['symbol','date']); assert len(y)==1 and y.iloc[0].v==2


def test_restriction_gates_fail_closed():
    e=SignalEngine()
    assert e.generate('A',.8,.8,price=100,atr=2,restricted=True) is None
    assert e.generate('A',.8,.8,price=100,atr=2,near_price_band=True) is None
    assert e.generate('A',.2,.8,price=100,atr=2,short_sale_blocked=True) is None
    assert e.generate('A',.8,.8,price=100,atr=2,impact_cost_bps=150) is None

def test_membership_empty_is_not_production_valid(tmp_path):
    p=tmp_path/'m.csv'; p.write_text('symbol,effective_from,effective_to,source,source_asof\n')
    try: load_membership(p)
    except ValueError: return
    assert False


def test_derivatives_futures_basis():
    from nse_signal.data.nse.derivatives import build_derivatives_context
    fo=pd.DataFrame([
        {'date':'2026-09-01','symbol':'ABC','expiry':'2026-09-24','option_type':'CE','strike':100,'close':5,'volume':100,'oi':1000,'oi_change':100},
        {'date':'2026-09-01','symbol':'ABC','expiry':'2026-09-24','option_type':'FUT','strike':0,'close':102,'volume':100,'oi':1000,'oi_change':100},
    ])
    spot=pd.DataFrame([{'date':'2026-09-01','symbol':'ABC','close':100}])
    x=build_derivatives_context(fo,spot)
    assert np.isclose(x.iloc[0].futures_basis,.02)


def test_stale_rows_fail_pit_quality():
    import pandas as pd
    from nse_signal.data.nse.pit_quality import audit_pit_frame
    df = pd.DataFrame({
        'symbol':['ABC'],
        'signal_time':['2026-10-03T09:15:00Z'],
        'asof_time':['2026-10-01T09:15:00Z'],
    })
    report = audit_pit_frame(df, key_cols=['symbol'], max_stale_days=1)
    assert report['stale_rows'] == 1
    assert report['pass'] is False
