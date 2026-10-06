from __future__ import annotations
import argparse
from datetime import datetime, timezone
from pathlib import Path
from .registry import build_registry
from .base import save_with_provenance

def main():
    p=argparse.ArgumentParser(description="Acquire secondary broker/public market data for research only.")
    p.add_argument("provider", choices=["tejhq","bharatstock","upstox","5paisa","angelone","fyers","dhan","groww","yahoo"])
    p.add_argument("symbol")
    p.add_argument("--start", required=True)
    p.add_argument("--end", required=True)
    p.add_argument("--interval", default="1d")
    p.add_argument("--output", default="data/raw/secondary")
    p.add_argument("--symbol-token")
    p.add_argument("--groww-symbol")
    p.add_argument("--security-id")
    p.add_argument("--instrument-key")
    p.add_argument("--scrip-code")
    args=p.parse_args()
    start=datetime.fromisoformat(args.start)
    end=datetime.fromisoformat(args.end)
    start = start if start.tzinfo else start.replace(tzinfo=timezone.utc)
    end = end if end.tzinfo else end.replace(tzinfo=timezone.utc)
    reg=build_registry()
    kw={}
    if args.symbol_token: kw["symbol_token"]=args.symbol_token
    if args.groww_symbol: kw["groww_symbol"]=args.groww_symbol
    if args.security_id: kw["security_id"]=args.security_id
    if args.instrument_key: kw["instrument_key"]=args.instrument_key
    if args.scrip_code: kw["scrip_code"]=args.scrip_code
    result=reg.historical(args.provider,args.symbol,start,end,args.interval,**kw)
    out=Path(args.output)/args.provider/f"{args.symbol.replace(':','_').replace('/','_')}.csv"
    path,meta=save_with_provenance(result.dataframe,path,result,{"start":args.start,"end":args.end,"interval":args.interval,**kw})
    print(f"Saved {path} rows={len(result.dataframe)} sha256={meta['sha256']}")

if __name__ == "__main__": main()
