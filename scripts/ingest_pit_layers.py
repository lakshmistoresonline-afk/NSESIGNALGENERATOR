#!/usr/bin/env python3
"""Normalize locally acquired official NSE/PIT secondary layers."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
import argparse
from nse_signal.data.nse.pit_layers import normalize_delivery, normalize_impact_cost, normalize_breadth, normalize_vix, normalize_corporate_events, normalize_pit_fundamentals, normalize_participant_oi, normalize_fii_derivatives, normalize_daily_volatility
from nse_signal.data.nse.store import PITStore

FUNCS={'delivery':normalize_delivery,'impact_cost':normalize_impact_cost,'breadth':normalize_breadth,'india_vix':normalize_vix,'corporate_events':normalize_corporate_events,'fundamentals':normalize_pit_fundamentals,'participant_oi':normalize_participant_oi,'fii_derivatives':normalize_fii_derivatives,'daily_volatility':normalize_daily_volatility}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('layer',choices=sorted(FUNCS)); ap.add_argument('file'); ap.add_argument('--out',default='data/processed/nse_pit'); ap.add_argument('--asof-time'); args=ap.parse_args()
 fn=FUNCS[args.layer]; kwargs={}
 if args.asof_time and args.layer in {'delivery','impact_cost','breadth','india_vix'}: kwargs['asof_time']=args.asof_time
 df=fn(args.file,**kwargs)
 if 'symbol' not in df: df['symbol']='__MARKET__'
 p=PITStore(args.out).write(args.layer,df); print(f'WROTE {p} rows={len(df)}')
if __name__=='__main__': main()
