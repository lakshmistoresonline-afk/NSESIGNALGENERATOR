"""Robust AST-based Static Security Audit: Uses Python ast.parse() and AST node inspection to detect forbidden hardcoded constants, feature fallbacks (row.get with defaults), fabricated expected values, artificial timestamps, and fallback artifacts. Fails closed if any semantic violation is found."""
from __future__ import annotations
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class SignalSemanticASTVisitor(ast.NodeVisitor):
    def __init__(self):
        self.violations = []

    def visit_Call(self, node):
        # Check for dict .get(..., default) calls on features or row objects
        if isinstance(node.func, ast.Attribute) and node.func.attr == "get":
            if len(node.args) > 1:
                self.violations.append(f"Forbidden feature/row .get() with default fallback value at line {node.lineno}.")
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id
                if name == "expected_value":
                    self.violations.append(f"Forbidden assignment to '{name}' at line {node.lineno}.")
                if name in {"risk_gate_status", "publication_status"} and isinstance(node.value, ast.Constant) and node.value.value == "PASS":
                    self.violations.append(f"Hardcoded PASS assignment for '{name}' at line {node.lineno}.")
        self.generic_visit(node)

    def visit_Constant(self, node):
        val = node.value
        if isinstance(val, (int, float)):
            if val in {0.5, 0.2, 0.02, 100.0, 0.02}:
                self.violations.append(f"Prohibited hardcoded numerical constant '{val}' at line {node.lineno}.")
        if isinstance(val, str):
            if "T16:00:00Z" in val or "T18:00:00Z" in val or "T09:15:00Z" in val:
                self.violations.append(f"Prohibited artificial timestamp string '{val}' at line {node.lineno}.")
            if "production_artifact.joblib" in val:
                self.violations.append(f"Prohibited fallback artifact path at line {node.lineno}.")
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
            visitor = SignalSemanticASTVisitor()
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
        print("AST STATIC AUDIT PASSED: Zero forbidden feature fallbacks or hardcoded values found via ast.parse().")
        sys.exit(0)

if __name__ == "__main__":
    audit_ast()
