# V21 Final Release Audit

## Scope
Signal-only NSE research/publication platform. `REAL_TRADING=false` and `SIGNAL_ONLY=true` are mandatory.

## Authoritative PIT data
Production authority is restricted to official NSE India / NSE Clearing / NSE Indices publications. The release includes an authoritative source catalog and deterministic acquisition pipeline for CM UDiFF, F&O UDiFF, security master and index history, plus contracts for delivery, impact cost, volatility, restrictions, participant OI, FII derivatives, India VIX, corporate actions and index history.

## Historical Nifty 200
The current official Nifty 200 CSV is explicitly treated as a current snapshot only. Historical backtests require dated official constituent intervals or licensed historical constituent data. The platform fails closed rather than backfilling today's constituents into the past.

## PIT integrity
- `market_time`, `asof_time`, and `signal_time` are distinct.
- Daily EOD rows are decision-eligible at the next verified trading-session open unless a true publication timestamp is supplied.
- Unknown calendar years are blocked rather than treated as ordinary weekdays.
- Raw artifacts are immutable and content-hashed.
- Normalized stores use atomic writes.
- PIT snapshots are content-addressed and immutable.

## Model/Publication controls
- Lifecycle: REGISTERED -> VALIDATED -> PAPER -> CHAMPION -> RETIRED.
- Champion is required for production publication.
- Dataset snapshot is required.
- Session validity and signal TTL are enforced.
- Existing statistical gates continue to require OOS evidence, CPCV/PBO/DSR, calibration, stability, drift, economic stress and bootstrap evidence.

## Operational controls
Readiness, data-health, model-health and publication-health endpoints are included. The dashboard remains read-only. No broker execution endpoints are implemented.

## Data packaging statement
No third-party or synthetic market history is relabeled as authoritative. Because this build environment has no outbound DNS/network access to NSE archives, official historical file bytes could not be truthfully embedded during this build. The release therefore ships the verified official-source catalog and acquisition/validation machinery and remains fail-closed until the authoritative files are acquired locally.
