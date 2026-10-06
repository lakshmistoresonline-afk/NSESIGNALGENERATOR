#!/usr/bin/env python3
from pathlib import Path
import sys,pandas as pd
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from nse_signal.data.nse.derivatives import build_derivatives_context

def main():
 import argparse
 ap=argparse.ArgumentParser(); ap.add_argument('--fo',default='data/processed/nse_pit/fo_daily.csv'); ap.add_argument('--spot',default='data/processed/nse_pit/cash_daily.csv'); ap.add_argument('--out',default='data/processed/nse_pit/derivatives_context.csv'); args=ap.parse_args()
 fo=pd.read_csv(args.fo,parse_dates=['date','expiry'])
 spot=pd.read_csv(args.spot,parse_dates=['date']) if Path(args.spot).exists() else None
 out=build_derivatives_context(fo,spot)
 if out.empty: raise SystemExit('No usable option rows found; refusing to create an empty derivatives context')
 out['signal_time']=pd.to_datetime(out['date']).dt.tz_localize('Asia/Kolkata').dt.tz_convert('UTC')+pd.Timedelta(hours=10)
 out['asof_time']=out['signal_time']
 Path(args.out).parent.mkdir(parents=True,exist_ok=True); out.to_csv(args.out,index=False); print(f'WROTE {args.out} rows={len(out)}')
if __name__=='__main__': main()
