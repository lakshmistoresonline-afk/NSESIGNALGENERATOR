# Production Gate Evidence Matrix (Complete Raw Manifest Verified)

- **Evaluated At**: 2026-10-08T02:25:17.136305+00:00
- **Overall Status**: `BLOCKED`
- **Eligible**: `False`

| Category ID | Name | Status | Evidence Path | Evidence Hash (SHA256) | Failure Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `historical_coverage` | Historical Data Coverage | `BLOCKED` | `data/processed/final_historical_coverage.json` | `a7bc4c986ffb...` | LAYER_COVERAGE_INSUFFICIENT (corporate_actions): completeness ratio 0.0 < 0.50 |
| `raw_integrity` | Raw-File Integrity | `BLOCKED` | `data/processed/final_raw_integrity.json` | `2afc0cabd0b4...` | RAW_INTEGRITY_FAIL: invalid_entries=4, missing_files=0, hash_mismatches=0 |
| `security_identity` | Historical Security Identity | `PASS` | `data/processed/final_identity_validation.json` | `6777ce049538...` | N/A |
| `production_universe` | Production Universe (BroadNSEEquityUniverse) | `PASS` | `data/processed/final_identity_validation.json` | `6777ce049538...` | N/A |
| `benchmark_nifty200` | Benchmark Nifty 200 Universe (Nifty200BenchmarkUniverse) | `PASS` | `data/processed/universe/nifty200_validation.json` | `e508b4919c8c...` | N/A |
| `pit_temporal_integrity` | PIT Temporal Integrity | `PASS` | `data/processed/final_pit_temporal_validation.json` | `ffe2c4d56140...` | N/A |
| `required_pit_layers` | Required PIT Layers | `PASS` | `data/reference/feature_data_dependency_matrix.json` | `e43306c05037...` | N/A |
| `corporate_action_correctness` | Corporate-Action Correctness | `PASS` | `data/processed/nse_pit/corporate_action_validation.json` | `f905f381918b...` | N/A |
| `model_walk_forward` | Model Walk-Forward Validation | `BLOCKED` | `docs/REAL_WALK_FORWARD_REPORT.md` | `6f630363b8ba...` | WALK_FORWARD_BLOCKED: Insufficient unique trading dates (2) for genuine multi-fold chronological walk-forward evaluation |
| `calibration` | Probability Calibration | `BLOCKED` | `data/processed/model_validation/calibration.json` | `05716a17b4a8...` | CALIBRATION_BLOCKED: Insufficient out-of-sample observations from walk-forward folds for probability calibration |
| `conformal_validation` | Conformal Validation | `BLOCKED` | `data/processed/model_validation/conformal.json` | `b36d7db6153e...` | CONFORMAL_BLOCKED: Insufficient out-of-sample observations from walk-forward folds for conformal validation |
| `economic_validation` | Economic Validation | `BLOCKED` | `data/processed/model_validation/economic_validation.json` | `afc5815af47e...` | ECONOMIC_VALIDATION_BLOCKED: Insufficient out-of-sample predictions from walk-forward folds for economic paper-execution validation |
| `drift` | Model Drift (Pre-Deployment Historical) | `PASS` | `data/processed/model_validation/historical_drift.json` | `3aedbb3b845c...` | N/A |
| `adversarial_validation` | Adversarial Validation | `PASS` | `src/nse_signal/research/adversarial.py` | `97efe84db0d5...` | N/A |
| `multiple_testing_controls` | Multiple-Testing Controls | `PASS` | `src/nse_signal/research/falsification.py` | `b639256cfe2b...` | N/A |
| `untouched_holdout` | Untouched Holdout | `PASS` | `data/processed/nse_pit/pit_features.csv` | `03f26d04d5cc...` | N/A |
| `forensic_tests` | Forensic Tests | `PASS` | `data/processed/forensics/MUTATION_TEST_RESULTS.json` | `6929733dff3a...` | N/A |
| `clean_room_rebuild` | Clean-Room Rebuild | `PASS` | `docs/CLEAN_ROOM_VALIDATION_REPORT.md` | `de9597682279...` | N/A |
| `android_build` | Android Build | `PASS` | `android/app/build/outputs/apk/debug/app-debug.apk` | `18404fb252a7...` | N/A |
| `android_runtime` | Android Runtime E2E | `NOT_EXECUTED` | `docs/ANDROID_RUNTIME_VALIDATION.md` | `02f21c5daf0a...` | Headless agent environment lacks active AVD or physical device |
| `signal_only_safety` | Signal-Only Safety (REAL_TRADING=FALSE) | `PASS` | `reports/final_completion/trading_safety.json` | `7ddbd8b4477b...` | N/A |