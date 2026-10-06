"""Iteration 9.9 Forensic Framework: Validator Runner in Fresh Subprocess."""
from __future__ import annotations
import subprocess
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from .models import ExecutionEvidence

def run_validator_subprocess(python_executable=sys.executable) -> tuple[ExecutionEvidence, dict]:
    start_t = time.perf_counter()
    cmd = [python_executable, "-c", "import sys, json; from nse_signal.data.pit_validator import validate_pit_dataset; res = validate_pit_dataset(); print(json.dumps(res))"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    end_t = time.perf_counter()

    validator_state = {}
    if res.returncode == 0 and res.stdout.strip():
        try:
            # find last line of stdout that is JSON
            lines = res.stdout.strip().splitlines()
            validator_state = json.loads(lines[-1])
        except Exception:
            pass

    ev = ExecutionEvidence(
        command=" ".join(cmd),
        cwd=str(Path.cwd()),
        start_time=datetime.now(timezone.utc).isoformat(),
        end_time=datetime.now(timezone.utc).isoformat(),
        duration_seconds=round(end_t - start_t, 4),
        exit_code=res.returncode,
        stdout=res.stdout,
        stderr=res.stderr
    )
    return ev, validator_state
