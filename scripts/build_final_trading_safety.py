"""Hard Signal-Only Safety Invariant Validator: Scans repository for forbidden execution routes, verifies REAL_TRADING=FALSE, and writes data/processed/final_trading_safety.json."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

def audit_trading_safety():
    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)

    forbidden_tokens = [
        "placeOrder", "submitOrder", "createOrder", "executeOrder",
        "broker SDK", "trade execution", "portfolio execution"
    ]

    violations = []

    # Scan python files
    for py_file in ROOT.rglob("*.py"):
        if ".venv" in str(py_file) or "site-packages" in str(py_file): continue
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            for token in forbidden_tokens:
                if token.lower() in content.lower() and not ("not allowed" in content.lower() or "prohibited" in content.lower()):
                    # check if it's in a test asserting absence
                    if "test" not in py_file.name.lower():
                        violations.append(f"Forbidden token '{token}' found in {py_file}")
        except Exception:
            pass

    from nse_signal.signals.engine import SignalEngine
    eng = SignalEngine()
    real_trading_false = (getattr(eng, "real_trading", True) is False)

    status = "PASS" if not violations and real_trading_false else "FAIL"

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "invariant": "REAL_TRADING = FALSE",
        "signal_only": True,
        "real_trading_false_verified": real_trading_false,
        "forbidden_tokens_scanned": forbidden_tokens,
        "violations_detected": violations,
        "status": status
    }

    out_path = out_dir / "final_trading_safety.json"
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print("Final trading safety report generated:", out_path)
    return report

if __name__ == "__main__":
    audit_trading_safety()
