# Secondary/free market-data providers

These adapters are deliberately separated from the authoritative NSE PIT layer.
They can supply development/current-data observations and cross-checks, but their
output is **not** accepted as proof of survivorship-free PIT completeness, exchange
licensing, historical corporate actions, historical constituent membership, or true
publication-time availability.

## Providers

- **Yahoo Finance**: public chart endpoint; unofficial/secondary. No API key in this adapter. Review Yahoo terms before redistribution. Never use it to satisfy PIT readiness.
- **Angel One SmartAPI**: free SmartAPI; historical candles are available for NSE/BSE/F&O, with API credentials and documented request/rate limits. SmartAPI also exposes historical OI for live F&O contracts. It can be used for secondary candles and cross-checks.
- **FYERS API**: FYERS states that Trading APIs and historical/quotes/market data are free for FYERS users, subject to its terms and app permissions.
- **DhanHQ**: authenticated historical OHLC API; useful as a secondary source. It is not an exchange-authoritative PIT archive.
- **Groww API**: currently advertised at INR 499 + taxes/month; therefore it is included as an optional broker source, **not** classified as free tier. Its historical API documents full daily history and F&O backtesting data from 2020.

## Security

Credentials are read from environment variables and never written into CSV files.
Execution/order endpoints are not implemented by these adapters.

## Usage

```text
set ALLOW_SECONDARY_PROVIDER=true
python scripts/acquire_secondary_market_data.py yahoo RELIANCE --start 2025-01-01 --end 2025-12-31 --interval 1d
```

Angel One additionally requires `ANGELONE_API_KEY`, `ANGELONE_AUTH_TOKEN` and a
historical `symbol_token`. Groww requires `GROWW_ACCESS_TOKEN`; Dhan requires
`DHAN_ACCESS_TOKEN` and `security_id`; FYERS requires `FYERS_ACCESS_TOKEN`.

Every downloaded file receives a `.metadata.json` sidecar containing provider,
retrieval timestamp, request parameters, source URL, source tier and SHA-256.


## V21 provider-policy hardening

- Upstox and 5paisa are supported as free secondary market-data APIs.
- Yahoo is supported only for explicit/manual use and is excluded from automatic fallback because current Yahoo terms restrict automated collection and commercial reuse without permission.
- Secondary results are never PIT-authoritative. Their retrieval timestamp is not treated as historical publication/availability time.
- Provider adapters are read-only: no order endpoints are exposed.
- Historical providers must be cross-checked against authoritative NSE data before being admitted to any PIT dataset.
