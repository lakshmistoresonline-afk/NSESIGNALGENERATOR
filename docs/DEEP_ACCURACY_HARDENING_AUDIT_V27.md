# V27 Deep Accuracy Hardening Audit

## Scope
Source-level audit of the uploaded V26 package, focused on Indian NSE equity signal
quality, causal correctness, point-in-time integrity, validation, and publication safety.

## Release-blocking findings fixed

### 1. Market regime rolling-window duplication
A panel contains one row per security per timestamp. The previous regime implementation
mapped one market value to every security and then applied rolling windows over rows.
A 200-row SMA therefore represented roughly 50-100 market sessions depending on panel
size. V27 computes market statistics once per unique timestamp and broadcasts them back.

### 2. Broad India universe
NIFTY 200 is a benchmark universe, not an all-NSE equity universe. V27 adds a broad
NSE equity universe contract based on historical security-master identity/series and
trailing, as-of liquidity/history filters. It excludes non-EQ series by default.

### 3. Timeout-label selection bias
The former production target excluded every triple-barrier timeout. This can condition
the training sample on unusually large future moves that hit a barrier. V27 supports
a directional timeout policy for production/OOS research: a timeout is labelled by the
realized next-open-to-horizon return. The legacy `exclude` mode remains available for
specialized barrier-only research.

### 4. Panel calibration
Panel walk-forward calibration is now chronological and split into calibration-fit and
later conformal-calibration observations. This prevents reuse of the same observations
for both probability mapping and conformal coverage.

### 5. Production conformal state
Production artifacts freeze a conformal nonconformity quantile. Live data is never used
to recalibrate the model.

### 6. Champion governance
A model cannot transition to `CHAMPION` unless its registry metrics contain a successful
full governance gate. This prevents manual promotion of an unvalidated artifact.

### 7. Secondary provider hierarchy
TejHQ and BharatStock are now included in the default secondary research fallback order,
while remaining explicitly secondary and never replacing authoritative PIT data.

### 8. Operational readiness
The dashboard now reports `blocked` when required PIT/provenance requirements are
missing instead of reporting a misleading `ok` status.

## Remaining production requirements

The software still deliberately refuses to imply that free/secondary data establishes
authoritative historical accuracy. Required licensed/official PIT datasets must be
acquired, normalized, hashed, and validated before production promotion.

At minimum this includes:
- historical NSE cash EOD data
- historical NSE F&O EOD data if derivatives features are enabled
- historical security/contract identity data
- benchmark/index history
- required official restriction/liquidity/PIT report layers
- a complete provenance/checksum manifest
- a frozen dataset snapshot
- out-of-sample governance evidence

## Accuracy principle

More indicators do not automatically mean more accurate signals. V27 therefore
prioritizes causal correctness, PIT integrity, economic execution realism, selective
abstention, regime conditioning, liquidity controls, and validation against unseen
historical periods.
