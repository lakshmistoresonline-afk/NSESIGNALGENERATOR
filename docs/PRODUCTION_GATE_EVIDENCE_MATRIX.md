# Production Gate Evidence Matrix (Prompt 39 Required PIT Layer Contract Verified)

- **Evaluated At**: 2026-10-08T05:16:03.823938+00:00
- **Overall Status**: `BLOCKED`
- **Eligible**: `False`

| Category ID | Name | Status | Evidence Path | Evidence Hash (SHA256) | Failure Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `historical_coverage` | Historical Data Coverage | `PASS` | `data/processed/final_historical_coverage.json` | `43ea1d8df973...` | N/A |
| `raw_integrity` | Raw-File Integrity | `PASS` | `data/processed/final_raw_integrity.json` | `bd2afa47cb44...` | N/A |
| `security_identity` | Historical Security Identity | `PASS` | `data/processed/final_identity_validation.json` | `031ab1f87c9b...` | N/A |
| `production_universe` | Production Universe (BroadNSEEquityUniverse) | `PASS` | `data/processed/final_identity_validation.json` | `031ab1f87c9b...` | N/A |
| `benchmark_nifty200` | Benchmark Nifty 200 Universe (Nifty200BenchmarkUniverse) | `PASS` | `data/processed/universe/nifty200_validation.json` | `78985728f47a...` | N/A |
| `pit_temporal_integrity` | PIT Temporal Integrity | `PASS` | `data/processed/final_pit_temporal_validation.json` | `a9a31a5304df...` | N/A |
| `required_pit_layers` | Required PIT Layers | `BLOCKED` | `data/processed/nse_pit/cash_daily.csv` | `MISSING_FILE...` | MISSING_OR_INVALID_EVIDENCE_FILE: data/processed/nse_pit/cash_daily.csv (MISSING_FILE) |
| `corporate_action_correctness` | Corporate-Action Correctness | `PASS` | `data/processed/nse_pit/corporate_action_validation.json` | `7bfc4b038d50...` | N/A |
| `model_walk_forward` | Model Walk-Forward Validation | `PASS` | `docs/REAL_WALK_FORWARD_REPORT.md` | `86275b5306d5...` | N/A |
| `calibration` | Probability Calibration | `PASS` | `data/processed/model_validation/calibration.json` | `36c07ab1351e...` | N/A |
| `conformal_validation` | Conformal Validation | `PASS` | `data/processed/model_validation/conformal.json` | `072208539092...` | N/A |
| `economic_validation` | Economic Validation | `PASS` | `data/processed/model_validation/economic_validation.json` | `d132841ac372...` | N/A |
| `drift` | Model Drift (Pre-Deployment Historical) | `PASS` | `data/processed/model_validation/historical_drift.json` | `44e37890a7b6...` | N/A |
| `adversarial_validation` | Adversarial Validation | `PASS` | `src/nse_signal/research/adversarial.py` | `97efe84db0d5...` | N/A |
| `multiple_testing_controls` | Multiple-Testing Controls | `PASS` | `src/nse_signal/research/falsification.py` | `b639256cfe2b...` | N/A |
| `untouched_holdout` | Untouched Holdout | `PASS` | `data/processed/nse_pit/pit_features.csv` | `03f26d04d5cc...` | N/A |
| `forensic_tests` | Forensic Tests | `PASS` | `data/processed/forensics/MUTATION_TEST_RESULTS.json` | `6929733dff3a...` | N/A |
| `clean_room_rebuild` | Clean-Room Rebuild | `PASS` | `docs/CLEAN_ROOM_VALIDATION_REPORT.md` | `de9597682279...` | N/A |
| `android_build` | Android Build | `PASS` | `android/app/build/outputs/apk/debug/app-debug.apk` | `18404fb252a7...` | N/A |
| `android_runtime` | Android Runtime E2E | `NOT_EXECUTED` | `docs/ANDROID_RUNTIME_VALIDATION.md` | `02f21c5daf0a...` | Headless agent environment lacks active AVD or physical device |
| `signal_only_safety` | Signal-Only Safety (REAL_TRADING=FALSE) | `PASS` | `reports/final_completion/trading_safety.json` | `7ddbd8b4477b...` | N/A |