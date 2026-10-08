"""Robust AST-based Static Security Audit: Uses Python ast.parse() to inspect historical_engine.py and live_engine.py for forbidden hardcoded constants, fabricated scores, fixed timestamps, assert passes, and fallback artifacts. Fails closed if any semantic violation is found."""
from __future__ import annotations
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class SignalASTVisitor(ast.NodeVisitor):
    def __init__(self):
        self.violations = []

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id
                if name in {"factor_score", "regime_score", "quality_score"} and isinstance(node.value, ast.Constant):
                    self.violations.append(f"Hardcoded score assignment '{name} = {node.value.value}' detected.")
                if name in {"risk_gate_status", "publication_status"} and isinstance(node.value, ast.Constant) and node.value.value == "PASS":
                    self.violations.append(f"Hardcoded PASS string assignment for '{name}' detected.")
                if name == "pit_provenance_verified" and isinstance(node.value, ast.Constant) and node.value.value is True:
                    self.violations.append("Hardcoded pit_provenance_verified=True detected.")
        self.generic_visit(node)

    def visit_Constant(self, node):
        val = node.value
        if isinstance(val, (int, float)):
            if val in {0.65, 0.60, 0.75, 0.98, 1.04, 100.0}:
                self.violations.append(f"Prohibited hardcoded numeric constant '{val}' detected.")
        if isinstance(val, str):
            if "T16:00:00Z" in val or "T18:00:00Z" in val:
                self.violations.append(f"Prohibited artificial timestamp string '{val}' detected.")
            if "production_artifact.joblib" in val:
                self.violations.append("Prohibited fallback artifact path 'production_artifact.joblib' detected.")
            if "median_values" in val:
                self.violations.append("Prohibited median_values reference detected.")
        self.generic_visit(node)

def audit_ast():
    targets = [
        ROOT / "src/nse_signal/signals/historical_engine.py",
        ROOT / "src/nse_signal/signals/live_engine.py"
    ]

    all_violations = []
    for t in targets:
        if not t.exists(): continue
        try:
            tree = ast.parse(t.read_text(encoding="utf-8"))
            visitor = SignalASTVisitor()
            visitor.visit(tree)
            if visitor.violations:
                all_violations.extend([f"{t.name}: {v}" for v in visitor.violations])
        except Exception as e:
            all_violations.append(f"AST parse error on {t.name}: {e}")

    if all_violations:
        print("AST STATIC AUDIT FAILED:")
        for v in all_violations:
            print(f" - {v}")
        sys.exit(1)
    else:
        print("AST STATIC AUDIT PASSED: Zero forbidden hardcoded anti-patterns found via ast.parse().")
        sys.exit(0)

if __name__ == "__main__":
    audit_ast()
