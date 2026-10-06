# Accuracy Enhancement Roadmap — final research layer

The signal engine is optimized for *out-of-sample reliability*, not a high in-sample accuracy number.

## Added controls

1. Triple-barrier and fixed-horizon labels are kept separate from causal features.
2. Purged/embargoed walk-forward validation remains mandatory.
3. CPCV-style group splits are available for robustness analysis.
4. Fold-local feature selection and feature-stability frequencies prevent global selection leakage.
5. Time-ordered probability calibration remains mandatory.
6. Split-conformal abstention provides a second, distribution-free selective-prediction layer when calibration data is sufficient.
7. Multi-horizon disagreement is treated as uncertainty.
8. Regime-conditional metrics prevent a model from hiding failure in one market regime.
9. PSI drift monitoring detects feature-distribution changes between research and live periods.
10. Validation-only threshold selection prevents test-set threshold optimization.
11. Cross-sectional ranking and sector/name caps reduce concentration.
12. Dynamic economic costs remain separate from predictive metrics.
13. Data quality, corporate events, liquidity, and stale-data gates are explicit.

## Data that materially improves future accuracy

The architecture accepts point-in-time fundamentals, corporate actions, earnings/events, sector/index breadth, options IV/PCR/OI, futures basis, delivery data, order-book imbalance/spread/depth and timestamped news/sentiment. These must be timestamped as-of data; they must not be backfilled using information that was unavailable at the signal timestamp.

NSE provides separate market-data and corporate-data products, and commercial use is governed by its data-sharing/usage terms. See the official NSE data policy and historical/corporate-data pages before connecting a production feed.

## Accuracy gate

A model should publish only when it passes all applicable gates:

- predictive metrics beat a naive baseline on untouched OOS data;
- probability calibration is acceptable;
- economic backtest remains positive after realistic costs;
- regime-conditioned performance is not catastrophically weak;
- feature stability is adequate;
- drift is within tolerance;
- conformal/uncertainty gates permit publication;
- no data-quality, event, liquidity or staleness gate is violated.

A failed gate means **NO SIGNAL / MODEL NOT DEPLOYABLE**, not a lower-quality signal.
