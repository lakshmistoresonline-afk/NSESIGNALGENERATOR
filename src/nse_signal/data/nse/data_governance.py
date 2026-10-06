"""Authoritative PIT data possession/licensing readiness checks."""
from __future__ import annotations
import json
from pathlib import Path

DEFAULT_REGISTER = Path("data/reference/authoritative_pit_data_gap_register.json")


def load_gap_register(path=DEFAULT_REGISTER) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"PIT data gap register missing: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def data_governance_status(path=DEFAULT_REGISTER) -> dict:
    reg = load_gap_register(path)
    gaps = reg.get("gaps", [])
    blockers = [
        {
            "layer": x.get("layer"),
            "status": x.get("status"),
            "dataset": x.get("dataset"),
            "authority": x.get("authority"),
            "official_reference": x.get("official_reference"),
        }
        for x in gaps
        if x.get("status") in {"NOT_SUPPLIED_OR_LICENSED", "NOT_BUNDLED"} and x.get("production_required", True)
    ]
    return {
        "status": "blocked" if blockers else "ok",
        "production_eligible": not blockers,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "policy": reg.get("policy"),
    }
