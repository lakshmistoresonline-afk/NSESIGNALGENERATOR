#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path as _Path
_ROOT=_Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))
import argparse, json
from pathlib import Path
import pandas as pd
from nse_signal.data.provenance import validate_asof_data
from nse_signal.data.nse.membership import load_membership, assert_no_overlap

ap=argparse.ArgumentParser(); ap.add_argument('--root',default='data/processed/nse_pit'); ap.add_argument('--membership',default='data/reference/nifty200_membership.csv'); args=ap.parse_args()
root=Path(args.root); report={'files':{},'membership':{}}
for p in root.glob('*.csv'):
    df=pd.read_csv(p)
    r={'rows':len(df),'columns':len(df.columns),'duplicate_rows':int(df.duplicated().sum())}
    if {'signal_time','asof_time'}<=set(df.columns): r['asof']=validate_asof_data(df)
    report['files'][p.name]=r
try:
    m=load_membership(args.membership); assert_no_overlap(m); report['membership']={'rows':len(m),'status':'ok'}
except Exception as e: report['membership']={'status':'FAIL','reason':str(e)}
print(json.dumps(report,indent=2,default=str))
if any(v.get('asof',{}).get('pass') is False for v in report['files'].values()): raise SystemExit(2)
