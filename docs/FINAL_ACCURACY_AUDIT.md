# Final Signal-Accuracy Audit

## Scope

This release is no longer an indicator-only package. The signal-generation stack now treats predictive quality as a sequence of independent research gates.

## What was added

### 1. Data integrity

- OHLC consistency checks
- duplicate timestamp detection
- non-positive price checks
- negative-volume checks
- suspicious calendar-gap diagnostics
- cleaning function

### 2. Point-in-time discipline

The universe is intended to be supplied as dated constituent membership. A current survivor list must not be used to reconstruct historical universes.

NIFTY 200 is a broad-market reference universe; NSE states that it contains NIFTY 100 plus NIFTY Midcap 100 and is rebalanced semi-annually. The current NSE page reports about 79.85% free-float market-cap representation as of 30 March 2026.

### 3. Target engineering

The package now supports both:

- fixed-horizon directional labels
- triple-barrier labels with profit, stop and time barriers

Same-bar profit/stop collisions are pessimistically assigned to the stop barrier. Future labels are generated separately from causal features.

### 4. Purged walk-forward validation

For a horizon `H`, the training sample is ended at least `H + embargo` bars before the test start. This prevents labels whose future window overlaps the test interval from entering training.

### 5. Fold-local feature selection

Missingness and high-correlation pruning are fitted inside each training fold. The test fold cannot influence feature selection.

### 6. Ensemble modeling

The OOS engine combines:

- logistic regression
- random forest
- gradient boosting

and performs time-ordered probability calibration on a later training tail.

### 7. Multi-horizon confirmation

The package supports 1/3/5/10-bar models. Dispersion among horizon probabilities becomes an uncertainty signal rather than being ignored.

### 8. Regime conditioning

Causal regime features include:

- 200-period market trend distance
- 63-period trend slope
- 20-period realized volatility
- 252-period volatility percentile
- India VIX percentile when supplied
- breadth context when supplied
- NIFTY context when supplied

### 9. Meta-labeling

The primary directional model is separated from the question of whether the particular signal should be taken. Meta labels are generated only from OOS primary predictions.

### 10. Economic backtesting

The previous ambiguous return alignment was replaced with explicit next-bar-open entry and later exit semantics. A separate triple-barrier event backtester is available.

### 11. Cost model

Round-trip costs, slippage, optional spread and participation-based impact are separated from raw prediction quality.

### 12. Selective prediction

The signal engine can reject uncertain predictions instead of forcing every observation into BUY/SELL.

### 13. Regime/liquidity/event gates

Signals can be rejected for:

- insufficient probability
- weak factor support
- weak regime
- excessive model disagreement
- low liquidity
- excessive ATR volatility
- stale data
- corporate-event blackout
- non-positive cost-adjusted expected value

### 14. Cross-sectional controls

The research layer supports percentile/rank scoring, winsorization, sector-relative ranking and concentration caps.

### 15. Statistical robustness

The package reports:

- AUC
- PR AUC
- log loss
- Brier score
- coverage
- hit rate
- Sharpe
- Sortino
- profit factor
- drawdown
- skew/kurtosis
- probabilistic Sharpe ratio
- approximate deflated Sharpe statistic
- bootstrap intervals
- permutation diagnostics

The DSR/PBO literature specifically addresses selection bias and backtest overfitting; those diagnostics are therefore treated as research gates rather than cosmetic statistics.

## Additional data that can materially improve the system when legally/technically available

- point-in-time fundamentals
- earnings/event dates
- corporate actions
- delivery percentage
- bid/ask spread and depth
- order-book imbalance
- FII/DII flows
- advance/decline breadth
- option IV/PCR/OI
- futures basis and roll information
- timestamped news sentiment
- genuine 1H/4H/Daily multi-timeframe data

These inputs must carry their original publication/observation timestamps. No unavailable value is fabricated.

## Synthetic validation warning

`scripts/run_research_audit.py` intentionally uses synthetic data. Synthetic performance is only a software/invariant test. It is not evidence of profitable NSE trading performance.

In fact, a useful research property is that a deliberately weak/noisy synthetic market can produce poor OOS results and the publication gates should reject it. A system that always produces impressive synthetic results is more suspicious, not more accurate.

## Signal-only constraint

`REAL_TRADING = FALSE` remains enforced. There is no broker order placement or execution path in this package.

## Regulatory/data notes

NSE's Data Sharing & Usage Policy governs use and distribution of NSE market data. Any production feed should be sourced and licensed appropriately.

SEBI's February 2025 retail algorithmic-trading circular and subsequent implementation timeline should be reviewed if broker execution is ever added. This project deliberately does not add execution.
