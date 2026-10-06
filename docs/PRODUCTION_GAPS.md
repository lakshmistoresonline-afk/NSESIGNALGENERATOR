# Production gaps before relying on live signals

## Data acquisition / licensing blockers
1. Acquire/licence historical CM EOD data from NSE Data & Analytics.
2. Acquire/licence historical F&O EOD data if derivatives features are enabled.
3. Acquire/licence historical securities/contracts master data.
4. Acquire historical Nifty 200 constituent snapshots/effective intervals from NSE Indices.
5. Acquire/licence PIT corporate data and timestamped corporate announcements.
6. Acquire historical index constituent weights where index-weight features are enabled.
7. Acquire historical order/trade data only for features that genuinely require intraday microstructure.
8. Acquire a properly licensed timestamped news dataset before enabling news sentiment.
9. Acquire vintage/revision-aware fundamental data before enabling fundamental features.

## Research controls
10. Keep the final holdout sealed and consumed only once.
11. Use a fully specified CPCV/PBO procedure and a true DSR/PSR implementation; approximate DSR diagnostics must not be labelled as full DSR.
12. Record every model/search trial in the multiple-testing registry.
13. Require OOS meta-label predictions for meta-model training.
14. Require paper-forward validation before publication.

## Operational controls
15. Keep `REAL_TRADING=false` and `SIGNAL_ONLY=true`.
16. Keep third-party market-data fallback disabled.
17. Require verified PIT snapshot, provenance and applicable data-use rights before publication.
18. Keep the dashboard/API local or authenticated before LAN/public exposure.
