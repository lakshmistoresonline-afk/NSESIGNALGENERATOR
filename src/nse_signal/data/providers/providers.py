from __future__ import annotations
import os
from datetime import datetime, date, timedelta, timezone
import pandas as pd
from .base import ProviderError, ProviderResult, epoch, http_json, iso_now

COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]

def _frame(rows, tz="Asia/Kolkata"):
    if not rows:
        return pd.DataFrame(columns=COLUMNS)
    df = pd.DataFrame(rows, columns=COLUMNS)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce").dt.tz_convert(tz)
    for c in COLUMNS[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["timestamp", "open", "high", "low", "close"])
    if (df[["open","high","low","close"]] <= 0).any().any(): raise ProviderError("Malformed OHLC: non-positive price")
    if (df["high"] < df[["open","close","low"]].max(axis=1)).any(): raise ProviderError("Malformed OHLC: high below component")
    if (df["low"] > df[["open","close","high"]].min(axis=1)).any(): raise ProviderError("Malformed OHLC: low above component")
    if (df["volume"].dropna() < 0).any(): raise ProviderError("Malformed volume: negative value")
    return df.drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)

class YahooProvider:
    """Yahoo Finance chart endpoint. Unofficial/secondary; not for PIT licensing."""
    name = "yahoo"
    source_tier = "SECONDARY_UNOFFICIAL"
    license_status = "PUBLIC_ENDPOINT_TERMS_REVIEW_REQUIRED"
    def historical(self, symbol, start, end, interval="1d"):
        ysymbol = symbol if symbol.endswith(".NS") or symbol.endswith(".BO") else f"{symbol}.NS"
        p = {"period1": epoch(start), "period2": epoch(end), "interval": interval, "events": "history", "includeAdjustedClose": "true"}
        url = "https://query1.finance.yahoo.com/v8/finance/chart/" + ysymbol + "?" + __import__("urllib.parse").parse.urlencode(p)
        data, _ = http_json(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            r = data["chart"]["result"][0]
            q = r["indicators"]["quote"][0]
            rows = [[datetime.fromtimestamp(ts, timezone.utc).isoformat(), q["open"][i], q["high"][i], q["low"][i], q["close"][i], q.get("volume", [None]*len(r["timestamp"]))[i]] for i, ts in enumerate(r["timestamp"])]
        except Exception as exc:
            raise ProviderError(f"Yahoo response malformed for {symbol}: {exc}") from exc
        return ProviderResult(self.name, symbol, _frame(rows), iso_now(), url, self.source_tier, self.license_status)

class AngelOneProvider:
    name = "angelone"
    source_tier = "SECONDARY_BROKER_API"
    license_status = "ANGELONE_USER_API_TERMS"
    url = "https://apiconnect.angelone.in/rest/secure/angelbroking/historical/v1/getCandleData"
    interval_map = {"1m":"ONE_MINUTE","3m":"THREE_MINUTE","5m":"FIVE_MINUTE","10m":"TEN_MINUTE","15m":"FIFTEEN_MINUTE","30m":"THIRTY_MINUTE","1h":"ONE_HOUR","1d":"ONE_DAY"}
    def __init__(self, api_key=None, auth_token=None):
        self.api_key = api_key or os.getenv("ANGELONE_API_KEY")
        self.auth_token = auth_token or os.getenv("ANGELONE_AUTH_TOKEN")
    def historical(self, symbol, start, end, interval="1d", symbol_token=None, exchange="NSE"):
        if not self.api_key or not self.auth_token or not symbol_token:
            raise ProviderError("Angel One requires ANGELONE_API_KEY, ANGELONE_AUTH_TOKEN and ANGELONE_SYMBOL_TOKEN")
        body = {"exchange": exchange, "symboltoken": str(symbol_token), "interval": self.interval_map[interval], "fromdate": start.strftime("%Y-%m-%d %H:%M"), "todate": end.strftime("%Y-%m-%d %H:%M")}
        headers = {"X-PrivateKey": self.api_key, "Authorization": f"Bearer {self.auth_token}", "X-UserType":"USER", "X-SourceID":"WEB", "X-ClientLocalIP":"127.0.0.1", "X-ClientPublicIP":"", "X-MACAddress":"", "Accept":"application/json"}
        data, _ = http_json(self.url, method="POST", headers=headers, body=body)
        if not data.get("status"):
            raise ProviderError(data.get("message") or data.get("errorcode") or "Angel One historical request failed")
        rows = data.get("data") or []
        return ProviderResult(self.name, symbol, _frame(rows), iso_now(), self.url, self.source_tier, self.license_status)

class GrowwProvider:
    name = "groww"
    source_tier = "SECONDARY_BROKER_API"
    license_status = "GROWW_API_SUBSCRIPTION_TERMS"
    url = "https://api.groww.in/v1/historical/candles"
    def __init__(self, access_token=None): self.access_token = access_token or os.getenv("GROWW_ACCESS_TOKEN")
    def historical(self, symbol, start, end, interval="1d", groww_symbol=None, segment="CASH"):
        if not self.access_token: raise ProviderError("Groww requires GROWW_ACCESS_TOKEN")
        groww_symbol = groww_symbol or (f"NSE-{symbol}" if not symbol.startswith("NSE-") else symbol)
        params = {"exchange":"NSE", "segment":segment, "groww_symbol":groww_symbol, "start_time":start.strftime("%Y-%m-%d %H:%M:%S"), "end_time":end.strftime("%Y-%m-%d %H:%M:%S"), "candle_interval":interval}
        url = self.url + "?" + __import__("urllib.parse").parse.urlencode(params)
        data, _ = http_json(url, headers={"Authorization":f"Bearer {self.access_token}","X-API-VERSION":"1.0","Accept":"application/json"})
        if data.get("status") != "SUCCESS": raise ProviderError(str(data))
        rows = data.get("payload", {}).get("candles", [])
        rows = [[(datetime.fromtimestamp(r[0], timezone.utc).isoformat() if isinstance(r[0], (int,float)) else r[0]), *r[1:6]] for r in rows]
        return ProviderResult(self.name, symbol, _frame(rows), iso_now(), url, self.source_tier, self.license_status)

class DhanProvider:
    name = "dhan"
    source_tier = "SECONDARY_BROKER_API"
    license_status = "DHAN_USER_API_TERMS"
    url = "https://api.dhan.co/v2/charts/historical"
    def __init__(self, access_token=None): self.access_token = access_token or os.getenv("DHAN_ACCESS_TOKEN")
    def historical(self, symbol, start, end, security_id=None, exchange_segment="NSE_EQ", instrument="EQUITY"):
        if not self.access_token or not security_id: raise ProviderError("Dhan requires DHAN_ACCESS_TOKEN and security_id")
        body = {"securityId":str(security_id),"exchangeSegment":exchange_segment,"instrument":instrument,"expiryCode":0,"oi":False,"fromDate":start.strftime("%Y-%m-%d"),"toDate":end.strftime("%Y-%m-%d")}
        data, _ = http_json(self.url, method="POST", headers={"access-token":self.access_token,"Content-Type":"application/json"}, body=body)
        # Dhan returns column-oriented arrays in its API.
        ts = data.get("timestamp") or data.get("time") or []
        rows = []
        for i, t in enumerate(ts):
            rows.append([datetime.fromtimestamp(int(t), timezone.utc).isoformat(), data.get("open",[])[i], data.get("high",[])[i], data.get("low",[])[i], data.get("close",[])[i], data.get("volume",[])[i] if data.get("volume") else None])
        return ProviderResult(self.name, symbol, _frame(rows), iso_now(), self.url, self.source_tier, self.license_status)

class FyersProvider:
    name = "fyers"
    source_tier = "SECONDARY_BROKER_API"
    license_status = "FYERS_USER_API_TERMS"
    url = "https://api-t1.fyers.in/data/history"
    def __init__(self, access_token=None): self.access_token = access_token or os.getenv("FYERS_ACCESS_TOKEN")
    def historical(self, symbol, start, end, resolution="D"):
        if not self.access_token: raise ProviderError("FYERS requires FYERS_ACCESS_TOKEN")
        fyers_symbol = symbol if ":" in symbol else f"NSE:{symbol}-EQ"
        params = {"symbol":fyers_symbol,"resolution":resolution,"date_format":"1","range_from":start.strftime("%Y-%m-%d"),"range_to":end.strftime("%Y-%m-%d"),"cont_flag":"1"}
        url = self.url + "?" + __import__("urllib.parse").parse.urlencode(params)
        data, _ = http_json(url, headers={"Authorization":self.access_token,"User-Agent":"nse-signal-provider"})
        if data.get("s") not in ("ok", "no_data"): raise ProviderError(str(data))
        rows = [[datetime.fromtimestamp(r[0], timezone.utc).isoformat(), *r[1:6]] for r in data.get("candles", [])]
        return ProviderResult(self.name, symbol, _frame(rows), iso_now(), url, self.source_tier, self.license_status)


class UpstoxProvider:
    """Upstox V3 read-only historical market-data adapter."""
    name = "upstox"
    source_tier = "SECONDARY_BROKER_API"
    license_status = "UPSTOX_ANALYTICS_TOKEN_TERMS"
    url = "https://api.upstox.com/v3/historical-candle"
    def __init__(self, access_token=None):
        self.access_token = access_token or os.getenv("UPSTOX_ANALYTICS_TOKEN") or os.getenv("UPSTOX_ACCESS_TOKEN")
    def historical(self, symbol, start, end, interval="1d", instrument_key=None):
        if not self.access_token or not instrument_key:
            raise ProviderError("Upstox requires UPSTOX_ANALYTICS_TOKEN and instrument_key")
        interval_map = {"1m": ("minutes", "1"), "5m": ("minutes", "5"), "15m": ("minutes", "15"), "1h": ("hours", "1"), "2h": ("hours", "2"), "4h": ("hours", "4"), "1d": ("days", "1"), "1w": ("weeks", "1"), "1mo": ("months", "1"), "D": ("days", "1"), "W": ("weeks", "1")}
        if interval not in interval_map:
            raise ProviderError(f"Unsupported Upstox interval: {interval}")
        unit, iv = interval_map[interval]
        to_date = end.astimezone(timezone.utc).date().isoformat()
        from_date = start.astimezone(timezone.utc).date().isoformat()
        url = f"{self.url}/{__import__('urllib.parse').parse.quote(instrument_key, safe='')}/{unit}/{iv}/{to_date}/{from_date}"
        data, _ = http_json(url, headers={"Authorization": f"Bearer {self.access_token}", "Accept": "application/json"})
        candles = data.get("data", {}).get("candles", [])
        rows = [[datetime.fromtimestamp(r[0], timezone.utc).isoformat(), *r[1:6]] for r in candles]
        return ProviderResult(self.name, symbol, _frame(rows), iso_now(), url, self.source_tier, self.license_status)


class FivePaisaProvider:
    """5paisa Xstream read-only historical-candle adapter."""
    name = "5paisa"
    source_tier = "SECONDARY_BROKER_API"
    license_status = "5PAISA_XSTREAM_API_TERMS"
    base_url = "https://openapi.5paisa.com/V2/historical"
    def __init__(self, access_token=None):
        self.access_token = access_token or os.getenv("FIVEPAISA_ACCESS_TOKEN")
    def historical(self, symbol, start, end, interval="1d", scrip_code=None, exchange="N", exchange_type="C"):
        if not self.access_token or not scrip_code:
            raise ProviderError("5paisa requires FIVEPAISA_ACCESS_TOKEN and scrip_code")
        iv = {"1m":"1m","5m":"5m","10m":"10m","15m":"15m","30m":"30m","1h":"60m","1d":"1d"}.get(interval, interval)
        url = f"{self.base_url}/{exchange}/{exchange_type}/{scrip_code}/{iv}?from={start.strftime('%Y-%m-%d')}&end={end.strftime('%Y-%m-%d')}"
        data, _ = http_json(url, headers={"Authorization": f"bearer {self.access_token}", "Content-Type":"application/json"})
        candles = data.get("body", {}).get("candles", data.get("data", {}).get("candles", []))
        rows = []
        for r in candles:
            rows.append([r.get("Timestamp") if isinstance(r, dict) else r[0],
                         r.get("Open") if isinstance(r, dict) else r[1],
                         r.get("High") if isinstance(r, dict) else r[2],
                         r.get("Low") if isinstance(r, dict) else r[3],
                         r.get("Close") if isinstance(r, dict) else r[4],
                         r.get("Volume") if isinstance(r, dict) else r[5]])
        return ProviderResult(self.name, symbol, _frame(rows), iso_now(), url, self.source_tier, self.license_status)

# Optional derivatives-specific methods are attached as explicit data-only operations.
def _angel_oi(self, symbol_token, start, end, interval="ONE_DAY", exchange="NFO"):
    if not self.api_key or not self.auth_token or not symbol_token:
        raise ProviderError("Angel One OI requires ANGELONE_API_KEY, ANGELONE_AUTH_TOKEN and symbol token")
    body={"exchange":exchange,"symboltoken":str(symbol_token),"interval":interval,"fromdate":start.strftime("%Y-%m-%d %H:%M"),"todate":end.strftime("%Y-%m-%d %H:%M")}
    headers={"X-PrivateKey":self.api_key,"Authorization":f"Bearer {self.auth_token}","X-UserType":"USER","X-SourceID":"WEB","X-ClientLocalIP":"127.0.0.1","X-ClientPublicIP":"","X-MACAddress":"","Accept":"application/json"}
    data,_=http_json("https://apiconnect.angelone.in/rest/secure/angelbroking/historical/v1/getOIData",method="POST",headers=headers,body=body)
    if not data.get("status"): raise ProviderError(data.get("message") or "Angel One OI request failed")
    return pd.DataFrame(data.get("data") or [])
AngelOneProvider.historical_oi = _angel_oi


def _groww_expiries(self, underlying_symbol, year, month=None):
    if not self.access_token: raise ProviderError("Groww requires GROWW_ACCESS_TOKEN")
    params={"exchange":"NSE","underlying_symbol":underlying_symbol,"year":year}
    if month is not None: params["month"]=month
    url="https://api.groww.in/v1/historical/expiries?"+__import__("urllib.parse").parse.urlencode(params)
    data,_=http_json(url,headers={"Authorization":f"Bearer {self.access_token}","X-API-VERSION":"1.0","Accept":"application/json"})
    if data.get("status")!="SUCCESS": raise ProviderError(str(data))
    return data.get("payload",{}).get("expiries",[])
GrowwProvider.expiries = _groww_expiries


def _groww_contracts(self, underlying_symbol, expiry_date):
    if not self.access_token: raise ProviderError("Groww requires GROWW_ACCESS_TOKEN")
    params={"exchange":"NSE","underlying_symbol":underlying_symbol,"expiry_date":expiry_date}
    url="https://api.groww.in/v1/historical/contracts?"+__import__("urllib.parse").parse.urlencode(params)
    data,_=http_json(url,headers={"Authorization":f"Bearer {self.access_token}","X-API-VERSION":"1.0","Accept":"application/json"})
    if data.get("status")!="SUCCESS": raise ProviderError(str(data))
    return data.get("payload",{}).get("contracts",[])
GrowwProvider.contracts = _groww_contracts


class TejHQProvider:
    """Keyless/low-friction NSE-derived EOD provider. Secondary only."""
    name = "tejhq"
    source_tier = "SECONDARY_NSE_DERIVED"
    license_status = "TEJHQ_TERMS_AND_DATASET_LICENSE"
    base_url = "https://api.tejhq.dev/v1"
    def __init__(self, api_key=None): self.api_key = api_key or os.getenv("TEJHQ_API_KEY")
    def historical(self, symbol, start, end, interval="1d"):
        if interval not in ("1d", "D"):
            raise ProviderError("TejHQ adapter supports EOD interval 1d only")
        url = f"{self.base_url}/ohlcv/NSE/{symbol.upper()}"
        params = {"from": start.strftime("%Y-%m-%d"), "to": end.strftime("%Y-%m-%d")}
        if self.api_key: params["api_key"] = self.api_key
        url = url + "?" + __import__('urllib.parse').parse.urlencode(params)
        headers = {"Accept":"application/json"}
        data, _ = http_json(url, headers=headers)
        rows = data.get("data", data.get("results", data if isinstance(data, list) else []))
        normalized=[]
        for r in rows or []:
            if isinstance(r, dict):
                ts=r.get("timestamp",r.get("date",r.get("datetime")))
                normalized.append([ts,r.get("open",r.get("Open")),r.get("high",r.get("High")),r.get("low",r.get("Low")),r.get("close",r.get("Close")),r.get("volume",r.get("Volume"))])
            elif isinstance(r,(list,tuple)) and len(r)>=6:
                normalized.append(list(r[:6]))
        return ProviderResult(self.name, symbol, _frame(normalized), iso_now(), url, self.source_tier, self.license_status)

class BharatStockProvider:
    """BharatStock API secondary provider. Usage is subject to its plan/terms."""
    name = "bharatstock"
    source_tier = "SECONDARY_MARKET_API"
    license_status = "BHARATSTOCK_API_TERMS"
    base_url = "https://api.bharatstockapi.com"
    def __init__(self, api_key=None): self.api_key = api_key or os.getenv("BHARATSTOCK_API_KEY")
    def historical(self, symbol, start, end, interval="1d"):
        if not self.api_key: raise ProviderError("BharatStock requires BHARATSTOCK_API_KEY")
        if interval not in ("1d","D"): raise ProviderError("BharatStock adapter supports EOD interval 1d only")
        url = self.base_url + "/api/v1/equity/history"
        params = {"symbol":symbol.upper(),"from":start.strftime("%Y-%m-%d"),"to":end.strftime("%Y-%m-%d"),"interval":"1d"}
        url += "?" + __import__('urllib.parse').parse.urlencode(params)
        data,_=http_json(url,headers={"X-API-KEY":self.api_key,"Authorization":f"Bearer {self.api_key}","Accept":"application/json"})
        rows=data.get("data",data.get("results",[])) if isinstance(data,dict) else data
        normalized=[]
        for r in rows or []:
            if isinstance(r,dict): normalized.append([r.get("timestamp",r.get("date")),r.get("open"),r.get("high"),r.get("low"),r.get("close"),r.get("volume")])
            elif isinstance(r,(list,tuple)) and len(r)>=6: normalized.append(list(r[:6]))
        return ProviderResult(self.name,symbol,_frame(normalized),iso_now(),url,self.source_tier,self.license_status)
