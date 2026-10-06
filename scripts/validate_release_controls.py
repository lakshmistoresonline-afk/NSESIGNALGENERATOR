#!/usr/bin/env python3
"""Validate release-time integrity across a built PIT dataset."""
from pathlib import Path
import sys,pandas as pd,json
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from nse_signal.data.nse.pit_quality import audit_pit_frame

def main():
 import argparse
 ap=argparse.ArgumentParser(); ap.add_argument('--file',default='data/processed/nse_pit/pit_features.csv'); args=ap.parse_args()
 if not Path(args.file).exists():
  print(json.dumps({'pass':False,'status':'BLOCKED','reason':'PIT dataset not built','file':args.file},indent=2))
  raise SystemExit(2)
 x=pd.read_csv(args.file)
 report={'rows':len(x),'checks':{}}
 for c in [c for c in x.columns if c=='asof_time' or c.startswith('asof_time_')]:
  report['checks'][c]=audit_pit_frame(x.rename(columns={c:'asof_time'}),key_cols=['symbol','signal_time'] if 'symbol' in x else ['signal_time'])
 report['pass']=all(v['pass'] for v in report['checks'].values())
 print(json.dumps(report,indent=2,default=str))
 if not report['pass']: raise SystemExit(2)
if __name__=='__main__': main()
