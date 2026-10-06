# Deep Accuracy Hardening Audit — V26 Candidate

## Scope
Source-level audit of the uploaded `V25_RECONSTRUCTED` package, including the complete Python test suite, signal engine, feature construction, PIT layer handling, validation, backtesting and production model lifecycle.

## Baseline verification
- ZIP integrity: verified before extraction.
- Original test suite before changes: 93 passed.
- Final suite after changes: 96 passed.
- No broker order-placement implementation was added.
- `REAL_TRADING=False` / signal-only boundary remains enforced.

## Release-blocking defects fixed

### 1. Cross-symbol rolling-window contamination
The generic feature builder could apply rolling indicators to a concatenated multi-symbol frame. Rolling windows must be calculated independently per security before cross-sectional features are created.
**Fix:** `make_features()` now groups by symbol, sorts by timestamp, computes all causal rolling features per symbol, then combines the results for same-timestamp cross-sectional features.

### 2. Ambiguous market-regime context
`market_sma_200_gap`, market volatility and trend features could be derived from the security's own close when the input did not contain an actual benchmark. That is a stock trend proxy, not market regime.
**Fix:** regime construction now prefers explicit `benchmark_close` / `nifty_close` / `market_close` / `index_close`; panel data can use a clearly labelled same-timestamp cross-sectional median-return proxy. A stock-only fallback is labelled `stock_proxy` and is rejected by the signal engine when supplied as market context.

### 3. Conformal calibration data reuse
The previous walk-forward implementation fitted probability calibration and conformal coverage using the same tail observations. That re-use weakens the claimed conformal coverage property.
**Fix:** the calibration tail is split chronologically: earlier tail observations fit the probability calibrator; later tail observations are reserved for conformal calibration.

### 4. Gap-through-barrier backtest bias
Triple-barrier exits could value a later gap-through stop/target at the barrier price even though a real next-bar-open execution would occur at the gap price.
**Fix:** barrier labels now execute gap-through events at the actual bar open and retain explicit `profit_gap` / `stop_gap` event types.

### 5. Non-reproducible signal timestamps
Signals used `datetime.now()` even when evaluating historical/replayed data.
**Fix:** `decision_timestamp` is accepted and normalized to UTC when supplied; wall-clock time remains only the live default.

### 6. Production inference lifecycle was incomplete
The package had a model registry but no serialized production candidate artifact lifecycle.
**Fix:** added `models/production.py`, candidate training, atomic joblib artifact storage, contract hashing, champion-only signal generation script, and explicit fail-closed behavior when no champion exists.

### 7. Cross-sectional concentration filter
The previous cross-sectional filter exposed a `max_correlated` argument but did not actually enforce correlation-based crowding control.
**Fix:** correlation-aware selection and sector caps are now applied before final signal count.

### 8. Benchmark/index readiness
A production-accuracy architecture needs actual benchmark context rather than relying only on per-stock proxies.
**Fix:** the production-required PIT layers now include an index dataset, and the dashboard/readiness layer recognizes it.

## Accuracy architecture retained
- Official NSE/NSE Clearing/NSE Indices PIT-first policy.
- Effective-dated historical universe requirement.
- Purged walk-forward evaluation.
- Event-uniqueness weighting.
- Multi-horizon research controls.
- Calibration and conformal abstention.
- CPCV/PBO/DSR research controls.
- Cost-aware publication.
- Delivery/impact-cost/surveillance/price-band/short-sale restrictions.
- Signal-only safety boundary.

## Important production limitations
The package still does **not** contain licensed historical NSE market bytes or historical Nifty 200 constituent snapshots. Therefore, the correct production state remains **blocked** until the operator supplies the required authoritative datasets and records the applicable usage rights. Free secondary providers are useful for research/operational redundancy but are not substituted for authoritative PIT history.

NSE currently publishes UDiFF capital-market and F&O bhavcopies and related reports; its current report catalogue includes price-band, surveillance, delivery, impact-cost and daily-volatility data. NSE's current market-timing pages show the equity regular session at 09:15–15:30 IST and equity derivatives at 09:15–15:40 IST. These exchange mechanics are incorporated as governance inputs rather than as assumptions about future returns.

## What this release does not claim
No software change can guarantee a particular signal hit rate or future return. Accuracy must be established on unseen, point-in-time, transaction-cost-aware Indian-market data. The package therefore fails closed instead of fabricating missing PIT evidence.
