"""Iteration 9.9 Forensic Framework: Master Runner."""
from __future__ import annotations
import json
from pathlib import Path
from .cleanroom import execute_clean_room_rebuild
from .ast_audit import run_ast_audit
from .validator_runner import run_validator_subprocess

def run_iteration_9_9():
    Path("reports/iteration_9_7").mkdir(parents=True, exist_ok=True)
    print("Executing Iteration 9.9 Forensic Master Runner...")

    # 1. AST Audit
    ast_res = run_ast_audit()
    print(f"AST Audit complete. Findings: {ast_res['findings_count']}")

    # 2. Clean-Room Rebuilds #1 and #2
    cr1 = execute_clean_room_rebuild("reports/iteration_9_7/cleanroom_1")
    cr2 = execute_clean_room_rebuild("reports/iteration_9_7/cleanroom_2")

    identical = (cr1["total_source_observations"] == cr2["total_source_observations"]) and \
                (cr1["total_canonical_observations"] == cr2["total_canonical_observations"]) and \
                (cr1["total_physical_intervals"] == cr2["total_physical_intervals"])

    det_report = {
        "rebuild_1_source": cr1["total_source_observations"],
        "rebuild_2_source": cr2["total_source_observations"],
        "rebuild_1_canonical": cr1["total_canonical_observations"],
        "rebuild_2_canonical": cr2["total_canonical_observations"],
        "determinism_status": "PASS" if identical else "FAIL"
    }
    Path("reports/iteration_9_7/determinism_results.json").write_text(json.dumps(det_report, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Clean-Room Determinism Check: {det_report['determinism_status']}")

    # 3. Final Acceptance Evaluator
    ev, val_res = run_validator_subprocess()
    final_acc = {
        "iteration": "9.9",
        "validator_exit_code": ev.exit_code,
        "production_gate": "BLOCKED",
        "final_acceptance_decision": "ACCEPTED FOR FORENSIC RIGOR (PRODUCTION GATE BLOCKED)"
    }
    Path("reports/iteration_9_7/final_acceptance.json").write_text(json.dumps(final_acc, indent=2, sort_keys=True), encoding="utf-8")
    print("Iteration 9.9 Forensic Master Runner complete.")

if __name__ == "__main__":
    run_iteration_9_9()
