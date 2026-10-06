# Signal Accuracy Architecture

This application is a signal provider, not an execution engine. Accuracy is treated as an empirical research problem; no configuration guarantees future returns.

## Layers beyond indicators

1. **Data integrity** — duplicate timestamps, OHLC consistency, non-positive prices, negative volume, corporate-action consistency, missing-session detection.
2. **Point-in-time universe** — constituents must be dated; never train historical models using today's survivor list.
3. **Target engineering** — directional benchmark plus triple-barrier event labels. Profit/stop/time barriers are explicit and same-bar collisions are pessimistically resolved.
4. **Purged walk-forward validation** — training ends before the label horizon plus embargo. Calibration is performed on a later tail of the training sample.
5. **Feature selection inside each fold** — missingness and correlation pruning are fitted only on training data.
6. **Model ensemble** — logistic regression, random forest and gradient boosting provide different inductive biases; probabilities are averaged and then calibrated.
7. **Multi-horizon agreement** — 1/3/5/10-bar models provide directional persistence and uncertainty; disagreement suppresses publication.
8. **Regime conditioning** — market trend, realized volatility, India VIX percentile and breadth are used as context/gates rather than fabricated features.
9. **Meta-labeling** — a primary directional prediction is separated from the question “should this particular trade be taken?” and the meta target is built only from OOS primary predictions.
10. **Cost-aware economics** — next-bar entry, explicit holding/exit semantics, round-trip costs, slippage and barrier-aware exits are required.
11. **Selective prediction** — low-confidence observations are rejected rather than forced into BUY/SELL.
12. **Cross-sectional controls** — ranking, liquidity, sector concentration and correlated-signal limits are applied before publication.
13. **Statistical robustness** — Sharpe, Sortino, profit factor, drawdown, PSR, approximate DSR, bootstrap intervals and permutation tests are reported. Strategy search count must be recorded.
14. **Adversarial validation** — compare against naive direction, buy-and-hold, factor-only and simple logistic baselines; report degradation across regimes and time blocks.
15. **Live monitoring** — track calibration drift, probability distribution drift, feature missingness, regime frequency, signal hit rate, realized slippage proxy and performance decay.

## What should be added when data is available

- point-in-time fundamentals and earnings/event dates
- corporate actions and adjusted/unadjusted price reconciliation
- delivery percentage and auction/short-sale context where legally sourced
- order-book imbalance, spread and depth for intraday models
- FII/DII cash-market flows
- index/sector breadth
- option PCR, IV surface, OI and OI change
- futures basis/roll data
- timestamped news/sentiment with strict publication-time alignment
- multi-timeframe 1H/4H/Daily context

No external series is invented when unavailable.
