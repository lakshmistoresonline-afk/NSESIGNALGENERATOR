# PIT Validation Report

- **Validation Timestamp**: 2026-10-06T06:22:45.156413+00:00
- **Validation Status**: PIT_VALIDATION_PARTIAL
- **Production Gate**: BLOCKED
- **Checks Passed**: 26
- **Checks Failed**: 2

## Validation Registry (CHK_01 through CHK_30)

- **[CHK_01] Raw Manifest Integrity**: `PASS`
  - Records Examined: `4`
  - Failures: `0`
  - Evidence: `Loaded 4 raw manifest entries.`
  - Computed Values: `{"raw_entries": 4}`
  - Source Artifacts: `['data\\reference\\raw_manifest.json']`

- **[CHK_02] PIT Manifest Integrity**: `PASS`
  - Records Examined: `1`
  - Failures: `0`
  - Evidence: `PIT manifest loaded.`
  - Computed Values: `{"datasets_processed": 4}`
  - Source Artifacts: `['data\\processed\\pit\\pit_manifest.json']`

- **[CHK_03] PriceBar Physical File Existence**: `PASS`
  - Records Examined: `5847`
  - Failures: `0`
  - Evidence: `Physically loaded 5847 price bars.`
  - Computed Values: `{"record_count": 5847}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl']`

- **[CHK_04] InstrumentPIT Physical File Existence**: `PASS`
  - Records Examined: `28464`
  - Failures: `0`
  - Evidence: `Physically loaded 28464 intervals.`
  - Computed Values: `{"record_count": 28464}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_05] PriceBar Schema**: `PASS`
  - Records Examined: `5847`
  - Failures: `0`
  - Evidence: `Missing fields: []`
  - Computed Values: `{"missing": []}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl']`

- **[CHK_06] InstrumentPIT Schema**: `PASS`
  - Records Examined: `28464`
  - Failures: `0`
  - Evidence: `Missing fields: []`
  - Computed Values: `{"missing": []}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_07] PriceBar OHLC Validity**: `PASS`
  - Records Examined: `5847`
  - Failures: `0`
  - Evidence: `Inverted or non-positive OHLC count: 0`
  - Computed Values: `{"failures": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl']`

- **[CHK_08] PriceBar Volume Validity**: `FAIL`
  - Records Examined: `5847`
  - Failures: `1`
  - Evidence: `Negative volume count: 1`
  - Computed Values: `{"failures": 1}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl']`

- **[CHK_09] Instrument Identity Validity**: `PASS`
  - Records Examined: `28464`
  - Failures: `0`
  - Evidence: `Unknown symbol count: 0`
  - Computed Values: `{"failures": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_10] Instrument PK Uniqueness**: `FAIL`
  - Records Examined: `28464`
  - Failures: `10853`
  - Evidence: `Duplicate instruments per effective_from: 10853`
  - Computed Values: `{"failures": 10853}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_11] Effective Interval Validity**: `PASS`
  - Records Examined: `28464`
  - Failures: `0`
  - Evidence: `Invalid intervals: 0`
  - Computed Values: `{"failures": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_12] Effective Interval Overlap**: `PASS`
  - Records Examined: `28464`
  - Failures: `0`
  - Evidence: `Overlapping intervals: 0`
  - Computed Values: `{"failures": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_13] Future Event-Date Leakage**: `PASS`
  - Records Examined: `5847`
  - Failures: `0`
  - Evidence: `Future leak count: 0`
  - Computed Values: `{"failures": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl']`

- **[CHK_14] Publication/Effective-Time Consistency**: `PASS`
  - Records Examined: `5847`
  - Failures: `0`
  - Evidence: `Publication time anomalies: 0`
  - Computed Values: `{"failures": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl']`

- **[CHK_15] Source Hash Existence in Manifest**: `PASS`
  - Records Examined: `34311`
  - Failures: `0`
  - Evidence: `Orphan hashes: 0`
  - Computed Values: `{"failures": 0}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl', 'data\\processed\\pit\\canonical_instruments.jsonl', 'data\\reference\\raw_manifest.json']`

- **[CHK_16] Source-to-Normalized Reconciliation**: `PASS`
  - Records Examined: `4`
  - Failures: `0`
  - Evidence: `Source parse failures: 0`
  - Computed Values: `{"failures": 0}`
  - Source Artifacts: `['data\\reference\\raw_manifest.json']`

- **[CHK_17] Exact Row Reconciliation**: `PASS`
  - Records Examined: `62774`
  - Failures: `0`
  - Evidence: `Ledger reconciliation discrepancies: 0`
  - Computed Values: `{"failures": 0}`
  - Source Artifacts: `['data\\processed\\pit\\row_transformation_ledger.jsonl']`

- **[CHK_18] Rejected-Row Accounting**: `PASS`
  - Records Examined: `5847`
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
  - Records Examined: `2`
  - Failures: `1`
  - Evidence: `Trading dates covered: 2 (Required >= 30)`
  - Computed Values: `{"unique_dates": 2}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl']`

- **[CHK_21] Trading-Calendar Validity**: `PASS`
  - Records Examined: `2`
  - Failures: `0`
  - Evidence: `Trading calendar enforced.`
  - Computed Values: `{"valid": true}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl']`

- **[CHK_22] Cross-Dataset Symbol Consistency**: `PASS`
  - Records Examined: `5847`
  - Failures: `0`
  - Evidence: `Symbols align across datasets.`
  - Computed Values: `{"aligned": true}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl', 'data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_23] Cross-Dataset Date Consistency**: `PASS`
  - Records Examined: `5847`
  - Failures: `0`
  - Evidence: `Dates align across datasets.`
  - Computed Values: `{"aligned": true}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl', 'data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_24] Provenance Completeness**: `PASS`
  - Records Examined: `34311`
  - Failures: `0`
  - Evidence: `Provenance attached to all records.`
  - Computed Values: `{"complete": true}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl', 'data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_25] Missing/Unknown PIT State**: `PASS`
  - Records Examined: `34311`
  - Failures: `0`
  - Evidence: `PIT state fully tracked.`
  - Computed Values: `{"tracked": true}`
  - Source Artifacts: `['data\\processed\\pit\\canonical_price_bars.jsonl', 'data\\processed\\pit\\canonical_instruments.jsonl']`

- **[CHK_26] Historical Coverage Gate**: `PARTIAL`
  - Records Examined: `2`
  - Failures: `1`
  - Evidence: `Historical coverage partial (2 days).`
  - Computed Values: `{"unique_dates": 2}`
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
