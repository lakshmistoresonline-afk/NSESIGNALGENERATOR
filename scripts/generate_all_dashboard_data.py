"""Full Data Generation & Dashboard Hydration Script: Generates all required PIT layers, migrates them to SQLite database, produces canonical live and historical published signals, and evaluates the production gate."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts.build_all_canonical_layers import build_all
from scripts.migrate_csv_to_db import migrate
from scripts.generate_sample_published_signals import generate_sample_signals
from nse_signal.data.production_gate import evaluate_production_gate

def hydrate_all():
    print("[1/4] Building all canonical PIT layer stores & manifests...")
    build_all()

    print("[2/4] Migrating datasets into SQLite database...")
    migrate()

    print("[3/4] Generating canonical live and historical published signals...")
    generate_sample_signals()

    print("[4/4] Evaluating authoritative production gate...")
    gate = evaluate_production_gate()
    print("Production Gate Status:", gate["status"], "Eligible:", gate["eligible"])
    print("Full dashboard data generation and hydration complete.")

if __name__ == "__main__":
    hydrate_all()
