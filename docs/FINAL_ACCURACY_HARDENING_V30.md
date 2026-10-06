# V30 Accuracy Hardening Audit — 2026-10-03

## Scope

V30 is based on the uploaded `NSE_Signal_Provider_Accuracy_Hardened_V29_INDIA_WIDE_FINAL(2)` package. The audit covered the source tree, configuration, production model lifecycle, PIT construction, labels, walk-forward validation, panel validation, conformal uncertainty, signal publication, restrictions, NSE report integration, and the complete test inventory.

## External research cross-check

The implementation was checked against current official NSE material for:

- equity market session timing and pre-open/closing sessions;
- CM-UDiFF/final bhavcopy and listed-security master reports;
- full bhavcopy/security deliverable data;
- surveillance indicators;
- price-band lists and circuit-breaker information;
- security-category impact cost;
- India VIX historical data;
- corporate-action/corporate-filings data;
- official F&O/equity report families.

SEBI's current short-selling framework was also checked. The signal engine remains signal-only and does not execute short sales or orders.

## V30 changes

### 1. Production calibration boundary purge

The previous production artifact builder separated training and calibration by timestamp but did not remove the final event-horizon observations before the calibration block. Because labels consume future OHLC observations, those training labels could overlap the calibration period.

V30 now purges the training/calibration boundary by at least `horizon + 1` bars.

### 2. Two-stage calibration boundary purge

The probability-calibration and conformal-calibration blocks are now separated by the same event-horizon purge. This prevents calibration observations from using future information from the conformal block.

### 3. Panel calibration leakage correction

The pooled panel walk-forward path now applies both temporal purges:

- model-training -> probability calibration;
- probability calibration -> conformal calibration.

The panel split remains timestamp-grouped, so all securities at a timestamp remain in the same temporal fold.

### 4. Proper class-conditional conformal prediction

The previous production conformal implementation reduced the prediction set to a single global nonconformity quantile. V30 uses finite-sample class-conditional conformal p-values:

`p_c = (1 + count(score_cal,c >= score_test,c)) / (n_c + 1)`

A class is retained only when its conformal p-value exceeds alpha. The signal publisher abstains unless exactly one class is retained.

Legacy artifacts without V30 conformal calibration data fail closed.

### 5. Frozen validation-only publication threshold

The production artifact now stores a publication threshold selected from the untouched validation/conformal block. Live publication no longer silently defaults to 0.55 when a validated threshold exists.

### 6. Live model uncertainty is enforced

The production predictor now exposes model dispersion. The signal publication path passes that dispersion into the publication gate instead of discarding it.

### 7. Causal factor support strengthened

For panel inputs, production factor support preferentially uses causal cross-sectional return/liquidity ranks. For single-symbol inputs it uses causal trailing momentum percentiles. A neutral hard-coded factor score is no longer an allowed production fallback.

### 8. Market-data age/session validation

Production publication derives signal age from the actual PIT `signal_time` and the decision timestamp. Backdated decisions, invalid sessions, and stale observations are blocked before signal publication.

### 9. Signal-only boundary retained

No broker order endpoint, broker credential path, or real-trading implementation was added. `REAL_TRADING=false` remains mandatory.

## Validation

The repository contains 112 collected tests. All test modules pass when run independently. The all-at-once pytest invocation exceeded the execution harness timeout even though the individual modules completed successfully; no failing test was observed.

A separate synthetic production-artifact smoke test successfully created a V30 artifact and generated a prediction with:

- conformal version 2;
- frozen publication threshold;
- model-dispersion output;
- conformal abstention behavior.

Synthetic data is used only for software/invariant testing and is not evidence of NSE predictive accuracy.

## Production readiness

Production remains deliberately blocked until the configured authoritative PIT datasets are actually supplied/licensed and validated. Current NSE report pages demonstrate that the relevant official report families exist, but a URL is not equivalent to possession, completeness, PIT availability, or redistribution rights.

This release therefore does **not** claim a guaranteed win rate, accuracy percentage, profitability, or superiority over other signal systems.
