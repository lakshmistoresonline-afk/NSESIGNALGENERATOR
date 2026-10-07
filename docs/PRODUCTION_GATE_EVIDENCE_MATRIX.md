# Production Gate Evidence Matrix (Semantic PIT Layer Validator Verified)

- **Evaluated At**: 2026-10-07T12:35:13.720343+00:00
- **Overall Status**: `BLOCKED`
- **Eligible**: `False`

| Category ID | Name | Status | Evidence Path | Evidence Hash (SHA256) | Failure Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `historical_coverage` | Historical Data Coverage | `BLOCKED` | `data/processed/final_historical_coverage.json` | `be079168bdd2...` | LAYER_COVERAGE_INSUFFICIENT (corporate_actions): completeness ratio 0.0 < 0.50 |
| `raw_integrity` | Raw-File Integrity | `PASS` | `data/reference/raw_manifest.json` | `c5dc31fc9f2d...` | N/A |
| `security_identity` | Historical Security Identity | `PASS` | `data/processed/final_identity_validation.json` | `1e0fdcd6f331...` | N/A |
| `pit_universe` | Point-in-Time Universe | `PASS` | `data/reference/nifty200_membership.csv` | `f45b9f93c51d...` | N/A |
| `pit_temporal_integrity` | PIT Temporal Integrity | `PASS` | `data/processed/final_pit_temporal_validation.json` | `1f82fa315961...` | N/A |
| `required_pit_layers` | Required PIT Layers | `BLOCKED` | `data/processed/pit/canonical_price_bars.jsonl` | `MISSING_FILE...` | MISSING_OR_INVALID_EVIDENCE_FILE: data/processed/pit/canonical_price_bars.jsonl (MISSING_FILE) |
| `corporate_action_correctness` | Corporate-Action Correctness | `PASS` | `data/processed/nse_pit/corporate_action_validation.json` | `c3c05e7673a8...` | N/A |
| `model_walk_forward` | Model Walk-Forward Validation | `BLOCKED` | `docs/REAL_WALK_FORWARD_REPORT.md` | `6f630363b8ba...` | WALK_FORWARD_BLOCKED: Insufficient unique trading dates (2) for genuine multi-fold chronological walk-forward evaluation |
| `calibration` | Probability Calibration | `BLOCKED` | `data/processed/model_validation/calibration.json` | `7fe78b3e926b...` | CALIBRATION_BLOCKED: Insufficient out-of-sample observations from walk-forward folds for probability calibration |
| `conformal_validation` | Conformal Validation | `BLOCKED` | `data/processed/model_validation/conformal.json` | `9e948cd98b08...` | CONFORMAL_BLOCKED: Insufficient out-of-sample observations from walk-forward folds for conformal validation |
| `economic_validation` | Economic Validation | `NOT_APPLICABLE` | `docs/REAL_WALK_FORWARD_REPORT.md` | `6f630363b8ba...` | Economic validation optional until live trading simulation |
| `drift` | Model Drift | `NOT_APPLICABLE` | `data/processed/model_validation/real_walk_forward_results.json` | `6c1db4d6f0d1...` | Drift monitoring active post-deployment |
| `adversarial_validation` | Adversarial Validation | `PASS` | `src/nse_signal/research/adversarial.py` | `97efe84db0d5...` | N/A |
| `multiple_testing_controls` | Multiple-Testing Controls | `PASS` | `src/nse_signal/research/falsification.py` | `b639256cfe2b...` | N/A |
| `untouched_holdout` | Untouched Holdout | `PASS` | `data/processed/nse_pit/pit_features.csv` | `03f26d04d5cc...` | N/A |
| `forensic_tests` | Forensic Tests | `PASS` | `data/processed/forensics/MUTATION_TEST_RESULTS.json` | `6929733dff3a...` | N/A |
| `clean_room_rebuild` | Clean-Room Rebuild | `PASS` | `docs/CLEAN_ROOM_VALIDATION_REPORT.md` | `de9597682279...` | N/A |
| `android_build` | Android Build | `PASS` | `android/app/build/outputs/apk/debug/app-debug.apk` | `18404fb252a7...` | N/A |
| `android_runtime` | Android Runtime E2E | `NOT_EXECUTED` | `docs/ANDROID_RUNTIME_VALIDATION.md` | `02f21c5daf0a...` | Headless agent environment lacks active AVD or physical device |
| `signal_only_safety` | Signal-Only Safety (REAL_TRADING=FALSE) | `PASS` | `reports/final_completion/trading_safety.json` | `7ddbd8b4477b...` | N/A |