import io, zipfile, pandas as pd
from nse_signal.data.nse.archives import cm_bhavcopy_url, fo_bhavcopy_url
from nse_signal.data.nse.normalize import normalize_cash
from nse_signal.data.nse.membership import membership_asof, assert_no_overlap
from nse_signal.data.provenance import validate_asof_data

def test_official_archive_url_contract():
    from datetime import date
    assert cm_bhavcopy_url(date(2026,9,25)).endswith('BhavCopy_NSE_CM_0_0_0_20260925_F_0000.csv.zip')
    assert fo_bhavcopy_url(date(2026,9,25)).endswith('BhavCopy_NSE_FO_0_0_0_20260925_F_0000.csv.zip')

def test_udiff_cash_normalization():
    import tempfile, os
    raw=pd.DataFrame({'TckrSymb':['ABC'],'SctySrs':['EQ'],'TradDt':['2026-09-25'],'OpnPric':[100],'HghPric':[105],'LwPric':[99],'ClsPric':[104],'TtlTradgVol':[1000]})
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w') as z: z.writestr('x.csv',raw.to_csv(index=False))
    fd, p = tempfile.mkstemp(suffix='.zip')
    os.close(fd)
    try:
        with open(p,'wb') as f:
            f.write(b.getvalue())
        x=normalize_cash(p)
        assert list(x[['symbol','open','high','low','close','volume']].iloc[0])==['ABC',100,105,99,104,1000]
        assert validate_asof_data(x[['signal_time','asof_time']]).get('pass') is True
    finally:
        try:
            os.unlink(p)
        except:
            pass

def test_membership_asof():
    m=pd.DataFrame({'symbol':['A','A','B'],'effective_from':pd.to_datetime(['2020-01-01','2021-01-01','2020-01-01']),'effective_to':pd.to_datetime(['2020-12-31',None,None])})
    assert set(membership_asof(m,'2020-06-01').symbol)=={'A','B'}
    assert set(membership_asof(m,'2022-01-01').symbol)=={'A','B'}
    assert assert_no_overlap(m)

def test_delivery_breadth_vix_adapters(tmp_path):
    from nse_signal.data.nse.pit_layers import normalize_delivery, normalize_breadth, normalize_vix
    p=tmp_path/'d.csv'; pd.DataFrame({'SYMBOL':['ABC'],'DATE':['2026-09-25'],'DELIV_QTY':['500'],'DELIV_PER':['50.0'],'TOTTRDQTY':['1000']}).to_csv(p,index=False)
    x=normalize_delivery(p); assert x.iloc[0].delivery_pct==50.0; assert x.iloc[0].asof_time <= x.iloc[0].signal_time
    b=tmp_path/'b.csv'; pd.DataFrame({'DATE':['2026-09-25'],'ADVANCES':[1200],'DECLINES':[800],'UNCHANGED':[100]}).to_csv(b,index=False)
    y=normalize_breadth(b); assert y.iloc[0].ad_ratio==1.5 and y.iloc[0].symbol=='__MARKET__'
    v=tmp_path/'v.csv'; pd.DataFrame({'DATE':['2026-09-25'],'OPEN':[12],'HIGH':[13],'LOW':[11],'CLOSE':[12.5]}).to_csv(v,index=False)
    z=normalize_vix(v); assert z.iloc[0].symbol=='__INDIA_VIX__'


def test_corporate_event_date_only_rejected(tmp_path):
    from nse_signal.data.nse.pit_layers import normalize_corporate_events
    p=tmp_path/'c.csv'; pd.DataFrame({'SYMBOL':['ABC'],'PURPOSE':['Results'],'Broadcast Date':['2026-09-25']}).to_csv(p,index=False)
    try: normalize_corporate_events(p)
    except ValueError as e: assert 'date-only' in str(e)
    else: raise AssertionError('date-only corporate event was accepted')


def test_fundamentals_require_availability_timestamp(tmp_path):
    from nse_signal.data.nse.pit_layers import normalize_pit_fundamentals
    p=tmp_path/'f.csv'; pd.DataFrame({'symbol':['ABC'],'period_end':['2026-06-30'],'eps':[5]}).to_csv(p,index=False)
    try: normalize_pit_fundamentals(p)
    except ValueError as e: assert 'available_at' in str(e)
    else: raise AssertionError('fundamentals without availability timestamp were accepted')
