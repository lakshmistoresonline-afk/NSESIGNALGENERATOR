# Authoritative historical PIT data sources

Production data authority is restricted to NSE India / NSE Clearing / NSE Indices official publications.

## Primary daily market history
- Capital Market final UDiFF common bhavcopy: `https://www.nseindia.com/all-reports` and the deterministic archive family under `https://archives.nseindia.com/content/cm/`.
- Equity derivatives final UDiFF common bhavcopy: `https://www.nseindia.com/all-reports-derivatives` and the deterministic archive family under `https://archives.nseindia.com/content/fo/`.
- NSE security master: official CM security report.
- NSE index close reports: official daily index reports.

## Secondary PIT layers
Use the official NSE report catalog for delivery, impact cost, daily volatility, surveillance, price bands, short selling, participant OI and FII derivatives statistics. Corporate-action/filing events require the actual NSE broadcast/publication timestamp for PIT use.

## Historical Nifty 200 membership
The official NSE page publishes the current Nifty 200 list. It is **not** valid to apply today's list backward through history. Historical constituent data should come from dated official constituent-change records / NSE Indices historical constituent data. NSE Indices explicitly offers ongoing and historical index/component data through its data-subscription service. Until dated authoritative membership is supplied, historical Nifty 200 backtests remain blocked.

## Included in this release
This package includes:
1. the authoritative source catalog,
2. deterministic official archive URL builders,
3. immutable downloader + SHA-256 provenance,
4. PIT timestamp contract,
5. NSE 2026 equity holiday calendar sourced from the official NSE holiday schedule,
6. acquisition and validation scripts.

The release does **not** fabricate or silently substitute third-party market files when official historical bytes are unavailable in the build environment.
