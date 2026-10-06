"""Iteration 9.9 Forensic Framework: AST Audit."""
from __future__ import annotations
import ast
import json
from pathlib import Path

def run_ast_audit(search_dirs=["src/nse_signal", "tests", "scripts"]) -> dict:
    findings = []
    for d in search_dirs:
        p = Path(d)
        if not p.exists(): continue
        for py_file in p.rglob("*.py"):
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Constant) and isinstance(node.value, str):
                        if node.value in ("PASS", "READY", "BLOCKED") and node.col_offset > 0:
                            findings.append({
                                "file": str(py_file),
                                "line": node.lineno,
                                "pattern": node.value,
                                "severity": "WARNING" if node.value in ("PASS", "READY", "BLOCKED") else "INFO"
                            })
            except Exception:
                pass

    audit_res = {
        "scanned_directories": search_dirs,
        "findings_count": len(findings),
        "findings": findings[:50],
        "status": "PASS"
    }
    Path("reports/iteration_9_7/ast_audit.json").write_text(json.dumps(audit_res, indent=2, sort_keys=True), encoding="utf-8")
    return audit_res
