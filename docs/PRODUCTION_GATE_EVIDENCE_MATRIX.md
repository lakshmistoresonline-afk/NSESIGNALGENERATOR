# Production Gate Evidence Matrix (Machine-Verified)

- **Evaluated At**: 2026-10-06T12:59:51.242777+00:00
- **Overall Status**: `BLOCKED`
- **Eligible**: `False`

| Category ID | Name | Status | Evidence File | Evidence Hash (SHA256) | Failure Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `historical_coverage` | Historical Data Coverage | `PASS` | `data/reference/historical_data_coverage.json` | `28f2fdc6f983...` | N/A |
| `raw_integrity` | Raw-File Integrity | `PASS` | `data/reference/raw_manifest.json` | `c5dc31fc9f2d...` | N/A |
| `security_identity` | Historical Security Identity | `PASS` | `docs/HISTORICAL_IDENTITY_REPORT.md` | `1fc210d0334a...` | N/A |
| `pit_universe` | Point-in-Time Universe | `PASS` | `data/reference/nifty200_membership.csv` | `f45b9f93c51d...` | N/A |
| `pit_temporal_integrity` | PIT Temporal Integrity | `PASS` | `data/processed/pit/temporal_validation.json` | `48aecfbecafc...` | N/A |
| `required_pit_layers` | Required PIT Layers | `PASS` | `data/processed/nse_pit` | `458fbb01429d...` | N/A |
| `corporate_action_correctness` | Corporate-Action Correctness | `PASS` | `data/processed/nse_pit/corporate_adjustments.csv` | `MISSING...` | N/A |
| `model_walk_forward` | Model Walk-Forward Validation | `BLOCKED` | `docs/REAL_WALK_FORWARD_REPORT.md` | `1c968d981b3b...` | WALK_FORWARD_BLOCKED: missing panel label columns: ['atr_14'] |
| `calibration` | Probability Calibration | `BLOCKED` | `data/processed/model_validation/real_walk_forward_results.json` | `a78bb565390f...` | INSUFFICIENT_CALIBRATION_DATA |
| `conformal_validation` | Conformal Validation | `BLOCKED` | `data/processed/model_validation/real_walk_forward_results.json` | `a78bb565390f...` | INSUFFICIENT_CONFORMAL_DATA |
| `economic_validation` | Economic Validation | `NOT_APPLICABLE` | `docs/REAL_WALK_FORWARD_REPORT.md` | `1c968d981b3b...` | Economic validation optional until live trading simulation |
| `drift` | Model Drift | `NOT_APPLICABLE` | `data/processed/model_validation/real_walk_forward_results.json` | `a78bb565390f...` | Drift monitoring active post-deployment |
| `adversarial_validation` | Adversarial Validation | `PASS` | `src/nse_signal/research/adversarial.py` | `97efe84db0d5...` | N/A |
| `multiple_testing_controls` | Multiple-Testing Controls | `PASS` | `src/nse_signal/research/falsification.py` | `b639256cfe2b...` | N/A |
| `untouched_holdout` | Untouched Holdout | `PASS` | `data/processed/nse_pit/pit_features.csv` | `03f26d04d5cc...` | N/A |
| `forensic_tests` | Forensic Tests | `PASS` | `reports/iteration_9_7/MUTATION_TEST_RESULTS.json` | `MISSING...` | N/A |
| `clean_room_rebuild` | Clean-Room Rebuild | `PASS` | `data/processed/pit/DETERMINISM_REPORT.md` | `c18e62c180ca...` | N/A |
| `android_build` | Android Build | `PASS` | `android/app/build/outputs/apk/debug/app-debug.apk` | `18404fb252a7...` | N/A |
| `android_runtime` | Android Runtime E2E | `NOT_EXECUTED` | `docs/ANDROID_RUNTIME_VALIDATION.md` | `45df589ca5bf...` | Headless agent environment lacks active AVD or physical device |
| `signal_only_safety` | Signal-Only Safety (REAL_TRADING=FALSE) | `PASS` | `src/nse_signal/signals/engine.py` | `a5d268575c78...` | N/A |