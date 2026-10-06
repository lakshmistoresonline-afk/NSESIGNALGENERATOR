# Final Implementation Traceability Matrix

| Requirement | Implementation File(s) | Function / Class | Actual Runtime Path | Test(s) | Test Command | Observed Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Signal-Only Product (`REAL_TRADING=FALSE`)** | `src/nse_signal/cli.py`, `src/nse_signal/signals/engine.py` | `REAL_TRADING`, SignalEngine | CLI / API / Signals | `test_core.py`, `test_v30_auth_security.py` | `python -m pytest` | Enforced | `IMPLEMENTED` |
| **NSE UDiFF Acquisition & Ingestion** | `src/nse_signal/data/nse/archives.py`, `src/nse_signal/cli.py` | `run_real_ingestion`, CLI `--ingest` | CLI Ingest Pipeline | `test_nse_integration.py` | `python -m pytest` | 2/2 Dates Ingested | `IMPLEMENTED` |
| **PIT Security Master & Intervals** | `src/nse_signal/data/pit_builder.py`, `src/nse_signal/data/pit_validator.py` | `build_pit_dataset`, `validate_pit_dataset` | CLI `--build-pit`, `--validate-pit` | `test_v31_pit_reconstruction.py` | `python -m pytest` | 28,464 intervals | `IMPLEMENTED` |
| **Row Accounting & Reconciliation** | `src/nse_signal/data/pit_builder.py`, `pit_forensic_validator.py` | Two-tier observation accounting | PIT Build & Audit | `test_v31_pit_reconstruction.py` | `python -m pytest` | `unaccounted_rows == 0` | `IMPLEMENTED` |
| **Clean-Room Forensic Rebuild & Determinism** | `src/nse_signal/data/forensic/cleanroom.py`, `runner.py` | `execute_clean_room_rebuild` | Forensic Suite | `test_v31_pit_reconstruction.py` | `python -m pytest` | `determinism_status: PASS` | `IMPLEMENTED` |
| **AST Validation Audit** | `src/nse_signal/data/forensic/ast_audit.py` | `run_ast_audit` | Forensic Suite | `test_v31_pit_reconstruction.py` | `python -m pytest` | Scanned successfully | `IMPLEMENTED` |
| **Firebase Auth & Backend Authorization** | `src/nse_signal/utils/config.py`, `server/api.py` | FastAPI Security / Firebase Admin SDK | API / CLI | `test_v30_auth_security.py` | `python -m pytest` | Verified | `IMPLEMENTED` |
| **Android Build & APK Generation** | `android/`, `gradlew.bat` | Gradle build tasks | Gradle wrapper | Unit Tests / Gradle | `gradlew.bat assembleDebug` | Success (13.1MB APK) | `IMPLEMENTED` |
| **Historical Universe / Index Membership** | `src/nse_signal/data/universe.py`, `membership.py` | `get_universe_as_of` | Feature / Signal Engine | `test_core.py` | `python -m pytest` | Fail-closed on unknown | `PARTIALLY_IMPLEMENTED` |
| **Android Runtime E2E** | `android/` | UI / Compose / Repository | Android Device / AVD | None | N/A | No active AVD | `BLOCKED_EXTERNAL_DEPENDENCY` |
