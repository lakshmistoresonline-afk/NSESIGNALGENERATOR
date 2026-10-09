"""Convenience script to start the FastAPI signal server for local browser testing."""
from __future__ import annotations
import sys
from pathlib import Path
import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "server"))

from server.api import app

if __name__ == "__main__":
    print("Starting NSE Signal Provider Server on http://localhost:8000")
    print("Open http://localhost:8000/dashboard in your browser to test the web interface.")
    uvicorn.run(app, host="127.0.0.1", port=8000)
