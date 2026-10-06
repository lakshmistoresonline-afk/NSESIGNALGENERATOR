#!/usr/bin/env python3
"""Capture the current NIFTY 200 constituent snapshot only.

This does NOT backfill historical membership. Historical intervals must come from
a dated authoritative constituent dataset.
"""
from __future__ import annotations
import sys
from pathlib import Path as _Path
_ROOT=_Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))
import argparse
from datetime import date
import pandas as pd
from nse_signal.data.nse.live import NSEReadOnlyClient

ap=argparse.ArgumentParser(); ap.add_argument('--effective-from',required=True); ap.add_argument('--out',default='data/reference/nifty200_current_snapshot.csv'); args=ap.parse_args()
data=NSEReadOnlyClient().nifty200()
rows=[]
for r in data.get('data',[]):
    sym=r.get('symbol') or r.get('identifier')
    if sym and sym not in ('NIFTY 200',): rows.append({'symbol':sym,'effective_from':args.effective_from,'effective_to':'','source':'NSE web NIFTY 200 snapshot','source_asof':pd.Timestamp.utcnow().isoformat()})
if not rows: raise SystemExit('NIFTY 200 snapshot returned no constituent rows')
pd.DataFrame(rows).drop_duplicates('symbol').to_csv(args.out,index=False)
print(f'wrote {len(rows)} current constituents to {args.out}; do not treat as historical membership')
