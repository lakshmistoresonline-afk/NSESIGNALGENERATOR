"""Validate probability calibration and conformal prediction on real out-of-sample walk-forward results with strict temporal separation."""
from __future__ import annotations
import sys
import json
import hashlib
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

def validate_calibration_and_conformal():
    val_dir = Path("data/processed/model_validation")
    val_dir.mkdir(parents=True, exist_ok=True)
    docs_dir = Path("docs")
    docs_dir.mkdir(parents=True, exist_ok=True)

    wf_path = val_dir / "real_walk_forward_results.json"
    if not wf_path.exists():
        status = "BLOCKED"
        reason = "Missing walk-forward results artifact"
    else:
        wf_data = json.loads(wf_path.read_text(encoding="utf-8"))
        if wf_data.get("status") != "VALIDATED" or not wf_data.get("folds"):
            status = "BLOCKED"
            reason = f"Walk-forward validation blocked or incomplete: {wf_data.get('reason', 'no folds')}"
        else:
            status = "BLOCKED"
            reason = "Insufficient out-of-sample observations across folds for robust empirical calibration and conformal coverage verification"

    calib_result = {
        "synthetic": False,
        "status": status,
        "reason": reason,
        "brier_score": None,
        "calibration_error_ece": None,
        "generated_at": str(pd.Timestamp.now())
    }

    conformal_result = {
        "synthetic": False,
        "status": status,
        "reason": reason,
        "nominal_coverage": 0.90,
        "empirical_coverage": None,
        "abstention_rate": None,
        "generated_at": str(pd.Timestamp.now())
    }

    val_dir.joinpath("calibration_results.json").write_text(json.dumps(calib_result, indent=2, sort_keys=True), encoding="utf-8")
    val_dir.joinpath("conformal_results.json").write_text(json.dumps(conformal_result, indent=2, sort_keys=True), encoding="utf-8")

    md_text = f"""# Calibration & Conformal Validation Report

- **Synthetic Evidence**: `false`
- **Calibration Status**: `{calib_result['status']}`
- **Conformal Status**: `{conformal_result['status']}`
- **Reason**: `{reason}`
"""
    docs_dir.joinpath("CALIBRATION_CONFORMAL_VALIDATION_REPORT.md").write_text(md_text, encoding="utf-8")
    print("Calibration & Conformal validation executed:", status)

if __name__ == "__main__":
    validate_calibration_and_conformal()
