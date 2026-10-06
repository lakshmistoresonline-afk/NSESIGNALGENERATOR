# Real NSE Data Acquisition Runbook

1. Populate `data/reference/nifty200_membership.csv` with authoritative effective-dated NIFTY 200 snapshots.
2. Run `python scripts/ingest_nse.py --start YYYY-MM-DD --end YYYY-MM-DD`.
3. Inspect `data/raw/nse/manifest.jsonl` for missing dates and SHA-256 hashes.
4. Inspect `data/processed/nse_pit/*.meta.json` for as-of validation.
5. Add corporate-event files only with publication/availability timestamps.
6. Add derivatives surface snapshots only when their observation timestamps are known.
7. Run the research audit and keep a completely untouched final holdout.
8. Do not tune thresholds against the final holdout.

For current/live read-only snapshots, use `NSEReadOnlyClient`. Public web endpoints can change or be rate-limited; use an official/licensed NSE data product when the required latency, history, redistribution rights or service guarantees exceed the public web/archive offering.

## Secondary PIT layers — final

After CM/FO/security-master ingestion, normalize locally acquired official reports:

```bash
python scripts/ingest_pit_layers.py delivery <delivery-file.csv>
python scripts/ingest_pit_layers.py impact_cost <impact-cost-file.csv>
python scripts/ingest_pit_layers.py breadth <breadth-file.csv>
python scripts/ingest_pit_layers.py india_vix <india-vix-file.csv>
python scripts/ingest_pit_layers.py corporate_events <corporate-events.csv>
python scripts/ingest_pit_layers.py fundamentals <pit-fundamentals.csv>
```

Then build the integrated daily PIT table:

```bash
python scripts/build_pit_dataset.py
python scripts/validate_pit_dataset.py
```

Corporate-event files must contain a real broadcast/announcement timestamp. Date-only event dates are rejected. Fundamentals must contain a real information-availability timestamp. This prevents look-ahead from reporting/period-end dates.

For the daily close signal, same-day delivery/breadth/VIX reports that are only available after the close are intentionally not joined to that close observation. They become eligible only for a subsequent signal after their `asof_time`. This is expected PIT behavior.
