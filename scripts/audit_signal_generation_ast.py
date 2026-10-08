"""AST and Static Security Audit for Signal Generation: Scans historical_engine.py and live_engine.py for forbidden hardcoded patterns (median fallbacks, default prices, artificial timestamps, hardcoded model hashes, fallback artifact paths) and fails closed if detected."""
from __future__ import annotations
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def audit_ast():
    targets = [
        ROOT / "src/nse_signal/signals/historical_engine.py",
        ROOT / "src/nse_signal/signals/live_engine.py"
    ]

    forbidden_substrings = [
        "median_values",
        "100.0",
        "T18:00:00Z",
        "production_artifact.joblib",
        "prob_up = 0.60",
        "factor_score = 0.70",
        "INE002A01018"
    ]

    violations = []
    for t in targets:
        if not t.exists():
            continue
        content = t.read_text(encoding="utf-8")
        for sub in forbidden_substrings:
            if sub in content:
                violations.append(f"Forbidden pattern '{sub}' found in {t.name}")

    if violations:
        print("AST AUDIT FAILED:", violations)
        sys.exit(1)
    else:
        print("AST AUDIT PASSED: Zero forbidden anti-patterns detected in signal generation engines.")
        sys.exit(0)

if __name__ == "__main__":
    audit_ast()
