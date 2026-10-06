# Final Accuracy Research — V10 — 2026-10-03

## Purpose

V10 is a research-integrity and signal-quality pass over V9. The objective is to reduce false positives and hidden leakage without optimizing the synthetic audit to produce attractive returns.

## Research conclusions

Current financial-ML research continues to identify data leakage, non-IID validation, backtest overfitting, multiple testing, survivorship bias and poor reproducibility as dominant causes of inflated results. Recent work recommends pipeline-aligned audits, purging/embargo, CPCV, PBO and DSR rather than relying on one walk-forward score.

## V10 additions

1. **Falsification tests**
   - label-permutation null AUC
   - temporal prediction-shift AUC
   - numeric feature scan against future target proxy
2. **Calibration diagnostics**
   - expected calibration error (ECE)
   - maximum calibration error (MCE)
   - calibration slope/intercept
3. **Execution-cost stress testing**
   - 0.5x / 1x / 2x / 3x baseline cost scenarios
   - mean return and Sharpe under each scenario
4. **Full-event-horizon purge configuration**
   - CPCV purge/embargo increased to 10 bars because the configured horizon set includes 10 bars.
   - Panel walk-forward excludes the full configured event horizon before training.
5. **Pooled panel learning retained**
   - symbol-wise execution labels
   - timestamp-based splits
   - cross-sectional ranks/z-scores
   - sector/market residual research features
6. **Selective publication retained**
   - conformal abstention
   - multi-horizon agreement
   - ensemble disagreement
   - OOS meta-label gate

## Data priorities

The next accuracy phase should use genuinely point-in-time information: historical constituent membership, corporate actions and announcements, earnings/revisions, derivatives surfaces, breadth, delivery, liquidity/microstructure and timestamped news. NSE provides historical security-master, corporate-action, price/volume, delivery, impact-cost and derivatives reports, subject to applicable data access/licensing terms.

## What is intentionally not claimed

- No synthetic metric is presented as live NSE accuracy.
- No guaranteed profitability or accuracy is claimed.
- No broker execution is included.
- `REAL_TRADING=false` remains a hard boundary.
- Historical membership must be supplied as an actual point-in-time dataset before production training; the loader/template is not a fabricated historical universe.

## Final research recommendation

Stop expanding the technical-indicator library. Move to real point-in-time multi-symbol data and an untouched final holdout. Every new information layer must pass availability-time, leakage, drift, economic-cost and falsification checks before it can contribute to production signals.
