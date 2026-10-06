# NSE Point-in-Time Data Integration

## Authoritative layers

The ingestion layer targets NSE's published daily CM UDiFF bhavcopy, FO UDiFF bhavcopy, security master, index archives and related market reports. NSE retired the older daily bhavcopy/common-bhavcopy formats in July 2024 in favor of UDiFF common bhavcopy. The official reports page lists CM UDiFF, security master, security-wise delivery, impact cost and related reports. Historical reports also expose security-wise price/volume, advances/declines, historical indices and India VIX. 

## Canonical contract

Every external observation must carry:

- `symbol`
- event/report date
- `signal_time`
- `asof_time`
- source
- source URL or artifact ID
- artifact SHA-256
- retrieval timestamp

`asof_time <= signal_time` is mandatory for model features. Backward as-of joins are used for asynchronous information.

## Cash market

`CM-UDiFF Common Bhavcopy Final` is downloaded per trading date and normalized into `cash_daily`. The archive URL is deterministic:

`https://archives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{YYYYMMDD}_F_0000.csv.zip`

The UDiFF parser maps official fields such as `TckrSymb`, `TradDt`, `OpnPric`, `HghPric`, `LwPric`, `ClsPric`, and `TtlTradgVol` into canonical names.

## Equity derivatives

`FO-UDiFF Common Bhavcopy Final` is ingested into `fo_daily`, retaining expiry, option type, strike, underlying, volume, OI and OI change when present.

Archive URL:

`https://archives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{YYYYMMDD}_F_0000.csv.zip`

## Security master

The date-stamped NSE security master is retained because symbol/series/token mappings can change. Historical identifiers must never be reconstructed from today's master.

## Membership

NIFTY 200 membership is deliberately separated from the daily market data. The repository contains an **empty schema**, not fabricated historical membership. Populate it with authoritative/effective-dated constituent snapshots. The model gate should fail closed while the required historical membership is absent.

Required columns:

`symbol,effective_from,effective_to,source,source_asof`

## Corporate events and filings

Corporate actions, announcements and board meetings must be ingested with their actual announcement/availability timestamps. Record dates and ex-dates are not substitutes for announcement time when constructing a predictive feature.

## Derivatives surface

Daily FO data is a historical baseline. Intraday options IV/skew/order-book features require timestamped historical snapshots. NSE's public option-chain page exposes OI, change in OI, volume, IV, bid and ask for current observations, while historical contract-wise data is separately available.

## Delivery / impact / breadth

The next scheduled ingestion layers should include:

- security-wise delivery positions
- category impact-cost files
- advances/declines
- India VIX
- historical index OHLC
- price-band/surveillance indicators
- bulk/block deals and short selling where timestamp semantics permit

## Data quality gates

A dataset is rejected when:

1. an as-of timestamp is missing for a feature that requires it;
2. `asof_time > signal_time`;
3. duplicate `(symbol, signal_time, source)` rows exist without an explicit revision policy;
4. the source artifact checksum changes unexpectedly;
5. required trading dates are missing;
6. historical membership is inferred from today's constituents;
7. adjusted prices are mixed with raw prices without an explicit adjustment contract.

## No-execution boundary

This integration is read-only. It does not place orders, connect to a broker for execution, or alter `REAL_TRADING=false` / `SIGNAL_ONLY=true`.
