# NSE Signal Provider — Canonical V31 Architecture

A production-grade, India-wide NSE market-signal provider built on authoritative historical market data, point-in-time (PIT) processing, causal feature engineering, and fail-closed production controls.

## Absolute Product Invariants
- **Signal-Only Product**: `REAL_TRADING = FALSE` is permanently enforced in configuration and code.
- **No Broker Execution**: Zero broker login, order placement, trade execution, portfolio management, or trade execution routes exist.
- **Fail-Closed Governance**: Production publication and readiness gates are evidence-driven and fail closed when data or validation requirements are incomplete.

## Universe Architecture
- **Production Universe**: `BroadNSEEquityUniverse` — derived exclusively from historical security identity and causal historical observations (allowed series, listing status, minimum price, liquidity, and history). NIFTY 200 membership is **not** a prerequisite for broad NSE production signals.
- **Benchmark / Research Universe**: `Nifty200BenchmarkUniverse` — used strictly when requested universe explicitly equals `nifty200`. Fails closed if historical membership is unavailable.

## Point-in-Time (PIT) Requirements
- All temporal intervals enforce the strict half-open contract: `[effective_from, effective_to)`.
- No look-ahead bias, future data leakage, or survivorship bias.
- Authoritative multi-year historical NSE archives (2014–2026) with SHA-256 provenance (`data/raw/nse/`).

## Machine-Verified Production Gate
- Evaluated via `src/nse_signal/data/production_gate.py` across 20 distinct evidence categories.
- Current Status: **`BLOCKED`** (`FINAL_PRODUCTION_GATE.json`) due to fail-closed model validation and multi-year historical coverage expansion constraints.

## Quick Start & Run Commands

### 1. Start the API Server
```bash
python -m uvicorn server.api:app --host 127.0.0.1 --port 8010
```
Or use the provided batch script:
```text
run_server.bat
```

### 2. Run the Verification Test Suite
```bash
python -m pytest
```

### 3. Run Historical Ingestion & PIT Pipeline
```bash
python scripts/acquire_authoritative_pit.py --start 2024-01-02 --end 2024-01-31 --layers cash_bhavcopy,security_master
python scripts/build_pit_dataset.py
python scripts/validate_pit_dataset.py
```

## Android Client
- **Role**: Read-only signal viewing, Firebase authentication (`analyst` role authorization), and secure token handling.
- **Invariants**: Strictly signal-only; no broker or trading execution UI.
- **Build**: Compiled via Gradle (`gradlew.bat assembleDebug assembleRelease`).
- **Runtime**: `ANDROID_RUNTIME = NOT_EXECUTED` (Headless agent environment lacks active AVD or physical device).

## Historical Evolution
For past V8–V30 release history and migration notes, see [docs/history/V8_TO_V30_HISTORICAL_EVOLUTION.md](docs/history/V8_TO_V30_HISTORICAL_EVOLUTION.md).
