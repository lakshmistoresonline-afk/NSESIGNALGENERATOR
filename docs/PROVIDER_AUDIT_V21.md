# Provider and Release Audit — V21

## Free secondary sources

- Upstox Analytics Token / Historical Candle V3: free, read-only analytics token; historical daily data from 2000 and minute/hour data from 2022 according to current official documentation.
- 5paisa Xstream: free market-data system and historical candles.
- Angel One SmartAPI: historical NSE/NFO candles and historical OI are available through SmartAPI.
- FYERS: historical/quotes/market data are free for FYERS clients.

## Non-free / restricted sources

- Dhan: current pricing lists Data APIs at ₹499, while Trading APIs are free.
- Groww: current API is subscription-based; historical F&O data is available from 2020.
- Yahoo: explicit/manual only; excluded from automatic fallback because current Yahoo terms restrict automated collection and commercial reuse without permission.

## Safety

All provider adapters expose data retrieval only. They do not expose order placement, modification or cancellation. Secondary data is never treated as PIT-authoritative. Retrieval time is not substituted for historical publication/availability time.

## Reliability

- bounded retry/backoff for transient HTTP failures
- provider-specific argument filtering in fallback
- deterministic provenance sidecars
- SHA-256 hashes
- provider capability catalog
- cross-provider OHLCV reconciliation diagnostics
- automatic fallback excludes Yahoo
- explicit opt-in remains required for all secondary access
