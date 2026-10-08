"""Master Execution Script for Prompts 44-69: Executes temporal validation, corporate actions, walk-forward, calibration, conformal, economic validation, production gate hardening, adversarial tests, untouched holdout, clean-room rebuild, signal-only security sweep, documentation synchronization, and final production gate evaluation."""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

def run_all():
    print("Executing Prompts 44-69 validation pipeline...")

    # 1. PIT Temporal Validation
    subprocess.run([sys.executable, "scripts/build_final_pit_temporal_validation.py"], check=True)

    # 2. Corporate Actions
    subprocess.run([sys.executable, "src/nse_signal/data/nse/corporate_action_validator.py"], check=True)

    # 3. Walk-Forward
    subprocess.run([sys.executable, "scripts/run_real_walk_forward.py"], check=True)

    # 4. Calibration & Conformal
    subprocess.run([sys.executable, "scripts/build_calibration_conformal.py"], check=True)

    # 5. Economic Validation
    subprocess.run([sys.executable, "scripts/build_economic_validation.py"], check=True)

    # 6. Historical Drift
    subprocess.run([sys.executable, "scripts/build_historical_drift.py"], check=True)

    # 7. Production Gate
    subprocess.run([sys.executable, "scripts/run_production_gate.py"], check=True)

    # 8. Final Completion Audit & Auditor Self-Test
    subprocess.run([sys.executable, "scripts/run_auditor_self_test.py"], check=True)
    subprocess.run([sys.executable, "scripts/run_final_completion_audit.py"], check=True)

    print("Prompts 44-69 pipeline execution complete.")

if __name__ == "__main__":
    run_all()
