# Final Accuracy Research — V8

## Purpose
V8 is a stricter signal-publication and research-integrity release. It does not claim a target live accuracy or profitability.

## Additions
1. Causal fractional-differentiation research features.
2. Volume-bar sampling utility for event/activity-time experiments.
3. Conservative square-root market-impact estimate.
4. Optional meta-label gate trained only from OOS primary predictions.
5. Signal-engine gates for meta probability and multi-horizon agreement.
6. Existing CPCV, PBO, DSR/selection controls, conformal abstention, economic threshold selection, point-in-time universe framework, drift tests, and execution-consistent triple-barrier labels retained.

## Research rationale
Financial ML is exposed to non-IID data, regime shifts, overlapping labels, multiple testing, survivorship bias, transaction costs, and data-availability leakage. Current research recommends purged/embargoed and combinatorial validation, explicit selection-bias controls, and pipeline-level leakage audits. CPCV has shown advantages over conventional validation in controlled studies.

## Data priority
The next live-data phase should add point-in-time NIFTY 200 membership, fundamentals and revisions, corporate events, options IV/skew/OI, futures basis/OI, breadth, delivery, liquidity/impact and timestamped news. NSE publishes historical price/volume, delivery, corporate-action and derivatives datasets that can support this when acquired under the applicable data terms.

## Publication rule
A signal should be published only when the primary probability, economic value, data freshness, uncertainty, optional meta-label probability, and multi-horizon agreement gates pass. Missing information must fail closed.

## No execution
`REAL_TRADING=false` remains mandatory. This package is a signal/research system only.
