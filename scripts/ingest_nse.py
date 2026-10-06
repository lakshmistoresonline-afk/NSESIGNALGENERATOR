#!/usr/bin/env python3
"""Ingest official NSE daily archives without overwriting prior days."""
from __future__ import annotations
import sys
from pathlib import Path as _Path
_ROOT=_Path(__file__).resolve().parents[1]; sys.path.insert(0,str(_ROOT/'src'))
import argparse
from datetime import date,timedelta
from pathlib import Path
import pandas as pd
from nse_signal.data.nse.archives import download_artifact,append_manifest
from nse_signal.data.nse.normalize import normalize_cash,normalize_fo,normalize_security_master,normalize_index
from nse_signal.data.nse.store import PITStore
from nse_signal.data.nse.pit_quality import dedupe_latest

def dates(a,b):
 d=a
 while d<=b:
  if d.weekday()<5: yield d
  d+=timedelta(days=1)

def append_layer(root,name,df,keys):
 p=Path(root)/f'{name}.csv';
 if p.exists():
  old=pd.read_csv(p,parse_dates=[c for c in ['date','signal_time','asof_time','expiry'] if c in pd.read_csv(p,nrows=0).columns])
  df=pd.concat([old,df],ignore_index=True)
 df=dedupe_latest(df,keys)
 p.parent.mkdir(parents=True,exist_ok=True); df.to_csv(p,index=False); return p

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--start',required=True); ap.add_argument('--end',required=True); ap.add_argument('--layers',default='cm_bhavcopy,fo_bhavcopy,index_close,security_master'); ap.add_argument('--raw-root',default='data/raw/nse'); ap.add_argument('--pit-root',default='data/processed/nse_pit'); args=ap.parse_args()
 layers=[x.strip() for x in args.layers.split(',') if x.strip()]; results=[]
 for d in dates(date.fromisoformat(args.start),date.fromisoformat(args.end)):
  for layer in layers:
   try:
    a=download_artifact(layer,d,args.raw_root); append_manifest(a,str(Path(args.raw_root)/'manifest.jsonl')); results.append(a)
    if layer=='cm_bhavcopy': append_layer(args.pit_root,'cash_daily',normalize_cash(a.path),['symbol','date'])
    elif layer=='fo_bhavcopy': append_layer(args.pit_root,'fo_daily',normalize_fo(a.path),['symbol','date','expiry','option_type','strike'])
    elif layer=='security_master': append_layer(args.pit_root,'security_master',normalize_security_master(a.path),['symbol','asof_time'])
    elif layer=='index_close': append_layer(args.pit_root,'index_daily',normalize_index(a.path),['symbol','date'])
    print(f'OK {layer} {d} {a.bytes} bytes')
   except Exception as exc: print(f'SKIP {layer} {d}: {exc}')
 print(f'completed artifacts={len(results)}')
if __name__=='__main__': main()
