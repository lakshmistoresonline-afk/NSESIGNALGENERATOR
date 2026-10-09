# Production Gate Evidence Matrix (Fail-Closed Non-Pass Blocking Verified)

- **Evaluated At**: 2026-10-09T01:11:42.673041+00:00
- **Overall Status**: `BLOCKED`
- **Eligible**: `False`

| Category ID | Name | Status | Evidence Path | Evidence Hash (SHA256) | Failure Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `historical_coverage` | Historical Data Coverage | `PASS` | `data/processed/final_historical_coverage.json` | `4d0b9a4e1dee...` | N/A |
| `raw_integrity` | Raw-File Integrity | `PASS` | `data/processed/final_raw_integrity.json` | `bd2afa47cb44...` | N/A |
| `security_identity` | Historical Security Identity | `PASS` | `data/processed/final_identity_validation.json` | `1b41857e0bbe...` | N/A |
| `production_universe` | Production Universe (BroadNSEEquityUniverse) | `PASS` | `data/processed/final_identity_validation.json` | `1b41857e0bbe...` | N/A |
| `benchmark_nifty200` | Benchmark Nifty 200 Universe (Nifty200BenchmarkUniverse) | `PASS` | `data/processed/universe/nifty200_validation.json` | `300ebb72179d...` | N/A |
| `pit_temporal_integrity` | PIT Temporal Integrity | `PASS` | `data/processed/final_pit_temporal_validation.json` | `c8e9da8bd204...` | N/A |
| `required_pit_layers` | Required PIT Layers | `BLOCKED` | `data/processed/nse_pit/cash_daily.csv` | `MISSING_FILE...` | MISSING_OR_INVALID_EVIDENCE_FILE: data/processed/nse_pit/cash_daily.csv (MISSING_FILE) |
| `corporate_action_correctness` | Corporate-Action Correctness | `PASS` | `data/processed/nse_pit/corporate_action_validation.json` | `c897594ed1e1...` | N/A |
| `model_walk_forward` | Model Walk-Forward Validation | `PASS` | `docs/REAL_WALK_FORWARD_REPORT.md` | `b0d249b6c5d1...` | N/A |
| `calibration` | Probability Calibration | `PASS` | `data/processed/model_validation/calibration.json` | `52221fe15f41...` | N/A |
| `conformal_validation` | Conformal Validation | `PASS` | `data/processed/model_validation/conformal.json` | `76eb18c9b43a...` | N/A |
| `economic_validation` | Economic Validation | `PASS` | `data/processed/model_validation/economic_validation.json` | `898142a860e3...` | N/A |
| `drift` | Model Drift (Pre-Deployment Historical) | `PASS` | `data/processed/model_validation/historical_drift.json` | `1881881f1de3...` | N/A |
| `adversarial_validation` | Adversarial Validation | `PASS` | `src/nse_signal/research/adversarial.py` | `97efe84db0d5...` | N/A |
| `multiple_testing_controls` | Multiple-Testing Controls | `PASS` | `src/nse_signal/research/falsification.py` | `b639256cfe2b...` | N/A |
| `untouched_holdout` | Untouched Holdout | `PASS` | `data/processed/nse_pit/pit_features.csv` | `03f26d04d5cc...` | N/A |
| `forensic_tests` | Forensic Tests | `PASS` | `data/processed/forensics/MUTATION_TEST_RESULTS.json` | `6929733dff3a...` | N/A |
| `clean_room_rebuild` | Clean-Room Rebuild | `PASS` | `docs/CLEAN_ROOM_VALIDATION_REPORT.md` | `de9597682279...` | N/A |
| `android_build` | Android Build | `PASS` | `android/app/build/outputs/apk/debug/app-debug.apk` | `18404fb252a7...` | N/A |
| `android_runtime` | Android Runtime E2E | `NOT_EXECUTED` | `docs/ANDROID_RUNTIME_VALIDATION.md` | `02f21c5daf0a...` | Headless agent environment lacks active AVD or physical device |
| `signal_only_safety` | Signal-Only Safety (REAL_TRADING=FALSE) | `PASS` | `reports/final_completion/trading_safety.json` | `7ddbd8b4477b...` | N/A |