# Raw-Data-to-Model-Panel Reconciliation Report

| stage | unique_dates | rows | symbols | dropped_rows | reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `1_raw_nse_files` | 2794 | Unknown (archive files) | Unknown | 0 | Raw archive files present on disk |
| `2_normalization_manifest` | 0 | 0 | Variable per archive | 0 | Successfully ingested raw archives in manifest |
| `3_canonical_price_bars` | 2 | 5847 | 3027 | 0 | Canonical price observations extracted from archives |
| `4_pit_security_identity` | 2 | 5847 | 3027 | 0 | Effective-dated temporal identity model applied |
| `5_pit_price_bars_store` | 0 | 0 | 0 | 5847 | Filtered or aggregated into PIT store |
| `6_universe_selection_eq` | 0 | 0 | 0 | 0 | Filtered for series == 'EQ' |
| `7_feature_generation` | 2 | 5847 | 3027 | 0 | Warm-up window for lagging technical indicators (e.g. 200 EMA) |
| `8_labels_and_model_panel` | 2 | 5847 | 3027 | 0 | Execution-consistent target labels attached |
| `9_walk_forward_input` | 2 | 5847 | 3027 | 0 | Chronological fold partitioning |