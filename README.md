# V30 India-Wide Accuracy Hardening

V30 is the hardened successor to V29. It remains **signal-only** (`REAL_TRADING=false`) and does not place broker orders.

## V30 critical fixes
- India-wide PIT build now defaults to the broad NSE equity universe (`EQ`), with NIFTY 200 explicitly benchmark-only.
- Automatic secondary-provider fallback is disabled; secondary data requires explicit opt-in.
- Row-based walk-forward validation now rejects multi-security panels; panels must use timestamp-grouped `panel_walk_forward`.
- Economic backtests are symbol-safe for multi-security panels.
- PIT production signal generation is fail-closed on provenance, manifest, data-governance, restriction, event and market-context requirements.
- Production factor support is computed from causal trailing momentum percentiles rather than a hard-coded 0.50.
- PIT build canonicalizes impact cost and restriction fields and derives conservative corporate-event blackout flags.
- Unknown NSE calendar years now fail closed instead of being treated as business days.
- OHLCV validation now reports missing columns cleanly instead of crashing.
- Production remains blocked until authoritative PIT datasets are actually present, complete, and licensed.

## Validation
- Test suite: 110 passed.
- Python compilation: passed.
- Multi-security backtest smoke test: passed with symbol-isolated trade construction.
- Synthetic metrics remain diagnostics only and are not evidence of future market accuracy.

# NSE Signal Provider — Unified Research + Android Package

A self-contained **NSE stock signal research platform** combining the strongest engineering ideas selected from the referenced public projects and the user's TradeMindAI architecture.

## Hard product boundary

- **Signal provider only.**
- `REAL_TRADING = FALSE` is enforced in configuration and code.
- No broker login.
- No order placement.
- No portfolio execution engine.
- No automatic trade execution.

The application is designed to research and publish signals; it does **not** promise a particular accuracy or profitability level.


## Browser dashboard

The release includes a self-contained read-only frontend dashboard served by FastAPI; no Node/npm runtime is required.

Start with `run_server.bat` on Windows or `run_server.sh` on Linux/macOS, then open:

```text
http://127.0.0.1:8010/dashboard
```

The dashboard is fail-closed: it displays `PIT BLOCKED` until required NSE datasets, effective-dated NIFTY 200 membership, and provenance/checksum evidence are present. It only displays validated published signal artifacts and cannot create or execute orders.

## Release-candidate safety behavior

Production publication requires the PIT data contract, effective-dated universe, provenance manifest, economic context, restriction checks, and signal publication gates. Malformed or execution-enabled published signal artifacts are rejected by the dashboard API.

## Included capabilities

### TradeMindAI-derived integration

- Market-regime overlay
- Adaptive ATR risk geometry
- Signal quality gates
- Signal provenance concepts
- Outcome lifecycle concepts
- Shadow/paper signal architecture
- Signal-only safety boundary

### Research stack

- Point-in-time / no-lookahead feature design
- Purged walk-forward validation with embargo
- Probability calibration
- OOS diagnostics: AUC, accuracy, log loss, Brier score
- Cost/slippage-aware backtesting
- Cross-sectional factor ranking
- Research statistics and robustness controls
- Strategy-falsification workflow

### Applications

1. **FastAPI server** — `server/api.py`
2. **Streamlit research dashboard** — `app/app.py`
3. **Python CLI** — `src/nse_signal/cli.py`
4. **Android Studio client** — `android/`
5. **Offline synthetic market-data mode** — works without a market-data API

## Windows quick start

### 1. Start the API

Double-click:

```text
run_server.bat
```

The API starts at:

```text
http://localhost:8010
```

Health check:

```text
http://localhost:8010/health
```

### 2. Open the frontend dashboard

Open `http://localhost:8010/dashboard` in a browser.

### 3. Run the research dashboard

Double-click:

```text
run_streamlit.bat
```

### 4. Run the offline validation suite

Double-click:

```text
run_sample_test.bat
```

This uses synthetic data and does not require a broker or paid data feed.

## API

### Health

`GET /health`

### Generate signal

`POST /signal`

Example:

```json
{
  "symbol": "RELIANCE.NS",
  "probability_up": 0.68,
  "factor_score": 0.65,
  "threshold": 0.55
}
```

### Research

`POST /research`

Example:

```json
{
  "symbol": "RELIANCE.NS",
  "rows": 700
}
```

The research endpoint uses synthetic data by design so that the application can be verified without external credentials.

## Live NSE data

The Python data adapter supports `yfinance` as an optional/public-data adapter. For production-quality research, replace this with a properly licensed, point-in-time Indian market-data source and retain the same data interface.

Cached files go under `data/raw/` and should not be committed.

## Android Studio

Open:

```text
android/
```

The Android app is a client for the FastAPI server.

### Emulator

Use:

```text
http://10.0.2.2:8010
```

### Physical Android device

Use the Windows machine's LAN address, for example:

```text
http://192.168.x.x:8010
```

Ensure Windows Firewall permits inbound TCP 8010 on the private network.

## Android safety boundary

The Android client only sends signal/research requests to the local API. There is no broker SDK, broker credential field, or order-placement endpoint.

## Architecture

```text
NSE / cached market data
        |
        v
Point-in-time data layer
        |
        v
Feature engineering
        |
        +--> technical features
        +--> cross-sectional factors
        +--> regime features
        |
        v
Purged walk-forward ML
        |
        v
Probability calibration
        |
        v
Signal quality / no-trade gates
        |
        v
Cost-aware OOS backtest
        |
        v
Paper signal API
        |
        v
Android / Streamlit UI
```

## Important research limitation

A high historical win rate is not, by itself, evidence of a durable trading edge. The project therefore emphasizes unseen-data validation, leakage controls, costs, slippage, calibration, drawdown and robustness instead of an advertised accuracy target.

## Upstream references

See `docs/REPOSITORY_SOURCES.md`, `docs/UPSTREAM_REPOSITORIES.md`, and `docs/INTEGRATION_MATRIX.md` for the public repositories and the specific ideas incorporated.

## Indicator coverage

The canonical feature layer includes configurable: SMA/EMA trend stacks (5/10/20/50/100/200), RSI (7/14/21), ROC, MACD, stochastic %K/%D, ADX/+DI/-DI, CCI, Williams %R, MFI, CMF, OBV, TSI, Awesome Oscillator, ATR (5/14/20), realized volatility, Bollinger Bands/width/position, Donchian channels, Keltner channels, Parabolic SAR, VWAP, price/EMA/SMA gaps, EMA-stack regime, gap/range/body/wick structure, volume ratios/z-scores, dollar turnover z-score, multi-horizon returns, breakout/breakdown flags, ATR/range z-scores, and optional NSE context fields such as India VIX, NIFTY/sector returns, FII/DII flows, advance-decline ratio, PCR, open-interest change and futures basis.

The parameter source of truth is `config/indicator_parameters.yaml`. Optional market/derivatives fields remain nullable when the upstream provider does not supply them; the system does not fabricate missing inputs.

NSE session logic is aligned to the exchange schedule: regular equities trading is 09:15–15:30 IST, with separate pre-open and closing sessions. citeturn0search0turn0search2 India VIX is treated as a 30-calendar-day expected-volatility input when supplied, consistent with NSE's methodology. citeturn0search1turn0search47 The default universe is designed around Nifty 200 research, which NSE describes as comprising Nifty 100 and Nifty Midcap 100 constituents. citeturn0search5

This application remains signal-only. No broker order endpoint is included. If broker/API execution is ever added, it must be separately reviewed against the applicable SEBI/broker framework; SEBI's retail algorithmic-trading framework has specific requirements and implementation standards. citeturn0search4turn0search6turn0search48

## Indicator audit note
The indicator engine is cross-checked against the current TA-Lib catalogue. The project distinguishes executable causal indicators from provider-supplied NSE context and from generic/candlestick families requiring separate regression fixtures. See `docs/INDICATOR_AUDIT_2026-10-02.md`.


## Latest indicator audit

The latest audit uses 223 named functions in the exact TA-Lib reference catalogue and 212 controlled causal candidate features in the default ML matrix. EMA seeding, SMI, stochastic parameterization, BBANDS/APO/PPO/PVO MA types, Donchian parameter wiring and target isolation have been explicitly tested. See `docs/INDICATOR_AUDIT_2026-10-02.md`.

## Accuracy Architecture — Final Release

This release goes beyond technical indicators. It includes data-quality gates, separate causal labels, triple-barrier events, purge+embargo walk-forward validation, fold-local feature selection, time-ordered probability calibration, ensemble modeling, multi-horizon agreement, market-regime conditioning, meta-labeling, cost-aware backtesting, selective prediction, cross-sectional/sector controls, statistical robustness metrics, and live-drift monitoring hooks.

See `docs/FINAL_ACCURACY_AUDIT.md` and run `python scripts/run_research_audit.py` for an offline software audit. Synthetic results are not performance claims.

## Final Accuracy Governance

This release treats signal generation as a selective prediction problem, not an always-on forecasting problem. The model must pass predictive, calibration, stability, drift and economic gates before publication. Training uses fold-local feature selection and average event-uniqueness weighting. Validation uses purged/embargoed walk-forward plus optional CPCV. Labels and economic backtests share the same next-open execution contract. External fundamentals, corporate actions, derivatives, order-book and news/sentiment data must be point-in-time/as-of joined. The application remains signal-only and does not execute trades.

See `docs/FINAL_ACCURACY_RESEARCH_2026-10-02.md` and `docs/RESEARCH_SOURCES_2026-10-02.md`.

## Accuracy Final V5 — 2026-10-03

This release adds execution-consistent triple-barrier training labels, CPCV splitting, PBO and multiple-testing utilities, a stricter validation gate, and a point-in-time NIFTY 200 membership interface. The default system remains signal-only with real trading disabled. Synthetic audit results are diagnostics only and are not market-alpha evidence.


## Accuracy V6
See `docs/FINAL_ACCURACY_RESEARCH_2026-10-03_V6.md` for the latest research additions, synthetic audit interpretation, and remaining production-data requirements. V6 records ensemble disagreement and adds causal OHLCV volatility/liquidity/flow candidates while retaining strict OOS/economic publication gates.

## Accuracy Final V7
V7 adds selective prediction and evaluation controls: validation-only economic threshold selection, conformal abstention diagnostics, dependence-aware block bootstrap reporting, and multi-horizon agreement utilities. These controls are designed to reduce false positives and selection bias; they do not imply guaranteed live accuracy.

## V8 Accuracy Layer

V8 adds causal fractional-differentiation/event-time research utilities, conservative market-impact costing, and optional OOS meta-label and multi-horizon publication gates. Missing economic context fails closed.

## Real NSE point-in-time data integration

The project now includes a read-only official-NSE ingestion layer under `src/nse_signal/data/nse/` and `scripts/ingest_nse.py`. It downloads the published CM/FO UDiFF archive families, security masters and index files, records SHA-256 provenance, normalizes them into canonical schemas and refuses point-in-time violations. See `docs/NSE_POINT_IN_TIME_DATA_INTEGRATION.md` and `docs/DATA_ACQUISITION_RUNBOOK.md`.

Example:

```bash
python scripts/ingest_nse.py --start 2026-09-01 --end 2026-09-30
python scripts/validate_pit_dataset.py
```

Historical NIFTY 200 membership is **not fabricated**. Populate `data/reference/nifty200_membership.csv` from authoritative effective-dated constituent snapshots before enabling historical NIFTY 200 research. Current membership alone must not be backfilled into history.

## Real NSE PIT data phase
The package now includes official-source contracts and normalizers for delivery, impact cost, advances/declines, India VIX, corporate events and PIT fundamentals in addition to CM/F&O UDiFF and security master ingestion. Use `scripts/ingest_pit_layers.py` and `scripts/build_pit_dataset.py`. Missing or untimestamped information is rejected rather than fabricated.

## V13 PIT Integrity and NSE Context
V13 fixes daily ingestion overwrite, duplicate PIT joins, incomplete-cross-section leakage, empty-universe acceptance, and missing publication restrictions. It adds authoritative corporate-adjustment support, derivatives PCR/OI/IV context, surveillance/price-band/short-sale gates, participant/FII adapters, and stricter model-governance hooks. The application remains signal-only with REAL_TRADING=false.

## Frontend Dashboard — V14

V14 includes a self-contained **frontend dashboard** under `frontend/`. It is served directly by FastAPI and requires no Node/npm installation.

Start the API:

```text
run_server.bat
```

Then open:

```text
http://localhost:8010/dashboard
```

The dashboard shows:

- PIT readiness and required-layer status
- dataset row coverage
- provenance/manifest status
- published paper signals
- publication safety state
- impact-cost cap
- explicit `NO SIGNAL` when validated PIT data is unavailable
- explicit `REAL_TRADING = FALSE` safety boundary

The dashboard is **read-only** with respect to publication and contains no broker execution controls.

The legacy Streamlit research UI remains available through `run_streamlit.bat` for exploratory analysis.

## V18 authoritative PIT data
V18 uses official NSE/NSE Clearing/NSE Indices sources only for production PIT data. Run `acquire_authoritative_pit.bat 2026-09-01 2026-09-30` on a networked Windows machine to acquire official CM/F&O/security-master/index archive files with SHA-256 provenance. Historical Nifty 200 membership is a separate contract: the current constituent CSV is never backfilled into history; dated official constituent records or licensed historical constituent data are required.

## V19 data-governance hardening

Production market data no longer falls back to Yahoo/yfinance or another third-party downloader. A missing authoritative local NSE dataset fails closed. See `data/reference/authoritative_pit_data_gap_register.json` and `docs/AUTHORITATIVE_PIT_DATA_GAPS_2026-10-03.md` for the datasets that are not supplied/licensed in this release.

`/api/data-governance` exposes the current possession/licensing blockers. `/api/readiness`, `/api/data-health`, and `/api/publication-health` include this governance gate.

## Secondary market-data providers (research/current-data only)

V21 includes read-only secondary data adapters for Upstox, 5paisa, Angel One SmartAPI, FYERS, DhanHQ, Groww and explicit/manual Yahoo access. Upstox/5paisa are free secondary market-data sources; Yahoo is excluded from automatic fallback because current Yahoo terms restrict automated collection without permission. Secondary providers are explicitly tagged as non-authoritative and can never satisfy NSE PIT readiness. `ALLOW_SECONDARY_PROVIDER=true` is required. No order, broker-execution, portfolio or trade-placement methods are implemented in these adapters. V21 also adds provider-specific argument filtering, bounded retry/backoff, provider capability metadata, and cross-provider candle reconciliation.

Provider notes:
- Angel One SmartAPI: free historical API according to current SmartAPI documentation.
- FYERS: FYERS states historical/quotes/market data are free for FYERS users.
- DhanHQ: trading APIs are free, but Dhan currently prices Data APIs (including historical/real-time data) separately.
- Groww: current API pricing is INR 499 + taxes/month; it is not treated as a free-tier source.
- Yahoo Finance: public/secondary endpoint only; Yahoo terms restrict automated collection/commercial reuse, so it is never a production data-vending source.


## V28 accuracy hardening
See `docs/DEEP_ACCURACY_HARDENING_AUDIT_V28.md`. This release adds symbol-safe panel features, benchmark-aware regime context, two-stage conformal calibration, gap-aware barrier labels, reproducible decision timestamps, a serialized production model lifecycle, correlation-aware signal filtering, and explicit index readiness. Production remains fail-closed until authoritative PIT data and historical NIFTY 200 membership are actually supplied/licensed.


## V28 India-wide accuracy hardening

V28 adds:
- unique-timestamp market regime windows for multi-symbol panels
- broad NSE EQ-universe support with point-in-time security identity and trailing liquidity/history filters
- directional timeout labels for production/OOS training to reduce barrier-hit selection bias
- two-stage panel calibration and frozen conformal abstention
- mandatory governance evidence before a model can become CHAMPION
- TejHQ/BharatStock in the secondary research fallback hierarchy
- blocked operational status when required PIT/provenance controls are incomplete

The system remains **signal-only** (`REAL_TRADING=false`) and deliberately fails closed
when required authoritative PIT data, provenance, or governance evidence is unavailable.


## V30 temporal and publication hardening
- Production training/calibration boundaries are purged by the event horizon.
- Probability calibration and conformal calibration are separated by an event-horizon purge.
- Conformal uncertainty uses class-conditional finite-sample p-values.
- The validated publication threshold is frozen into the production model artifact.
- Production publication enforces model dispersion, signal age, valid NSE session, and causal factor context.
- Legacy production artifacts without V30 conformal calibration data fail closed.

See `docs/FINAL_ACCURACY_HARDENING_V30.md` for the complete audit.
