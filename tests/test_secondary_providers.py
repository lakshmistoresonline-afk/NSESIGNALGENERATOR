import os
from datetime import datetime, timezone
import pandas as pd
import pytest

from nse_signal.data.providers.providers import _frame, YahooProvider, AngelOneProvider, GrowwProvider, DhanProvider, FyersProvider, UpstoxProvider, FivePaisaProvider
from nse_signal.data.providers.policy import assert_secondary_allowed


def test_frame_normalizes_candles():
    df = _frame([["2025-01-02T09:15:00+05:30", 1, 2, 0.5, 1.5, 100]])
    assert list(df.columns) == ["timestamp","open","high","low","close","volume"]
    assert len(df) == 1
    assert str(df.timestamp.iloc[0].tz) == "Asia/Kolkata"


def test_secondary_provider_policy_is_fail_closed(monkeypatch):
    monkeypatch.setenv("ALLOW_SECONDARY_PROVIDER", "false")
    with pytest.raises(RuntimeError):
        assert_secondary_allowed("yahoo")


def test_provider_names_and_non_execution_surface():
    assert {YahooProvider.name, AngelOneProvider.name, GrowwProvider.name, DhanProvider.name, FyersProvider.name, UpstoxProvider.name, FivePaisaProvider.name} == {"yahoo","angelone","groww","dhan","fyers","upstox","5paisa"}
    for cls in [YahooProvider, AngelOneProvider, GrowwProvider, DhanProvider, FyersProvider]:
        assert not hasattr(cls, "place_order")
        assert not hasattr(cls, "modify_order")
        assert not hasattr(cls, "cancel_order")


def test_yahoo_url_generation(monkeypatch):
    captured = {}
    def fake(url, **kwargs):
        captured["url"] = url
        return {"chart":{"result":[{"timestamp":[1735818300],"indicators":{"quote":[{"open":[1],"high":[2],"low":[0.5],"close":[1.5],"volume":[10]}]}}]}}, "application/json"
    monkeypatch.setattr("nse_signal.data.providers.providers.http_json", fake)
    r = YahooProvider().historical("RELIANCE", datetime(2025,1,1,tzinfo=timezone.utc), datetime(2025,1,3,tzinfo=timezone.utc))
    assert "RELIANCE.NS" in captured["url"]
    assert len(r.dataframe) == 1
    assert r.source_tier == "SECONDARY_UNOFFICIAL"


def test_angel_parser(monkeypatch):
    def fake(*args, **kwargs):
        return {"status": True, "data":[["2025-01-02T09:15:00+05:30",1,2,.5,1.5,100]]}, "application/json"
    monkeypatch.setattr("nse_signal.data.providers.providers.http_json", fake)
    r = AngelOneProvider("k","t").historical("SBIN", datetime(2025,1,2,tzinfo=timezone.utc), datetime(2025,1,3,tzinfo=timezone.utc), symbol_token="3045")
    assert len(r.dataframe) == 1


def test_yahoo_not_in_automatic_fallback():
    from nse_signal.data.providers.fallback import SecondaryFallback
    assert "yahoo" not in SecondaryFallback().order


def test_upstox_parser(monkeypatch):
    monkeypatch.setattr("nse_signal.data.providers.providers.http_json", lambda *a, **k: ({"data":{"candles":[[1735818300,1,2,.5,1.5,10]]}}, "application/json"))
    r=UpstoxProvider("token").historical("RELIANCE", datetime(2025,1,1,tzinfo=timezone.utc), datetime(2025,1,3,tzinfo=timezone.utc), instrument_key="NSE_EQ|INE002A01018")
    assert len(r.dataframe)==1


def test_5paisa_parser(monkeypatch):
    monkeypatch.setattr("nse_signal.data.providers.providers.http_json", lambda *a, **k: ({"body":{"candles":[{"Timestamp":"2025-01-02T09:15:00","Open":1,"High":2,"Low":.5,"Close":1.5,"Volume":10}]}}, "application/json"))
    r=FivePaisaProvider("token").historical("RELIANCE", datetime(2025,1,1,tzinfo=timezone.utc), datetime(2025,1,3,tzinfo=timezone.utc), scrip_code="2885")
    assert len(r.dataframe)==1


def test_fallback_filters_provider_specific_kwargs(monkeypatch):
    from nse_signal.data.providers.fallback import SecondaryFallback
    class P:
        def historical(self, symbol, start, end, interval="1d"):
            return type("R", (), {"dataframe": __import__("pandas").DataFrame({"timestamp":[start],"open":[1],"high":[1],"low":[1],"close":[1],"volume":[1]})})()
    f=SecondaryFallback(order=["dummy"])
    f.registry.providers={"dummy":P()}
    r,_=f.historical("X",datetime(2025,1,1,tzinfo=timezone.utc),datetime(2025,1,2,tzinfo=timezone.utc),instrument_key="unused")
    assert len(r.dataframe)==1


def test_reconcile_surfaces_price_disagreement():
    from nse_signal.data.providers.reconcile import reconcile_candles
    a=_frame([["2025-01-02T09:15:00+05:30",100,101,99,100,1000]])
    b=_frame([["2025-01-02T09:15:00+05:30",101,102,100,101,1000]])
    out=reconcile_candles(a,b,tolerance_bps=5)
    assert out["disagreement"] is True
