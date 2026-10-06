# NSE Signal Provider Frontend Dashboard

A self-contained, read-only dashboard served by FastAPI. It has **no Node/npm runtime dependency**.

Start the API from the repository root:

```bash
python -m uvicorn server.api:app --host 0.0.0.0 --port 8010
```

Open:

```text
http://127.0.0.1:8010/dashboard
```

The dashboard displays PIT readiness, required-layer status, dataset coverage, provenance count and only validated published paper signals. If PIT requirements are incomplete it shows `PIT BLOCKED` and `NO SIGNAL`.
