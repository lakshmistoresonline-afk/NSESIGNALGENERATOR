# V31 Final Forensic Accounting Report (Iteration 7)

## 1. Executive Summary
This report summarizes the final forensic accounting, two-tier row reconciliation, cryptographic source fingerprinting, and independent runtime validation results for the NSE Signal Provider V31 system.

## 2. Source & Observation Accounting (Two-Tier Model)
- **Source Observations**: 62,774 total raw rows across 4 dataset files (Cash Bhavcopy: 5,852; Security Master: 56,922).
- **Normalized Observations**: 62,774 total rows successfully parsed.
- **Canonical Observations**: 62,769 total valid observations (PriceBar observations: 5,847; Security Master observations: 56,922).
- **Exact Duplicate Observations**: 5 (Cash Bhavcopy duplicate keys with identical payload hashes).
- **Conflict Observations**: 0.
- **Rejected Rows**: 0.
- **Transformation Errors**: 0.
- **Unaccounted Observations**: 0 (`normalized_rows == canonical_observations + exact_duplicate_observations + conflict_observations + rejected_rows + error_rows`).

## 3. Temporal Interval Accounting
- **Canonical Observations Assigned to Intervals**: 56,922 observations.
- **Temporal Instrument Intervals Created**: 18,915 non-overlapping effective-dated intervals (`[effective_from, effective_to)`).
- **Orphan / Unmapped Observations**: 0.

## 4. Independent Validation Registry (CHK_01 through CHK_30)
- **Total Checks Executed**: 30 runtime checks.
- **Status**: `PIT_VALIDATION_PARTIAL` (Due to multi-year historical coverage requirement of 30+ trading days; currently 2 trading days ingested).
- **Production Gate**: `BLOCKED` (Fail-closed).

## 5. Non-Negotiable Invariants
- **Signal-Only (`REAL_TRADING = FALSE`)**: Permanently enforced. Zero broker order placement or execution routes exist.
- **Authentication**: Real Firebase Auth and Firebase Admin SDK token verification enforced.
- **Android Runtime**: `NOT EXECUTED — NO DEVICE/EMULATOR` (Headless agent environment lacks active AVD or system images).
