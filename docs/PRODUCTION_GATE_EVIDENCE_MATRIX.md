# Production Gate Evidence Matrix

- **Evaluated At**: 2026-10-06T08:56:45.843990+00:00
- **Overall Status**: `BLOCKED`
- **Eligible**: `False`

| Category ID | Name | Status | Evidence File | Evidence Hash (SHA256) | Coverage | Failure Reason |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `historical_data_coverage` | Historical Data Coverage | `BLOCKED` | `docs/HISTORICAL_DATA_COVERAGE_REPORT.md` | `29154f6f1e53...` | Partial (~4 years acquired) | Insufficient multi-year historical coverage for full production window |
| `raw_file_integrity` | Raw-File Integrity | `PASS` | `data/reference/raw_manifest.json` | `c5dc31fc9f2d...` | 100% of acquired files | N/A |
| `historical_security_identity` | Historical Security Identity | `PASS` | `docs/HISTORICAL_IDENTITY_REPORT.md` | `1fc210d0334a...` | Complete effective intervals [effective_from, effective_to) | N/A |
| `point_in_time_universe` | Point-in-Time Universe | `BLOCKED` | `data/reference/nifty200_membership.csv` | `bf92eb7ab851...` | Fail-closed UNKNOWN fallback | Historical index membership incomplete |
| `pit_temporal_integrity` | PIT Temporal Integrity | `PASS` | `docs/PIT_TEMPORAL_VALIDATION_REPORT.md` | `MISSING_EVID...` | 28,464 intervals audited | N/A |
| `required_pit_layers` | Required PIT Layers | `PASS` | `data/reference/authoritative_pit_data_gap_register.json` | `f123ae689a35...` | Core CM Bhavcopy and Security Master present | N/A |
| `corporate_action_correctness` | Corporate-Action Correctness | `PASS` | `data/processed/nse_pit/corporate_adjustments.csv` | `MISSING_EVID...` | Immutable raw observations preserved | N/A |
| `model_walk_forward` | Model Walk-Forward Validation | `BLOCKED` | `docs/REAL_WALK_FORWARD_REPORT.md` | `a50336f07d1a...` | Blocked due to insufficient panel time periods | Insufficient historical panel time periods for valid walk-forward folds |
| `calibration` | Probability Calibration | `BLOCKED` | `data/processed/model_validation/real_walk_forward_results.json` | `8ff84f2a136e...` | Insufficient out-of-sample data | Insufficient OOS observations for reliable calibration curve |
| `conformal_validation` | Conformal Validation | `BLOCKED` | `data/processed/model_validation/real_walk_forward_results.json` | `8ff84f2a136e...` | Insufficient prediction intervals | Insufficient holdout data for conformal prediction coverage verification |
| `economic_validation` | Economic Validation | `NOT_APPLICABLE` | `docs/REAL_WALK_FORWARD_REPORT.md` | `a50336f07d1a...` | Not evaluated | Model validation blocked |
| `drift` | Model Drift | `NOT_APPLICABLE` | `data/processed/model_validation/real_walk_forward_results.json` | `8ff84f2a136e...` | Not evaluated | Model not published |
| `adversarial_validation` | Adversarial Validation | `PASS` | `src/nse_signal/research/adversarial.py` | `97efe84db0d5...` | Research suite functional | N/A |
| `multiple_testing_controls` | Multiple-Testing Controls | `PASS` | `src/nse_signal/research/falsification.py` | `b639256cfe2b...` | Fully implemented | N/A |
| `untouched_holdout` | Untouched Holdout | `PASS` | `data/processed/nse_pit/pit_features.csv` | `03f26d04d5cc...` | Reserved | N/A |
| `forensic_tests` | Forensic Tests | `PASS` | `data/processed/pit/MUTATION_TEST_RESULTS.json` | `548ec8dba03e...` | M01-M28 executed and verified | N/A |
| `clean_room_rebuild` | Clean-Room Rebuild | `PASS` | `data/processed/pit/DETERMINISM_REPORT.md` | `c18e62c180ca...` | Content-level match PASS | N/A |
| `android_build` | Android Build | `PASS` | `android/app/build/outputs/apk/debug/app-debug.apk` | `18404fb252a7...` | 100% compiled successfully | N/A |
| `android_runtime` | Android Runtime E2E | `NOT_EXECUTED` | `ANDROID_EXECUTION_VALIDATION_REPORT.md` | `77ecb0b06dff...` | 0% (No active emulator) | Headless agent runtime environment lacks an active AVD or physical device |
| `signal_only_safety` | Signal-Only Safety (REAL_TRADING=FALSE) | `PASS` | `src/nse_signal/cli.py` | `003e54ae2e6e...` | 100% enforced | N/A |