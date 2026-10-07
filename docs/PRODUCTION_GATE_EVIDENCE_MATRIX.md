# Production Gate Evidence Matrix (Self-Contained Manifest Verified)

- **Evaluated At**: 2026-10-07T04:54:28.691189+00:00
- **Overall Status**: `BLOCKED`
- **Eligible**: `False`

| Category ID | Name | Status | Evidence Path | Evidence Hash (SHA256) | Failure Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `historical_coverage` | Historical Data Coverage | `PASS` | `data/reference/historical_data_coverage.json` | `b5de3e070f29...` | N/A |
| `raw_integrity` | Raw-File Integrity | `PASS` | `data/reference/raw_manifest.json` | `c5dc31fc9f2d...` | N/A |
| `security_identity` | Historical Security Identity | `PASS` | `docs/HISTORICAL_IDENTITY_REPORT.md` | `1fc210d0334a...` | N/A |
| `pit_universe` | Point-in-Time Universe | `PASS` | `data/reference/nifty200_membership.csv` | `f45b9f93c51d...` | N/A |
| `pit_temporal_integrity` | PIT Temporal Integrity | `PASS` | `data/processed/pit/temporal_validation.json` | `36dcb4ff4c53...` | N/A |
| `required_pit_layers` | Required PIT Layers | `BLOCKED` | `data/reference/feature_data_dependency_matrix.json` | `93064e79edb9...` | MISSING_REQUIRED_PIT_LAYERS: ['cash_daily', 'security_master'] |
| `corporate_action_correctness` | Corporate-Action Correctness | `PASS` | `data/processed/nse_pit/corporate_action_validation.json` | `c19982a25cc2...` | N/A |
| `model_walk_forward` | Model Walk-Forward Validation | `BLOCKED` | `docs/REAL_WALK_FORWARD_REPORT.md` | `1ecf572ee018...` | WALK_FORWARD_BLOCKED: Insufficient unique trading dates (2) for multi-fold chronological walk-forward evaluation |
| `calibration` | Probability Calibration | `BLOCKED` | `data/processed/model_validation/real_walk_forward_results.json` | `5ba08b952ad4...` | INSUFFICIENT_CALIBRATION_DATA |
| `conformal_validation` | Conformal Validation | `BLOCKED` | `data/processed/model_validation/real_walk_forward_results.json` | `5ba08b952ad4...` | INSUFFICIENT_CONFORMAL_DATA |
| `economic_validation` | Economic Validation | `NOT_APPLICABLE` | `docs/REAL_WALK_FORWARD_REPORT.md` | `1ecf572ee018...` | Economic validation optional until live trading simulation |
| `drift` | Model Drift | `NOT_APPLICABLE` | `data/processed/model_validation/real_walk_forward_results.json` | `5ba08b952ad4...` | Drift monitoring active post-deployment |
| `adversarial_validation` | Adversarial Validation | `PASS` | `src/nse_signal/research/adversarial.py` | `97efe84db0d5...` | N/A |
| `multiple_testing_controls` | Multiple-Testing Controls | `PASS` | `src/nse_signal/research/falsification.py` | `b639256cfe2b...` | N/A |
| `untouched_holdout` | Untouched Holdout | `PASS` | `data/processed/nse_pit/pit_features.csv` | `03f26d04d5cc...` | N/A |
| `forensic_tests` | Forensic Tests | `PASS` | `data/processed/forensics/MUTATION_TEST_RESULTS.json` | `6929733dff3a...` | N/A |
| `clean_room_rebuild` | Clean-Room Rebuild | `PASS` | `docs/CLEAN_ROOM_VALIDATION_REPORT.md` | `50d1be3d489c...` | N/A |
| `android_build` | Android Build | `PASS` | `android/app/build/outputs/apk/debug/app-debug.apk` | `18404fb252a7...` | N/A |
| `android_runtime` | Android Runtime E2E | `NOT_EXECUTED` | `docs/ANDROID_RUNTIME_VALIDATION.md` | `02f21c5daf0a...` | Headless agent environment lacks active AVD or physical device |
| `signal_only_safety` | Signal-Only Safety (REAL_TRADING=FALSE) | `PASS` | `reports/final_completion/trading_safety.json` | `7ddbd8b4477b...` | N/A |