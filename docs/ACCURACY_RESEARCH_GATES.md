# Accuracy Research Gates

The objective is not to maximize historical win rate. The objective is to maximize the probability that a signal retains positive, cost-adjusted predictive value out of sample.

## Required gates

- Data quality gate
- Point-in-time universe gate
- Causal feature gate
- Purged + embargoed time split
- Fold-local feature selection
- Fold-local calibration
- Multi-horizon agreement
- Regime compatibility
- Liquidity/tradability gate
- Corporate-event gate when event data exists
- Positive cost-adjusted expected value
- Benchmark comparison
- Parameter-search accounting
- Multiple-testing adjustment
- Post-selection OOS holdout
- Live drift monitoring

## Accuracy metrics

Report, at minimum:

- ROC AUC
- PR AUC for imbalanced event labels
- log loss
- Brier score
- calibration curve / reliability bins
- expected calibration error
- coverage after selective prediction
- precision among published signals
- directional hit rate
- triple-barrier success rate
- average realized return
- profit factor
- Sharpe and Sortino
- max drawdown
- tail loss / CVaR
- turnover
- cost-adjusted return
- PSR
- DSR / selection-adjusted statistic
- bootstrap confidence intervals
- permutation p-value
- degradation by market regime
- degradation by sector
- degradation by liquidity bucket
- degradation through time

## Why these controls matter

Backtest overfitting and selection bias can make a searched strategy look much stronger than it is. The Deflated Sharpe Ratio was proposed specifically to account for selection bias, multiple testing and non-normal returns. The Probability of Backtest Overfitting framework uses combinatorial symmetric cross-validation to estimate overfit probability. Recent evaluation-integrity work similarly emphasizes leakage audits, purged/CPCV validation, DSR and falsification checks.

The project therefore records search trials and does not treat one favorable backtest as proof of predictive edge.
