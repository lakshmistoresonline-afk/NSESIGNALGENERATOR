"""Clean-process import tests for pit_layer_validator and production_gate modules."""
from __future__ import annotations
import subprocess
import sys
import os

def test_import_pit_layer_validator():
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    cmd = [sys.executable, "-c", "import nse_signal.data.nse.pit_layer_validator; print('OK')"]
    res = subprocess.run(cmd, capture_output=True, text=True, env=env)
    assert res.returncode == 0
    assert "OK" in res.stdout

def test_import_production_gate():
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    cmd = [sys.executable, "-c", "import nse_signal.data.production_gate; print('OK')"]
    res = subprocess.run(cmd, capture_output=True, text=True, env=env)
    assert res.returncode == 0
    assert "OK" in res.stdout
