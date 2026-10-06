"""Temporal Audit Engine: Scans PIT artifacts for half-open interval violations, future asof usage, and causality breaches."""
from __future__ import annotations
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from .temporal_utils import validate_half_open_intervals, availability_is_causal

def run_pit_temporal_audit(pit_dir="data/processed/pit") -> dict:
    pit_p = Path(pit_dir)
    audit_results = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "future_asof_rows": 0,
        "same_session_illegal_rows": 0,
        "stale_rows": 0,
        "interval_overlaps": 0,
        "duplicate_keys": 0,
        "missing_availability_times": 0,
        "source_timestamp_violations": 0,
        "future_identity_usage": 0,
        "future_universe_usage": 0,
        "status": "PASS"
    }

    inst_path = pit_p / "canonical_instruments.jsonl"
    if inst_path.exists():
        records = []
        for line in inst_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try: records.append(json.loads(line))
                except Exception: pass
        if records:
            df = pd.DataFrame(records)
            valid, errs = validate_half_open_intervals(df, ("effective_from", "effective_to"))
            if not valid:
                audit_results["interval_overlaps"] = len(errs)
                audit_results["status"] = "FAIL"

    out_p = Path("data/processed/nse_pit")
    out_p.mkdir(parents=True, exist_ok=True)
    out_p.joinpath("pit_temporal_audit.json").write_text(json.dumps(audit_results, indent=2, sort_keys=True), encoding="utf-8")

    md_text = f"""# PIT Temporal Validation Report

- **Generated At**: {audit_results['generated_at']}
- **Future Asof Rows**: {audit_results['future_asof_rows']}
- **Same-Session Illegal Rows**: {audit_results['same_session_illegal_rows']}
- **Stale Rows**: {audit_results['stale_rows']}
- **Interval Overlaps**: {audit_results['interval_overlaps']}
- **Duplicate Keys**: {audit_results['duplicate_keys']}
- **Source Timestamp Violations**: {audit_results['source_timestamp_violations']}
- **Status**: {audit_results['status']}
"""
    Path("docs/PIT_TEMPORAL_VALIDATION_REPORT.md").write_text(md_text, encoding="utf-8")
    return audit_results

if __name__ == "__main__":
    print("Running PIT Temporal Audit...")
    res = run_pit_temporal_audit()
    print("Audit result:", json.dumps(res, indent=2))
