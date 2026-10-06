# Final Release Audit — V14

## Frontend status

V14 **does include a frontend dashboard**. It is a self-contained HTML/CSS/JavaScript dashboard served by FastAPI at `/dashboard`; it does not require Node, npm, or a frontend build step.

The existing Streamlit application remains available as the exploratory research UI.

## V14 fixes

- Added operational frontend dashboard.
- Added read-only dashboard overview and published-signal endpoints.
- Restricted CORS to configured local dashboard origins by default.
- Marked the `/signal` API as `research_only`; non-research sources are rejected.
- Added PIT readiness, layer coverage and provenance status endpoints.
- Dashboard fails closed when required PIT data is unavailable.
- Added stale-row failure to PIT quality pass/fail logic.
- Added API/dashboard smoke validation.
- Preserved `REAL_TRADING = FALSE` and no broker execution.

## Validation

- 69 pytest tests passed.
- Python compileall passed.
- FastAPI dashboard smoke test passed for HTML, CSS, JS, health and overview endpoints.
- Dashboard requires no Node/npm runtime dependency.

## Known non-correctness warning

The large indicator builder emits pandas DataFrame-fragmentation performance warnings. They do not cause test failures or alter the calculated values. A future performance-only refactor can batch indicator construction with `pd.concat`.

## Production data boundary

The dashboard does not treat synthetic research data as live NSE data. Required PIT layers remain fail-closed until authoritative datasets have actually been acquired and validated.
