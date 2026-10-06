# Final Accuracy Research & Signal-Generation Audit — 2026-10-02

## Objective
Improve genuine out-of-sample signal quality without manufacturing backtest accuracy. The system remains signal-only (`REAL_TRADING=false`).

## Highest-impact additions
1. Execution-consistent next-open entry for labels and economic backtests.
2. Triple-barrier labels with conservative same-bar stop-first handling.
3. Purged and embargoed walk-forward validation.
4. CPCV as an independent robustness diagnostic.
5. Fold-local feature selection; no full-sample feature selection.
6. Event-overlap/average-uniqueness sample weighting so overlapping labels do not dominate training.
7. Time-ordered probability calibration.
8. Validation-only threshold selection; test set is never used for threshold tuning.
9. Multi-horizon confirmation and uncertainty/abstention.
10. Meta-labeling using genuinely OOS primary predictions.
11. Regime conditioning and market-context features.
12. Point-in-time/as-of joins for all external information.
13. Feature-distribution drift monitoring (PSI) with publication abstention.
14. Cross-sectional ranking and sector/concentration controls.
15. Cost/slippage/impact-aware economic validation.
16. Predictive and economic benchmark gates.
17. Statistical diagnostics: Brier, log loss, AUC/PR-AUC, PSR/DSR/PBO-style diagnostics, permutation tests and bootstrap intervals.
18. Explicit optional information layers for fundamentals, corporate actions, earnings, derivatives surface, order book, delivery, breadth and timestamped news/sentiment.

## What should not be added blindly
- More correlated technical indicators solely to increase feature count.
- Full-sample normalization/scaling.
- Future corporate/fundamental values merged by report date instead of availability timestamp.
- Threshold optimization on the final test period.
- A model acceptance decision based on accuracy alone.
- Broker execution; this application is signal-only.

## Research rationale
Financial ML is vulnerable to leakage, non-IID validation, backtest overfitting and multiple testing. Purging/embargoing, CPCV, DSR/PBO-style diagnostics, falsification tests and reproducible point-in-time pipelines are therefore treated as governance controls, not optional decorations.

## Required live-data layers
The model is ready to consume, when available and correctly timestamped: NIFTY/sector breadth, India VIX, FII/DII, options IV/PCR/OI/futures basis, order-book/depth/spread, delivery data, corporate events, earnings, point-in-time fundamentals and timestamped news/sentiment.

## Acceptance policy
A candidate model is not deployable merely because it has high historical accuracy. It must beat a naive probability baseline out of sample, remain calibrated, retain feature stability, remain inside the training distribution, and demonstrate positive cost-adjusted economic evidence under the frozen execution contract. If these conditions are not met, the correct output is `NO MODEL / NO SIGNAL`.
