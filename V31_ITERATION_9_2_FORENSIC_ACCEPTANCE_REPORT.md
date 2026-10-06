# V31 Iteration 9.2 Forensic Acceptance Report

## 1. Executed Commands
- `python -m pytest`
- `python -m nse_signal.cli --ingest --start-date 2025-01-02 --end-date 2025-01-03`
- `python -m nse_signal.cli --audit`
- `python -m nse_signal.cli --build-pit`
- `python -m nse_signal.cli --validate-pit`
- `python -m nse_signal.data.pit_forensic_validator`

## 2. Raw Evidence
- **Source Observations**: 62,774
- **Normalized Observations**: 62,774

## 3. Five Conflict Cases
- Recorded in `FORENSIC_DISCREPANCY_CASES.json` (5 Cash Bhavcopy payload conflicts).

## 4. Builder vs Clean-Room Reconciliation
- Reconciled successfully via `FORENSIC_SOURCE_RECONCILIATION.json`.

## 5. Canonical Artifact Reconciliation
- Match confirmed across PriceBars (5,847) and Instrument observations (56,922).

## 6. Interval Reconstruction
- Temporal intervals created: 28,464 (`FORENSIC_INTERVAL_ACCOUNTING.json`).

## 7. Mutation M01-M28 Results
- All 28 mutations executed and detected successfully (`MUTATION_TEST_RESULTS.json`).

## 8. Test-of-Test
- Verified successfully (`FORENSIC_TEST_OF_TESTS.md`).

## 9. Determinism
- Two clean-room rebuild runs match identically (`DETERMINISM_REPORT.md`).

## 10. AST Audit
- Independence audit passed (`AST_VALIDATION_AUDIT.md`).

## 11. Pytest
- `131 passed, 0 failed`.

## 12. Full Pipeline
- Exit code `0`.

## 13. Production Gate
- **Status**: `BLOCKED` (Fail-closed due to insufficient historical coverage of only 2 trading dates).

## 14. Android Runtime Status
- **Status**: `NOT EXECUTED — NO DEVICE/EMULATOR`.

## 15. Remaining Blockers
- Authoritative multi-year historical depth pending.

## 16. Final Acceptance Decision
- **Status**: `ACCEPTED FOR FORENSIC RIGOR (PRODUCTION GATE BLOCKED)`.
