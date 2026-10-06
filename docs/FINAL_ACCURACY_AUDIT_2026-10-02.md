# Final Accuracy Architecture Audit — 2026-10-02

## Objective

Improve genuine out-of-sample signal quality rather than maximize in-sample accuracy. The application remains signal-only; no broker execution is implemented.

## Highest-value additions

### 1. Execution-consistent target construction
Signals are formed at close[t]. Default event labels and economic backtests enter at open[t+1]. ATR used to set barriers is frozen at signal time. This removes a subtle mismatch where labels could otherwise assume entry at close[t] while the backtest entered at open[t+1]. Same-bar TP/SL collisions are resolved stop-first because OHLC data cannot establish intrabar ordering.

### 2. Purged + embargoed validation
Training observations whose label windows can overlap the test period are removed. Embargo is applied after the purge. This is mandatory for overlapping financial labels.

### 3. CPCV robustness layer
A combinatorial purged group splitter is included for additional model-selection robustness. It should be used as a secondary validation framework, not as a license to search many configurations and keep the best result.

### 4. Fold-local feature selection
Feature ranking and correlation pruning occur inside each training fold. The test set never participates in feature selection.

### 5. Time-ordered calibration
Probability calibration is performed using observations later than model-training observations and earlier than the test period.

### 6. Selective prediction / conformal abstention
The package can abstain when a calibrated prediction does not produce a sufficiently narrow conformal prediction set. This creates an explicit NO-SIGNAL outcome rather than forcing a directional prediction.

### 7. Validation-only threshold selection
Signal probability thresholds can be selected on a validation segment and then frozen for the untouched test period. Threshold optimization on the test set is prohibited.

### 8. Regime-conditional evaluation
Performance is evaluated separately by market regime so a good aggregate score cannot hide catastrophic behavior in one regime.

### 9. Feature and data drift monitoring
Population Stability Index is available for comparing research/live feature distributions. Drift thresholds are configured at warning 0.10 and fail 0.25.

### 10. Cross-sectional and portfolio controls
Signals can be ranked cross-sectionally with sector neutrality and name/sector concentration caps. This avoids allowing ten correlated banking signals to masquerade as ten independent opportunities.

### 11. Point-in-time data provenance
Provider inputs can be checked for `asof_time <= signal_time`, and point-in-time backward joins are available. Fundamentals, corporate actions, news and derivatives data must be timestamped as-of data rather than backfilled values.

### 12. Economic validation
Predictive metrics and trading economics are reported separately. A model is not considered deployable merely because AUC, accuracy, or a label hit rate improves. Costs, slippage, barrier outcomes, drawdown and stability must also pass.

## Additional data that can materially improve signal quality

The architecture accepts, but does not fabricate:

- point-in-time fundamentals and valuation ratios;
- earnings and corporate-event calendars;
- corporate actions and adjusted-price metadata;
- sector/index breadth;
- India VIX and volatility surface data;
- option implied volatility, PCR and open-interest changes;
- futures basis and roll information;
- delivery percentage and turnover;
- bid/ask spread, depth and order-book imbalance;
- timestamped news and sentiment;
- market microstructure features for intraday models.

Every external observation must carry an availability/as-of timestamp. NSE publishes separate market-data and corporate-data products and its data-sharing/usage policy governs commercial access and redistribution.

## Research evidence

Financial-ML evaluation literature repeatedly identifies information leakage, non-IID validation, backtest overfitting and multiple testing as major sources of inflated results. Purging, embargoing, CPCV, falsification tests, DSR and PBO are therefore treated as research controls rather than optional reporting metrics.

Triple-barrier labels are also not sufficient proof of economic value. A model can predict a label while the resulting portfolio rule loses money after the execution contract and costs are applied. The package therefore requires a separate economic backtest.

## Synthetic audit result

The included synthetic audit is a software/methodology diagnostic only and is not market evidence.

Latest 700-row synthetic run:

- OOS AUC: approximately 0.593
- OOS accuracy: approximately 0.568
- OOS log loss: approximately 0.6903 vs 0.6931 50/50 baseline
- OOS Brier: approximately 0.2482 vs 0.2500 50/50 baseline
- CPCV splits: 15
- Fixed-horizon backtest: positive total return but large drawdown and only modest profit factor
- Triple-barrier backtest: negative total return, negative Sharpe and profit factor below 1

The negative triple-barrier result is deliberately retained. The framework should reject a weak economic rule instead of presenting a favorable metric from a different target definition.

## Deployment gate

A production signal should be published only when all applicable gates pass:

1. data quality;
2. point-in-time provenance;
3. untouched OOS predictive improvement;
4. probability calibration;
5. regime stability;
6. feature stability;
7. drift tolerance;
8. uncertainty/conformal gate;
9. realistic transaction/slippage/impact costs;
10. economic performance;
11. concentration/liquidity constraints;
12. signal freshness and event-risk gates.

If a gate fails, the correct output is **NO SIGNAL / MODEL NOT DEPLOYABLE**.

## Important limitation

No collection of indicators, models or validation techniques can guarantee future accuracy. The objective is to reduce known sources of false confidence and improve the probability that a published signal represents a reproducible, cost-adjusted out-of-sample relationship.

## Primary references

- TA-Lib function catalogue: https://ta-lib.org/functions/
- NSE data policy: https://www.nseindia.com/static/market-data/nse-data-policy
- NSE historical/EOD data: https://www.nseindia.com/static/market-data/eod-historical-data-subscription
- NSE corporate data: https://www.nseindia.com/static/market-data/corporate-data-subscription
- Rana, Evaluation Integrity in Machine Learning for Finance (SSRN): https://papers.ssrn.com/sol3/Delivery.cfm/7007079.pdf?abstractid=7007079&mirid=1&type=2
- Bailey et al., The Probability of Backtest Overfitting: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
- Bailey & López de Prado, The Deflated Sharpe Ratio: https://doi.org/10.3905/jpm.2014.40.5.094
