#!/usr/bin/env python3
"""Run unified evidence-driven production gate evaluation."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'src'))
from nse_signal.data.production_gate import evaluate_production_gate

def main():
    res = evaluate_production_gate(str(ROOT))
    print(f"Production Gate Status: {res['status']} (Eligible: {res['eligible']})")
    print(f"Blocking Reasons: {res['blocking_reasons']}")

if __name__ == "__main__":
    main()
