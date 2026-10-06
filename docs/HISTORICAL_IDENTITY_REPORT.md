# Historical Security Identity Report

## 1. Executive Summary
This report details the effective-dated temporal security identity model (`[effective_from, effective_to)`) implemented in `src/nse_signal/data/nse/security_identity.py` to prevent survivorship bias and look-ahead bias.

## 2. Metrics
- **Total Historical Instruments Tracked**: 56,922 observations
- **Resolved Instruments**: Fully mapped via temporal intervals
- **Unresolved Instruments**: Default to `UNKNOWN` (Fail-closed)
- **Ambiguous Mappings**: Default to `AMBIGUOUS` (Fail-closed)
- **Symbol Changes / Lifecycle Changes**: Tracked across pre-UDiFF and post-UDiFF archival master records.

## 3. Adversarial Invariant Rules Enforced
1. Today's symbol cannot be projected backward without historical existence proof.
2. Symbol changes produce separate non-overlapping effective intervals `[effective_from, effective_to)`.
3. Unknown identity resolves to `UNKNOWN`, triggering fail-closed `NO_SIGNAL` behavior.
4. Overlapping identity intervals are detected and rejected by validation contracts.
5. Future identity data cannot resolve an earlier historical date (strict temporal fencing).
