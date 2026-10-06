# Final Accuracy Research — 2026-10-02 V2

## Purpose

This release focuses on genuine out-of-sample signal quality rather than adding indicators indiscriminately.

## Added controls

1. Adversarial validation — trains a separate classifier to distinguish research/reference data from current/live data. A high AUC indicates distribution shift and can block publication.
2. Dependence-aware block bootstrap — confidence intervals preserve short-range return dependence instead of treating every bar as IID.
3. Regime-conditional evaluation — signal precision and coverage are measured by regime and volatility bucket.
4. Signal persistence/stability gate — publication can require a prediction to remain decisive for a configured number of observations and/or a minimum stability score.
5. Existing event uniqueness, purged/embargoed WFO, CPCV, calibration, conformal abstention, point-in-time validation, drift/PSI, economic gates and model governance remain active.

## Research rationale

Financial time series are dependent and non-stationary. Recent financial-ML evaluation work emphasizes leakage control, purged/CPCV validation, backtest-overfitting diagnostics and reproducibility rather than relying on a single backtest score. The system therefore treats model acceptance as a governance decision, not a promise of future performance.

## No artificial accuracy

Synthetic data is used only for software diagnostics. A model that does not beat its baseline or fails the economic contract is rejected. No threshold, feature, or model is tuned against the final test set.

## Remaining external information layers

For real NSE research, the highest-value additions are point-in-time fundamentals, corporate events, options surface/OI, order-book/depth, delivery, breadth, sector/factor data and timestamped news. These must be licensed/obtained from appropriate sources and joined strictly as-of the signal timestamp.
