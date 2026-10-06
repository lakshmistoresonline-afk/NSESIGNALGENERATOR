from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError

_MAX_RESPONSE_BYTES = int(__import__("os").getenv("PROVIDER_MAX_RESPONSE_BYTES", "10000000"))
_FAILURES = {}
_BREAKER_UNTIL = {}

@dataclass(frozen=True)
class ProviderResult:
    provider: str
    symbol: str
    dataframe: object
    retrieved_at: str
    source_url: str
    source_tier: str = "SECONDARY"
    license_status: str = "USER_ACCOUNT_TERMS"
    pit_authoritative: bool = False
    candle_timestamp_semantics: str = "candle_start"
    availability_semantics: str = "retrieval_time_only"

class ProviderError(RuntimeError):
    pass

def http_json(url: str, *, method="GET", headers=None, body=None, timeout=30, retries=3, backoff=0.75):
    """Small dependency-free HTTP client with bounded retry/backoff.

    Retries only transient failures (429/5xx/timeouts). Authentication and
    validation errors fail immediately so provider credentials are not hammered.
    """
    import time as _time
    host = url.split('/')[2] if '://' in url else url
    now = _time.time()
    if _BREAKER_UNTIL.get(host, 0) > now:
        raise ProviderError(f"Circuit breaker open for {host}")
    last = None
    for attempt in range(max(1, retries)):
        req = Request(url, method=method, headers=headers or {})
        if body is not None:
            req.data = json.dumps(body).encode()
            req.add_header("Content-Type", "application/json")
        try:
            with urlopen(req, timeout=timeout) as r:
                raw = r.read(_MAX_RESPONSE_BYTES + 1)
                if len(raw) > _MAX_RESPONSE_BYTES:
                    raise ProviderError(f"Provider response exceeds {_MAX_RESPONSE_BYTES} bytes")
                _FAILURES[host] = 0
                return json.loads(raw.decode("utf-8")), r.headers.get("Content-Type", "")
        except HTTPError as exc:
            last = exc
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retries - 1:
                _FAILURES[host] = _FAILURES.get(host, 0) + 1
                if _FAILURES[host] >= 3: _BREAKER_UNTIL[host] = _time.time() + 60
                raise ProviderError(f"HTTP {exc.code} for {url}") from exc
        except Exception as exc:
            last = exc
            if isinstance(exc, ProviderError): raise
            if attempt == retries - 1:
                _FAILURES[host] = _FAILURES.get(host, 0) + 1
                if _FAILURES[host] >= 3: _BREAKER_UNTIL[host] = _time.time() + 60
                raise ProviderError(f"HTTP request failed for {url}: {exc}") from exc
        _time.sleep(backoff * (2 ** attempt))
    raise ProviderError(f"HTTP request failed for {url}: {last}")

def epoch(dt):
    return int(dt.timestamp())

def iso_now():
    return datetime.now(timezone.utc).isoformat()

def save_with_provenance(df, path, result: ProviderResult, request_params: dict):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    meta = {
        "provider": result.provider,
        "symbol": result.symbol,
        "retrieved_at": result.retrieved_at,
        "source_url": result.source_url,
        "source_tier": result.source_tier,
        "license_status": result.license_status,
        "request": request_params,
        "sha256": digest,
        "pit_authoritative": False,
        "execution_capability_used": False,
        "data_availability_semantics": result.availability_semantics,
        "candle_timestamp_semantics": result.candle_timestamp_semantics,
        "pit_authoritative": result.pit_authoritative,
    }
    path.with_suffix(path.suffix + ".metadata.json").write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")
    return path, meta
