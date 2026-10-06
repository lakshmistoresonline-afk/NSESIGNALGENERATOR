"""Read-only NSE web data client for current snapshots with structured error handling.

This client never places orders. NSE may change/limit public web endpoints; callers
must respect NSE terms and use licensed/paid feeds when their latency or redistribution
requirements require them.
"""
from __future__ import annotations
import json, time, urllib.parse, urllib.request

class NSEDataError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code

class NSEReadOnlyClient:
    base = "https://www.nseindia.com"
    def __init__(self, timeout=20):
        self.timeout = timeout
        self.cookies = {}
        self._prime()

    def _prime(self):
        req = urllib.request.Request(self.base, headers={"User-Agent":"Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                for k,v in r.headers.items():
                    if k.lower() == "set-cookie": self.cookies[k] = v.split(';',1)[0]
        except Exception as exc:
            # Structured error classification rather than silent pass
            raise NSEDataError("UNAVAILABLE", f"Failed to connect and prime cookies from NSE base URL: {exc}") from exc

    def get_json(self, path: str, params: dict | None = None):
        q = urllib.parse.urlencode(params or {})
        url = self.base + path + ("?" + q if q else "")
        headers = {"User-Agent":"Mozilla/5.0 (compatible; NSE-Signal-Research/1.0)", "Accept":"application/json,text/plain,*/*", "Referer":self.base + "/"}
        if self.cookies: headers["Cookie"] = "; ".join(self.cookies.values())
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=self.timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as he:
            raise NSEDataError("HTTP_ERROR", f"NSE HTTP Error {he.code}: {he.reason}") from he
        except Exception as exc:
            raise NSEDataError("MALFORMED_OR_TIMEOUT", f"Failed to retrieve JSON from NSE endpoint {path}: {exc}") from exc

    def nifty200(self):
        return self.get_json("/api/equity-stockIndices", {"index":"NIFTY 200"})

    def option_chain(self, symbol: str):
        return self.get_json("/api/option-chain-equities", {"symbol":symbol})

    def equity_quote(self, symbol: str):
        return self.get_json("/api/quote-equity", {"symbol":symbol})

    def index_quote(self, index: str = "NIFTY 200"):
        return self.get_json("/api/equity-stockIndices", {"index":index})
