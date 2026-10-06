# Final Accuracy / PIT Integrity Audit — V13

## Purpose
V13 is a correctness-focused release over V12. It fixes data-layer defects that can materially change historical signal validity and adds missing NSE-context features without inventing unavailable data.

## Findings fixed
1. Daily NSE ingestion previously overwrote prior normalized days; V13 appends and deduplicates by natural keys.
2. PIT secondary layers could contain duplicate symbol/date rows; V13 keeps the latest available observation before joins.
3. Cross-sectional transforms did not explicitly enforce information availability for every peer; V13 rejects unavailable rows and only ranks released observations.
4. Corporate-action adjustment factors were absent; V13 requires authoritative price/volume factors and never infers them from price jumps.
5. Daily derivatives rows were parsed but not converted into model context; V13 adds nearest-expiry PCR, OI/OI-change, IV and ATM OI concentration context when those fields exist.
6. Surveillance, price-band and short-sale restrictions were not publication gates; V13 fails closed for restricted or near-limit names and blocked shorts.
7. Model governance now supports mandatory adversarial validation, block-bootstrap evidence and calibration ECE checks.
8. PIT membership can no longer silently pass as an empty file in production/backtest mode.

## Research basis
Financial ML remains vulnerable to incomplete-cross-section leakage, temporal leakage, selection bias, non-IID validation and economic-cost overstatement. V13 therefore treats information availability as a row-level property, not only a dataset-level timestamp.

A recent 2026 paper specifically identifies incomplete-cross-section leakage when peer-group statistics are formed before all firms' information is available. This is addressed here by release-time-aware cross-sectional transforms.

## NSE layers
The project is designed around official NSE report families: CM UDiFF, F&O UDiFF, security master, delivery, impact cost, surveillance, price-band/security lists, short-selling, breadth, historical indices/India VIX and derivatives participant reports. Actual historical files must be acquired from their authoritative source; the package never fabricates them.

## Non-negotiable controls
- REAL_TRADING=false
- signal_only=true
- no broker execution
- no historical universe inference
- no date-only corporate event timestamps
- no date-only fundamentals
- no same-timestamp unavailable peer information
- no automatic corporate-action inference
- no test-set threshold tuning
- fail-closed publication

## Validation
The V13 test suite must pass before packaging. Synthetic metrics are diagnostic only and are not market-alpha evidence.
