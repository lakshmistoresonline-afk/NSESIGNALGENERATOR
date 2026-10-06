#!/usr/bin/env python3
"""Acquire authoritative NSE PIT raw artifacts without fabricating data.

Examples:
  python scripts/acquire_authoritative_pit.py --start 2026-09-01 --end 2026-09-30 --layers cash_bhavcopy,fo_bhavcopy,security_master,index_close

The script skips weekends, respects the included NSE holiday calendar, never
silently overwrites an existing artifact, and writes SHA-256 provenance.
Historical Nifty 200 membership is deliberately NOT reconstructed from today's
list; supply dated official constituent records or a licensed historical dataset.
"""
from __future__ import annotations
import argparse, sys, json
from datetime import date,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from nse_signal.data.nse.archives import download_artifact, append_manifest
from nse_signal.data.nse.session_calendar import load_holidays,is_trading_day
from nse_signal.data.nse.authoritative import required_layers

def dates(a,b,holidays):
    d=a
    while d<=b:
        if is_trading_day(d,holidays): yield d
        d+=timedelta(days=1)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--start',required=True); ap.add_argument('--end',required=True); ap.add_argument('--layers',default='cash_bhavcopy,fo_bhavcopy,security_master,index_close'); ap.add_argument('--raw-root',default='data/raw/nse'); args=ap.parse_args()
    layers=[x.strip() for x in args.layers.split(',') if x.strip()]
    allowed={'cash_bhavcopy','cm_bhavcopy','fo_bhavcopy','security_master','index_close'}
    bad=set(layers)-allowed
    if bad: raise SystemExit(f'Unsupported deterministic archive layers: {sorted(bad)}. Use official landing pages for secondary reports.')
    holidays=load_holidays(); count=0; failed=[]
    for d in dates(date.fromisoformat(args.start),date.fromisoformat(args.end),holidays):
        for layer in layers:
            actual_layer = 'cm_bhavcopy' if layer == 'cash_bhavcopy' else layer
            try:
                a=download_artifact(actual_layer,d,args.raw_root)
                append_manifest(a,str(Path(args.raw_root)/'manifest.jsonl')); count+=1
                print(f'OK {layer} {d} sha256={a.sha256} bytes={a.bytes}')
            except Exception as exc:
                print(f'FAIL {layer} {d} :: {exc}')
                failed.append({"layer": layer, "date": d.isoformat(), "error": str(exc)})

    fail_p = Path(args.raw_root) / 'acquisition_failures.json'
    fail_p.parent.mkdir(parents=True, exist_ok=True)
    fail_p.write_text(json.dumps(failed, indent=2, sort_keys=True), encoding='utf-8')
    print(f'acquired={count}, failed={len(failed)}')
if __name__=='__main__': main()
