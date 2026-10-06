# Final Accuracy Research Audit — 2026-10-02 v3

## Final corrections

1. Triple-barrier labels now use the same execution horizon as the economic backtest: signal at close[t], entry at open[t+1], monitor through close[t+1+horizon]. ATR is frozen at signal time.
2. Model acceptance is strict: missing predictive/economic/stability/drift evidence is a failure, not an implicit pass.
3. Production SignalEngine now requires price + ATR economic context by default; a probability-only prediction cannot become a published signal.
4. Default universe is provider-driven point-in-time NIFTY 200 membership, with a synthetic fallback only for offline demos.
5. Cross-sectional and sector-neutral transforms are available for timestamped multi-symbol panels.
6. Clean-checkout test collection no longer depends on a manually exported PYTHONPATH.

## Evidence standard

The research stack uses purged/embargoed walk-forward validation, CPCV-style robustness, fold-local feature selection, event-uniqueness weighting, temporal calibration, conformal abstention, adversarial drift, PSI, regime evaluation, cost-aware economics and strict model governance.

The latest synthetic audit is intentionally retained as a falsification diagnostic. It does not constitute market-alpha evidence. In the latest 700-row synthetic run, the OOS classifier did not beat the 50/50 log-loss or Brier baselines, while the execution-consistent triple-barrier backtest had profit factor below 1. The correct conclusion is therefore that the synthetic model should not be promoted to production.

## Research rationale

Financial-ML evaluation literature identifies leakage, non-IID validation, multiple testing, selection bias and backtest overfitting as major sources of inflated results. Purging, embargoing, CPCV, DSR/PBO diagnostics, falsification and reproducible data provenance are therefore treated as gates.
