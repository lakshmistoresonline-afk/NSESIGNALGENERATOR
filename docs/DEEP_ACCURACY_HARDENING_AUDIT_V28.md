# V28 India-Wide Accuracy Hardening Audit

## Release intent
V28 is a signal-only NSE research/publication package. It does not place, modify, or cancel broker orders and `REAL_TRADING` remains false.

## Critical findings fixed
1. `make_labels()` and the directional benchmark label could shift across securities in a panel. Labels are now grouped by symbol.
2. Generic CPCV is row-index based and is unsafe when applied directly to a panel. A timestamp-grouped panel CPCV splitter was added.
3. Same-timestamp cross-sectional market residualization is not a valid beta regression when the benchmark return is identical across rows. V28 adds trailing per-symbol beta/residual features.
4. Broad-universe selection could retain a security whose last observation was far older than the requested date. A configurable staleness gate was added.
5. Effective-dated membership could contain overlapping intervals. Membership validation now rejects overlaps and source timestamps that occur after effective membership.
6. Corporate adjustment factors were present as a module but were not integrated into PIT dataset construction. The PIT build now consumes authoritative adjustment factors when present and production configuration requires the adjustment layer.
7. Corporate event availability is elevated to a production requirement because event blackout logic cannot be relied on when the event feed is absent.

## New causal features
- market breadth up/down share
- market return dispersion
- high-volatility cross-section share
- trailing 60-session benchmark beta
- benchmark residual return
- trailing relative strength
- sector-relative trailing strength

These are used only when the required source fields exist and are calculated without future observations.

## Validation
- 105 tests passed.
- Python compilation and ZIP integrity must be rechecked on packaging.
- Existing pandas fragmentation warnings are performance warnings in the legacy indicator builder, not evidence of look-ahead bias. They remain visible rather than being suppressed.

## Production limitation
The package deliberately does not claim that a model is the most accurate in India. Accuracy must be established on authoritative, point-in-time historical data with delisted securities, effective-dated universe membership, corporate adjustments/events, benchmark/index history, realistic costs, and an untouched chronological test period.
