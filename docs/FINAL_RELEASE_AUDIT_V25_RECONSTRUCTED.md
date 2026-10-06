# V25 Reconstructed Release Audit

This release is reconstructed from the persisted V21 package and the documented V22–V25 hardening requirements after the original V25 binary became unavailable.

## Included hardening
- TejHQ and BharatStock secondary EOD adapters.
- Secondary-provider acquisition CLI includes both new providers.
- Explicit Upstox interval mapping for 1m/5m/15m/1h/2h/4h/1d/1w/1mo.
- Bounded retries, response-size limits, and per-host circuit breaker.
- OHLC/volume sanity rejection for malformed bars.
- Provider catalog/readiness endpoints.
- Android client changed to read-only health/readiness/provider monitoring.
- Android version 25.0.0.
- Signal-only safety boundary retained; no broker execution methods added.
- Authoritative PIT readiness remains fail-closed when licensed/effective-dated PIT datasets are absent.

## Data status
Secondary providers are convenience/research sources only. They do not become authoritative PIT evidence and cannot unlock production readiness by themselves.
