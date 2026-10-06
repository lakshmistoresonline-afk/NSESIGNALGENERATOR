#!/usr/bin/env python3
"""Download the official current Nifty 200 constituent list.

IMPORTANT: this file is a current snapshot, not historical PIT membership. It is
never automatically converted into historical effective-dated membership.
"""
from __future__ import annotations
import argparse, hashlib, os, urllib.request
from pathlib import Path
URL='https://nsearchives.nseindia.com/content/indices/ind_nifty200list.csv'
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='data/reference/nifty200_current_official.csv'); args=ap.parse_args()
    p=Path(args.out); p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists(): raise SystemExit(f'Refusing to overwrite existing official snapshot: {p}')
    req=urllib.request.Request(URL,headers={'User-Agent':'Mozilla/5.0 (compatible; NSE-Signal-Research/1.0)','Referer':'https://www.nseindia.com/'})
    with urllib.request.urlopen(req,timeout=45) as r: raw=r.read()
    tmp=p.with_suffix('.tmp'); tmp.write_bytes(raw); os.replace(tmp,p)
    print(f'{p} bytes={len(raw)} sha256={hashlib.sha256(raw).hexdigest()} source={URL}')
if __name__=='__main__': main()
