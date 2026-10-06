# Final Accuracy Research — V9

## Research conclusion
V9 focuses on the remaining high-value structural accuracy controls rather than adding more technical indicators. Current financial-ML literature continues to identify leakage, multiple testing, non-IID validation, survivorship bias and the gap between statistical and economic performance as major causes of failed generalization.

## V9 additions
1. **True pooled multi-symbol walk-forward**: `models/panel_walk_forward.py` trains one model across symbols while splitting strictly by timestamp, rather than treating concatenated symbols as one time series.
2. **Symbol-wise execution-consistent labels**: `research/panel_labels.py` applies next-open triple-barrier labels independently to each symbol and conservatively purges the complete event horizon.
3. **Point-in-time cross-sectional features**: ranks/z-scores are calculated only within the same timestamp; sector residuals and market residuals are also same-timestamp transformations.
4. **Cross-sectional future excess-return research target**: provided as an auxiliary ranking target, not silently substituted for the executable target.
5. **Panel feature selection**: panel features are only exposed to the model when `timestamp` and `symbol` are present, preventing single-series tests from acquiring meaningless all-NaN columns.

## Why this matters
A multi-stock signal provider should learn both absolute and relative information. But simply concatenating symbols and using a single-series walk-forward creates invalid training/test geometry. V9 makes the pooled-panel path explicit and time-based.

## Data priority remains unchanged
The largest unimplemented accuracy gains still require genuine point-in-time data: historical NIFTY 200 membership, fundamentals and revisions, corporate events, derivatives surfaces, breadth, delivery/liquidity/microstructure and timestamped news. NSE publishes historical price/volume, delivery, corporate-action and derivatives reports that can support those layers subject to applicable data access terms.

## Publication discipline
Signals remain fail-closed on missing economic context, uncertainty, stale data, excessive model disagreement, conformal abstention, and optional meta-label/horizon gates. Validation-only threshold selection must never touch the final holdout.

## Synthetic audit
Synthetic diagnostics are research tests only. They are not evidence of live NSE alpha or a guaranteed accuracy percentage. V9 retains the requirement for an untouched final holdout before any production promotion.

## Execution boundary
`REAL_TRADING=false` and `signal_only=true` remain mandatory. No broker execution is included.
