# NSE Signal Provider — Accuracy Research V7

## Research conclusion
The remaining high-value accuracy improvements are selective prediction and evaluation integrity, not indiscriminate indicator expansion.

## V7 additions
1. Cost-aware validation-only threshold selection.
2. Conformal abstention remains available for ambiguous predictions.
3. Dependence-aware stationary block bootstrap is now reported alongside IID bootstrap.
4. Multi-horizon directional agreement utility added for independent horizon models.
5. Economic publication must remain next-open, cost-adjusted, ATR-aware.
6. Model disagreement remains a first-class uncertainty feature.

## Why these matter
Financial observations are autocorrelated, labels overlap, regimes change, and repeated model/threshold search creates selection bias. Current research recommends purging/embargo, CPCV, PBO/DSR and pipeline-level leakage audits. CPCV has shown lower PBO and stronger DSR statistics than conventional validation in controlled comparisons.

## Data layers still required for genuine market validation
- point-in-time NIFTY 200 membership
- timestamped fundamentals and earnings revisions
- corporate actions/events
- options IV/skew/OI/futures basis
- market and sector breadth
- delivery/turnover
- timestamped news/events
- historical bid/ask and order-book data where available

NSE currently publishes historical derivatives reports and option-chain fields including OI, change in OI, volume, IV, bid and ask. These should be captured with availability timestamps and joined backward/as-of rather than by calendar date alone.

## Non-negotiable publication rules
- No future information in features.
- No threshold tuning on the final holdout.
- No today's universe applied to historical periods.
- No signal publication without economic context.
- No production promotion when the model fails predictive, economic, stability, drift or validation gates.
- No claim of guaranteed accuracy or profitability.

## Signal-only boundary
`REAL_TRADING=false` and no broker execution are permitted by design.
