# PIT Validation Report

- **Validation Timestamp**: 2026-10-10T12:52:12.928406+00:00
- **Validation Status**: PIT_VALIDATION_PARTIAL
- **Production Gate**: BLOCKED
- **Checks Passed**: 27
- **Checks Failed**: 1

## Validation Registry (CHK_01 through CHK_30)

- **[CHK_01] Raw Manifest Integrity**: `PASS`
  - Records Examined: `345`
  - Failures: `0`
  - Evidence: `Loaded 345 raw manifest entries.`
  - Computed Values: `{"raw_entries": 345}`
  - Source Artifacts: `['data\\reference\\raw_manifest.json']`

- **[CHK_02] PIT Manifest Integrity**: `PASS`
  - Records Examined: `1`
  - Failures: `0`
  - Evidence: `PIT manifest loaded.`
  - Computed Values: `{"datasets_processed": 345}`
  - Source Artifacts: `['data\\processed\\pit\\pit_manifest.json']`

- **[CHK_03] PriceBar Physical File Existence**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Physically loaded 0 price bars.`
  - Computed Values: `{"record_count": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl']`

- **[CHK_04] InstrumentPIT Physical File Existence**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Physically loaded 0 intervals.`
  - Computed Values: `{"record_count": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_05] PriceBar Schema**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Missing fields: []`
  - Computed Values: `{"missing": []}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl']`

- **[CHK_06] InstrumentPIT Schema**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Missing fields: []`
  - Computed Values: `{"missing": []}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_07] PriceBar OHLC Validity**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Inverted or non-positive OHLC count: 0`
  - Computed Values: `{"failures": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl']`

- **[CHK_08] PriceBar Volume Validity**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Negative volume count: 0`
  - Computed Values: `{"failures": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl']`

- **[CHK_09] Instrument Identity Validity**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Unknown symbol count: 0`
  - Computed Values: `{"failures": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_10] Instrument PK Uniqueness**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Duplicate instruments per effective_from: 0`
  - Computed Values: `{"failures": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_11] Effective Interval Validity**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Invalid intervals: 0`
  - Computed Values: `{"failures": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_12] Effective Interval Overlap**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Overlapping intervals: 0`
  - Computed Values: `{"failures": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_13] Future Event-Date Leakage**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Future leak count: 0`
  - Computed Values: `{"failures": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl']`

- **[CHK_14] Publication/Effective-Time Consistency**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Publication time anomalies: 0`
  - Computed Values: `{"failures": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl']`

- **[CHK_15] Source Hash Existence in Manifest**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Orphan hashes: 0`
  - Computed Values: `{"failures": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl', 'data\\processed\\pit\\canonical_instruments.jsonl', 'data\\reference\\raw_manifest.json']`

- **[CHK_16] Source-to-Normalized Reconciliation**: `FAIL`
  - Records Examined: `345`
  - Failures: `345`
  - Evidence: `Source parse failures: 345`
  - Computed Values: `{"failures": 345}`
  - Source Artifacts: `['data\\reference\\raw_manifest.json']`

- **[CHK_17] Exact Row Reconciliation**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Ledger reconciliation discrepancies: 0`
  - Computed Values: `{"failures": 0}`
  - Source Artifacts: `['data\\processed\\pit\\row_transformation_ledger.jsonl']`

- **[CHK_18] Rejected-Row Accounting**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Rejected rows accounted: 0`
  - Computed Values: `{"rejected_rows": 0}`
  - Source Artifacts: `['data\\processed\\pit\\pit_manifest.json']`

- **[CHK_19] Error-Row Accounting**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Transformation errors logged: 0`
  - Computed Values: `{"error_rows": 0}`
  - Source Artifacts: `['data\\processed\\pit\\transformation_errors.json']`

- **[CHK_20] Dataset/Date Completeness**: `PARTIAL`
  - Records Examined: `0`
  - Failures: `1`
  - Evidence: `Trading dates covered: 0 (Required >= 30)`
  - Computed Values: `{"unique_dates": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl']`

- **[CHK_21] Trading-Calendar Validity**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Trading calendar enforced.`
  - Computed Values: `{"valid": true}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl']`

- **[CHK_22] Cross-Dataset Symbol Consistency**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Symbols align across datasets.`
  - Computed Values: `{"aligned": true}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl', 'data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_23] Cross-Dataset Date Consistency**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Dates align across datasets.`
  - Computed Values: `{"aligned": true}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl', 'data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_24] Provenance Completeness**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Provenance attached to all records.`
  - Computed Values: `{"complete": true}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl', 'data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_25] Missing/Unknown PIT State**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `PIT state fully tracked.`
  - Computed Values: `{"tracked": true}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl', 'data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_26] Historical Coverage Gate**: `PARTIAL`
  - Records Examined: `0`
  - Failures: `1`
  - Evidence: `Historical coverage partial (0 days).`
  - Computed Values: `{"unique_dates": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl']`

- **[CHK_27] Required Dataset Gate**: `PASS`
  - Records Examined: `2`
  - Failures: `0`
  - Evidence: `Required datasets present.`
  - Computed Values: `{"present": true}`
  - Source Artifacts: `['data\\reference\\raw_manifest.json']`

- **[CHK_28] Transformation-Error Gate**: `PASS`
  - Records Examined: `0`
  - Failures: `0`
  - Evidence: `Error gate status: PASS`
  - Computed Values: `{"error_count": 0}`
  - Source Artifacts: `['data\\processed\\pit\\transformation_errors.json']`

- **[CHK_29] Report/State Consistency**: `PASS`
  - Records Examined: `1`
  - Failures: `0`
  - Evidence: `Reports synchronized with state.`
  - Computed Values: `{"consistent": true}`
  - Source Artifacts: `['data\\processed\\pit\\pit_validation_state.json']`

- **[CHK_30] Production Gate**: `PASS`
  - Records Examined: `1`
  - Failures: `0`
  - Evidence: `Production gate decision evaluated correctly: BLOCKED`
  - Computed Values: `{"production_gate": "BLOCKED"}`
  - Source Artifacts: `['data\\processed\\pit\\pit_manifest.json']`
