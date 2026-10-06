# NSE Signal Provider — Final Accuracy Research V6

## Purpose

V6 is a signal-generation research and publication framework. It is **not** a claim of market accuracy or profitability. Synthetic audits are diagnostic only.

## Research conclusions

Current financial-ML evidence continues to emphasize that the main threats are leakage, non-IID validation, selection bias, multiple testing, and mismatch between predictive labels and the economic payoff contract. CPCV with purging/embargo is useful because financial labels resolve over intervals rather than at a single timestamp. DSR/PBO and an explicit trial registry are necessary when many models, features, thresholds or parameter sets have been searched.

The latest research also cautions that even triple-barrier labels can fail economically if the label contract is not aligned with the actual trading payoff. Therefore V6 keeps the next-open entry, frozen-at-signal ATR and economic backtest contract aligned, while still requiring economic validation.

## V6 additions

1. **Execution-consistent event labels** — next-open entry, ATR frozen at signal time, explicit profit/stop/timeout events, conservative same-bar collision handling.
2. **CPCV / purge / embargo** — 15-path default configuration for six groups and two test groups.
3. **Selection-aware validation** — PBO and multiple-testing registry are publication-gate inputs; no single backtest is treated as sufficient.
4. **Model disagreement** — ensemble dispersion is recorded as uncertainty instead of hiding disagreement behind a simple mean probability.
5. **Alternative volatility estimators** — Parkinson and Garman-Klass realized volatility candidates.
6. **Liquidity / impact proxies** — Amihud-style illiquidity, dollar-volume state, range-per-volume and volume-price impact candidates.
7. **Flow / candle-state candidates** — signed-volume proxy, close-location value, CLV-volume pressure.
8. **Trend-quality / distribution candidates** — directional efficiency, return skew/kurtosis, volatility-of-volatility and range compression.
9. **Gap decomposition** — overnight versus intraday return features and their rolling abnormality.
10. **Cross-sectional architecture** — timestamp-local ranks, sector-relative transforms and market residuals remain available for a point-in-time multi-symbol panel.
11. **Point-in-time universe requirement** — historical membership must be supplied as-of; current constituents must not be backfilled into history.
12. **Strict signal publication** — no signal without economic context (price + ATR), positive cost-adjusted expected value, risk/reward and configured quality gates.

## What still requires real data before production

The highest-value remaining work is data rather than more indicators:

- point-in-time NIFTY 200 membership history;
- point-in-time fundamentals and earnings revisions;
- corporate actions and corporate announcements with availability timestamps;
- options IV, skew, term structure, OI and changes in OI;
- futures basis and OI;
- market/sector breadth and constituent-level breadth;
- delivery/turnover information;
- timestamped bid/ask and order-book imbalance where available;
- timestamped news/events and sentiment;
- a genuine multi-symbol panel learner rather than independent single-stock models;
- untouched final holdout data reserved until all research decisions are frozen.

## Synthetic audit interpretation

The V6 offline audit uses 700 synthetic observations. It generated 237 candidate features and 252 total columns.

The synthetic walk-forward model produced AUC about 0.528, but this does **not** establish market edge. The fixed-horizon economic backtest produced approximately 0.31 annualized Sharpe, 1.05 profit factor and a -46.6% maximum drawdown; the stationary bootstrap mean-return interval crossed zero. These results are not suitable for promotion.

The triple-barrier diagnostic happened to be stronger on the synthetic generator, but this is also not market evidence. The correct interpretation is that the research framework is capable of detecting and reporting different outcomes under different payoff contracts.

## Production promotion rule

A model should be published only if it passes all configured predictive, economic, stability, drift, CPCV/PBO and multiple-testing gates on genuine point-in-time data, and then survives a completely untouched holdout. If any required evidence is missing, the publication state should be **NO SIGNAL / RESEARCH ONLY**.

## Safety boundary

`REAL_TRADING=false` and `signal_only=true` remain hard requirements. This package contains no broker execution path.
