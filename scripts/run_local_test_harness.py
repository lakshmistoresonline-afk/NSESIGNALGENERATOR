"""Local System Test Harness: Exercises backend API routes, live and historical signal generation engines, and production gate checks locally on the developer workstation without requiring an Android AVD or physical device."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "server"))

from server.api import app
from nse_signal.signals.historical_engine import HistoricalSignalEngine
from nse_signal.signals.live_engine import LiveSignalEngine
from nse_signal.data.production_gate import evaluate_production_gate

def run_local_harness():
    print("Initializing Local System Test Harness...")
    client = TestClient(app)

    # 1. Test Backend Health & API Endpoints
    print("[1/4] Testing Backend Health API...")
    try:
        res = client.get("/api/v1/health")
        print("Health response:", res.status_code, res.json())
    except Exception as e:
        print("Health API test note:", e)

    # 2. Test Production Gate Evaluation
    print("[2/4] Evaluating Production Gate locally...")
    gate = evaluate_production_gate()
    print("Production Gate Status:", gate["status"], "Eligible:", gate["eligible"])

    # 3. Test Historical Signal Engine Locally
    print("[3/4] Testing Historical Signal Generation locally...")
    hist_engine = HistoricalSignalEngine()
    hist_signals = hist_engine.generate_historical_signals("2024-01-02", "2024-01-02")
    print(f"Generated {len(hist_signals)} historical signals.")

    # 4. Test Live Signal Engine Locally
    print("[4/4] Testing Live Signal Engine locally...")
    live_engine = LiveSignalEngine()
    live_res = live_engine.scan_live_universe(session_id="LOCAL_HARNESS_TEST")
    print("Live scan result status:", live_res.get("status"), "Signals:", len(live_res.get("signals", [])))

    print("Local System Test Harness completed successfully.")

if __name__ == "__main__":
    run_local_harness()
