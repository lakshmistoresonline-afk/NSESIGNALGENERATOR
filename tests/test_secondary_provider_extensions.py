from datetime import datetime, timezone
from nse_signal.data.providers.providers import AngelOneProvider, GrowwProvider


def test_angel_oi_is_data_only(monkeypatch):
    monkeypatch.setattr("nse_signal.data.providers.providers.http_json", lambda *a, **k: ({"status":True,"data":[{"time":"2025-01-02T09:15:00+05:30","oi":100}]}, "application/json"))
    df=AngelOneProvider("k","t").historical_oi("1",datetime(2025,1,2,tzinfo=timezone.utc),datetime(2025,1,3,tzinfo=timezone.utc))
    assert list(df.columns)==["time","oi"]


def test_groww_derivative_discovery(monkeypatch):
    monkeypatch.setattr("nse_signal.data.providers.providers.http_json", lambda *a, **k: ({"status":"SUCCESS","payload":{"expiries":["2025-01-30"]}}, "application/json"))
    assert GrowwProvider("t").expiries("NIFTY",2025)==["2025-01-30"]
