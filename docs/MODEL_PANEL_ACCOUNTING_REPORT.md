# Model Panel Accounting Report (Prompt 43)

| stage | input_rows | output_rows | input_dates | output_dates | dropped_rows | drop_reasons |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `1_raw` | 979742 | 979742 | 2957 | 2957 | 0 | {} |
| `2_normalized` | 979742 | 979742 | 2957 | 2957 | 0 | {} |
| `3_security_identity` | 979742 | 979742 | 2957 | 2957 | 0 | {} |
| `4_pit_price_bars` | 979742 | 229163 | 2957 | 124 | 750579 | {"non_eq_series": 750579} |
| `5_universe` | 229163 | 229163 | 124 | 124 | 0 | {} |
| `6_features` | 229163 | 1200 | 124 | 124 | 227963 | {"warmup_window_nan": 227963} |
| `7_labels` | 1200 | 1200 | 124 | 124 | 0 | {} |
| `8_model_panel` | 1200 | 1200 | 124 | 124 | 0 | {} |
| `9_walk_forward_input` | 1200 | 1200 | 124 | 124 | 0 | {} |