# PIT NSE Data Integration — Final Phase

## Integrated
- NSE CM UDiFF daily bhavcopy
- NSE F&O UDiFF daily bhavcopy
- dated NSE security master
- delivery-position adapter
- security-category impact-cost adapter
- advances/declines breadth adapter
- India VIX adapter
- corporate-event/action adapter with strict announcement-time requirement
- point-in-time fundamentals interface with strict availability-time requirement
- PIT store, provenance and backward as-of joining
- source-contract registry
- normalized-layer CLI
- integrated PIT dataset builder

## Source evidence
NSE's official report catalog lists CM-UDiFF Common Bhavcopy Final, Security-wise Delivery Positions, Security Category Impact Cost, Advances/Declines, Historical Index Data and Historical Data for India VIX. NSE also exposes corporate filings/actions and F&O historical reports. The package uses those official source contracts and does not invent missing download endpoints.

## Fail-closed rules
1. Date-only corporate events are rejected for PIT modeling because a date does not establish when the information became available.
2. Fundamentals without an actual availability timestamp are rejected.
3. Historical NIFTY 200 membership is never inferred from today's constituents.
4. Licensed/order-book/news data is not fabricated or backfilled.
5. All joins are backward/as-of joins.

## Acquisition
Use `scripts/ingest_nse.py` for deterministic UDiFF/security-master archives. Use `scripts/ingest_pit_layers.py` for locally acquired official report files. Then use `scripts/build_pit_dataset.py` to create the leakage-safe daily PIT feature table.

## Current data-access boundary
This environment cannot directly retrieve external NSE archives. The package therefore contains production ingestion and validation code but does not claim that years of external data have been downloaded. Once files are supplied or network access is available, the same commands populate `data/raw/nse` and `data/processed/nse_pit`.

## Research consequence
Do not run final model selection until the full PIT dataset is populated and an untouched final holdout is frozen. The signal engine must remain fail-closed when required PIT layers are missing.
