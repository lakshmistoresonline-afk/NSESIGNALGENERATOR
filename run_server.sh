#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 -m venv .venv 2>/dev/null || true
. .venv/bin/activate
python -m pip install -r requirements.txt
PYTHONPATH="$PWD/src" python -m uvicorn server.api:app --host 0.0.0.0 --port 8010
