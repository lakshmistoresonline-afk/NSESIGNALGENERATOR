#!/usr/bin/env bash
set -euo pipefail
python3 scripts/acquire_authoritative_pit.py --start "$1" --end "$2"
