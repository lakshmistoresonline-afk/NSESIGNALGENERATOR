# Signal Generation Pipeline Audit (Prompt 70)

## 1. Executive Summary
This audit traces the complete signal-generation architecture from authoritative market data through point-in-time (PIT) processing, universe selection, feature engineering, model inference, calibration, conformal prediction, risk/filter gates, publication gating, persistence, backend APIs, web dashboard, and Android client.

---

## 2. Pipeline Trace & Component Inventory

| Pipeline Stage | Component / File | Classification | Findings & Architectural Gap |
| :--- | :--- | :--- | :--- |
| **Authoritative Market Data** | `data/raw/nse/`, `archives.py` | EXISTING | Official NSE raw archives (CM Bhavcopy, Security Master) stored immutably with SHA-256 provenance. |
| **PIT Data Layer** | `store.py`, `pit_layer_validator.py` | EXISTING | Authoritative PIT stores (`cash_daily.csv`, `security_master.csv`) enforced by semantic validators. |
| **Universe Selection** | `universe_policy.py`, `membership.py` | EXISTING | Separates production `BroadNSEEquityUniverse` from benchmark `Nifty200BenchmarkUniverse`. |
| **Feature Generation** | `features/build.py` | EXISTING | Causal technical and fundamental features calculated strictly point-in-time. |
| **Model Inference** | `models/production.py`, `walk_forward.py` | EXISTING | Ensemble model prediction with input feature schema hash and dataset manifest hash. |
| **Probability Calibration** | `research/calibration.py` | EXISTING | Out-of-sample TimeOrderedCalibrator for probability adjustments. |
| **Conformal Prediction** | `models/production.py` | EXISTING | Class-conditional conformal p-values and abstention logic. |
| **Risk / Filter Gates** | `risk/publication.py`, `signals/engine.py` | EXISTING | Regimes, ADX, liquidity, risk/reward (min 2.0), and uncertainty gates. |
| **Signal Decision** | `SignalEngine.generate` | EXISTING | Evaluates probability thresholds, factor scores, and gate passes. |
| **Publication Gate** | `risk/publication.py` | EXISTING | Fails-closed signal publication checks based on gate criteria. |
| **Persistence** | `published_signals.json` | BROKEN / DANGEROUS | Currently depends on static/ephemeral JSON files rather than a robust, queryable signal store. |
| **Backend API** | `server/api.py` | MISSING / BROKEN | Lacks comprehensive historical and live queryable endpoints with robust pagination and filter contracts. |
| **Web Dashboard** | `frontend/` | MISSING | Basic static display; lacks real-time streaming, historical drill-down, and professional analytics. |
| **Android Dashboard** | `android/` | MISSING | Read-only UI requires full integration with canonical signal APIs. |

---

## 3. Findings Classification

- **EXISTING**: Authoritative raw data, PIT identity, Broad NSE universe, causal features, model inference, calibration, conformal prediction, publication gates, and invariant `REAL_TRADING = FALSE`.
- **MISSING**: Durable queryable signal store, historical signal generation engine, live streaming session orchestrator, comprehensive historical/live API routes, and advanced dashboard views.
- **BROKEN**: Static JSON persistence (`published_signals.json`) lacking indexing, pagination, and multi-version lineage.
- **DANGEROUS**: Potential overlap between research demo scripts and production publication paths if not strictly isolated by `DATA_MODE`.
- **REQUIRES IMPLEMENTATION**: Prompts 71–86 (Canonical signal contract, historical engine, live engine, orchestration, signal store, lifecycle tracking, APIs, frontend rebuild, real-time updates, jobs, analytics, Android integration, and end-to-end validation).
