# NSE Signal Provider — Canonical V31 Architecture

A production-grade, India-wide NSE market-signal research and publication platform built on authoritative historical market data, point-in-time (PIT) processing, causal feature engineering, and fail-closed production controls.

---

## Absolute Operational Invariants

1. **Signal-Only Boundary**: `REAL_TRADING = FALSE` is permanently enforced across code, configuration, and API routes. Zero broker credentials, order placement, or trade execution routes exist.
2. **Production Universe**: `BroadNSEEquityUniverse` — derived exclusively from historical security identity (`[effective_from, effective_to)`) and causal historical price/volume observations. NIFTY 200 membership is **not** a prerequisite for broad NSE production signals.
3. **Research Benchmark Universe**: `Nifty200BenchmarkUniverse` — used strictly when requested universe explicitly equals `nifty200`. Fails closed if historical membership is unavailable.
4. **Authoritative Data Policy**: Production PIT pipelines require official NSE raw archives (UDiFF Common Bhavcopy & Security Master across 2014–2026). Secondary providers (Upstox, 5paisa, Angel One, FYERS, Dhan, Groww, Yahoo) are non-authoritative (`SECONDARY_UNOFFICIAL`), explicitly opt-in (`ALLOW_SECONDARY_PROVIDER=true`), and can **never** satisfy production PIT readiness.
5. **Fail-Closed Production Gate**: Evaluated dynamically across 20 distinct evidence categories via `src/nse_signal/data/production_gate.py`.

---

## Current Production Gate Status

- **Status**: **`BLOCKED`** (`FINAL_PRODUCTION_GATE.json`)
- **Active Blockers**: 
  - Insufficient multi-year validated historical coverage depth (< 500 trading days for full window).
  - Insufficient unique historical trading dates for full multi-fold chronological walk-forward folds.
  - Out-of-sample probability calibration and conformal validation pending complete multi-year OOS partition depth.

---

## Quick Start & Current Run Commands

### 1. Start the Read-Only FastAPI Server
```bash
python -m uvicorn server.api:app --host 127.0.0.1 --port 8010
```
Or execute:
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

### 4. Evaluate Machine-Verified Production Gate
```bash
python scripts/run_production_gate.py
```

---

## Android Client State
- **Role**: Read-only signal viewing and Firebase authentication (`analyst` role authorization).
- **Invariants**: Strictly signal-only; zero broker or trading execution UI.
- **Build**: Gradle build configured for debug and release builds.
- **Runtime**: `ANDROID_RUNTIME = NOT_EXECUTED` (Headless agent container environment lacks an active connected AVD or physical device).

---

## Documentation & History
- **Evidence Matrix**: [docs/PRODUCTION_GATE_EVIDENCE_MATRIX.md](docs/PRODUCTION_GATE_EVIDENCE_MATRIX.md)
- **Historical Evolution**: [docs/history/V8_TO_V30_HISTORICAL_EVOLUTION.md](docs/history/V8_TO_V30_HISTORICAL_EVOLUTION.md)
