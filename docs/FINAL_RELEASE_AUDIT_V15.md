# Final Release Audit V15

## Scope
Audited V14 source, dashboard/API contract, PIT readiness, publication safety, configuration consistency, packaging, compilation and tests.

## Fixes
1. API now reads production-required PIT layers from configuration.
2. Effective-dated NIFTY 200 membership and non-empty checksum/provenance manifest are explicit production-readiness requirements.
3. Publication gate now enforces PIT readiness, provenance, membership, restriction, price-band, short-sale, stale-market-data and impact-cost conditions.
4. SignalEngine propagates PIT/provenance/membership readiness into publication.
5. Impact-cost cap is configuration-driven rather than hard-coded.
6. Dashboard API rejects malformed or execution-enabled published signal artifacts.
7. Dashboard now exposes PIT-universe and provenance status.
8. Frontend documentation uses the actual port 8010.
9. Release root is flattened; it does not ship inside a nested prior-release directory.

## Verification
- 72 pytest tests passed.
- Python compilation passed for src/server/app/scripts.
- FastAPI endpoint smoke tests passed for health, dashboard HTML/CSS/JS and dashboard APIs.
- ZIP integrity verified.

## Deliberate limitation
Real NSE historical data is not fabricated or embedded. Production remains blocked until authoritative PIT datasets and provenance manifests are actually acquired.
