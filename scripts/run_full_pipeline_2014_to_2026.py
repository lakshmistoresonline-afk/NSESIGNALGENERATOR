"""Master Pipeline Orchestration Script: Runs database migration, PIT building, PIT validation, historical signal generation, and production gate evaluation with PYTHONPATH=src."""
from __future__ import annotations
import sys
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

def run_command(cmd, desc):
    print(f"\n[ORCHESTRATION] === {desc} ===")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
    print(res.stdout)
    if res.stderr:
        print("STDERR:", res.stderr)
    if res.returncode != 0:
        print(f"WARNING: Command failed with exit code {res.returncode}")
    else:
        print(f"SUCCESS: {desc} completed successfully.")
    return res.returncode == 0

def main():
    print("Starting Master Pipeline Orchestration (2014 to 2026)...")

    run_command("python scripts/migrate_csv_to_db.py", "Database Migration")
    run_command("python -m nse_signal.cli --build-pit", "PIT Dataset Builder")
    run_command("python -m nse_signal.cli --validate-pit", "PIT Dataset Validator")
    run_command("python scripts/generate_real_historical_signals_from_db.py", "Historical Signal Generation Engine")
    run_command("python scripts/run_production_gate.py", "Authoritative Production Gate Evaluation")

    print("\nMaster Pipeline Orchestration execution finished.")

if __name__ == "__main__":
    main()
