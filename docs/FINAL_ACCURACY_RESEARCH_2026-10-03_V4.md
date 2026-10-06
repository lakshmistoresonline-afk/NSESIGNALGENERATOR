# Final Accuracy Research — 2026-10-03 (V4)

## Executive conclusion

The highest-value remaining improvements are not additional technical indicators. The evidence favors improving information timing, execution-consistent labels, cross-sectional context, dependence-aware validation, multiple-testing controls, and point-in-time alternative data.

## Implemented in this release

1. **Execution-consistent training labels**
   - Default walk-forward training now uses next-open triple-barrier events.
   - ATR is frozen at signal time.
   - Monitoring starts on the actual entry bar.
   - Simultaneous barrier hits use conservative stop-first handling.
   - Timeout events are excluded from binary classification instead of being silently treated as losses.

2. **CPCV utility**
   - Added combinatorial purged cross-validation splitting with explicit purge and embargo buffers.
   - 6 groups / 2 test groups produces 15 paths in the default research configuration.

3. **PBO utility**
   - Added a paired in-sample/out-of-sample path diagnostic for probability of backtest overfitting.
   - It requires the candidate/model trial matrix rather than inventing a PBO number from one backtest.

4. **Multiple-testing registry utility**
   - Added a selection-aware summary of the number of candidate trials and observed Sharpe rank.

5. **Stricter model publication gate**
   - Predictive metrics alone are insufficient.
   - Economic, stability, drift, CPCV, PBO, DSR and multiple-testing evidence are now required when the strict validation gate is enabled.

6. **Point-in-time universe interface**
   - Added a versioned NIFTY 200 membership loader using `symbol`, `effective_from`, and `effective_to`.
   - The included membership CSV is intentionally empty; historical membership must be populated from versioned constituent files rather than fabricated.

7. **Regression safety**
   - 43 automated tests pass.
   - Python compilation passes.
   - The existing indicator warnings are performance warnings, not correctness failures.

## Research findings driving the architecture

- Recent financial-ML evaluation research emphasizes leakage, sample-splitting, model-selection and backtest-overfitting controls rather than headline backtest returns.
- A 2026 systematic review highlights non-IID validation, redundancy among price-derived indicators, and the importance of CPCV and more causal feature construction.
- A recent automated alpha-search study reported that its price/volume-only candidate signals failed its full survivor criteria in its tested universes and period. This is evidence against assuming that more price/volume formula search automatically creates robust alpha.
- NSE's NIFTY 200 is reviewed semi-annually, so a historical research universe must use effective-date membership rather than today's constituents applied backward.
- NSE provides timestamped option-chain fields including OI, change in OI, volume, IV and bid/ask fields, making a properly timestamped derivatives layer a high-value future information source.
- NSE publishes corporate actions and corporate-filings data; these should be joined by information availability time, not merely event/record date.

## Highest-value remaining additions

### A. Real point-in-time data stack — highest priority

Add versioned, timestamped providers for:
- NIFTY 200 historical membership
- fundamentals and quarterly results
- earnings dates and revisions
- corporate actions / corporate announcements
- index and sector breadth
- FII/DII flows
- futures basis and OI
- options IV, skew, term structure, PCR and OI concentration
- delivery percentage and turnover
- bid/ask spread and order-book imbalance where legally and technically available
- timestamped news/event sentiment

Every record must carry an `asof_time`/publication timestamp and be backward-as-of joined. Never use a value merely because its economic period predates the signal; it must have been publicly available by the signal timestamp.

### B. True multi-symbol panel learning

The current cross-sectional research utilities should be promoted into a production research path that trains across many symbols at each timestamp. Add:
- within-date ranks/z-scores
- sector-neutral residual returns
- market residual returns
- sector-relative momentum
- liquidity/volatility ranks
- cross-sectional target construction
- sector and market exposure diagnostics

### C. Nested model/threshold selection

The final untouched holdout must never participate in:
- feature selection
- hyperparameter tuning
- threshold tuning
- model family selection
- signal filtering
- indicator parameter search

Use nested time-aware selection and record every candidate in the trial registry.

### D. Proper DSR/PBO research implementation

The current DSR implementation is explicitly an approximation. Before any production claim, replace it with an exact search-design-aware DSR calculation and compute PBO from actual CPCV candidate paths.

### E. Regime-conditioned acceptance

Evaluate every candidate separately across:
- bull / bear / sideways trend
- low / normal / high volatility
- gap-heavy sessions
- event-heavy periods
- high/low liquidity regimes
- sector leadership/rotation regimes

A model that works only in one regime should not be presented as a universal signal generator.

### F. Probability calibration and abstention

Continue treating the model as a calibrated probability estimator rather than a forced BUY/SELL classifier. Add:
- rolling calibration drift
- conformal uncertainty
- abstention / NO-SIGNAL state
- minimum expected-value after costs
- minimum liquidity and spread conditions
- signal persistence/stability

### G. Realistic market-impact model

For higher-frequency variants, replace flat slippage with liquidity-aware cost assumptions using spread, participation, volatility and turnover. The signal provider remains signal-only; this is research realism, not order execution.

## Deliberately NOT added

- More arbitrary indicators simply to increase feature count.
- Synthetic historical fundamentals/options/news.
- Fabricated NIFTY 200 historical membership.
- Broker execution.
- Any path that can set `REAL_TRADING=true`.

## Validation result

The synthetic audit is implementation validation only. The current run has predictive AUC around 0.515, so it does **not** clear the configured predictive gate. This is intentionally retained as a negative research result rather than tuned away.

The package must therefore be treated as a research-grade signal framework awaiting genuine point-in-time market data and an untouched final holdout—not as evidence of a guaranteed accuracy or profitability level.
