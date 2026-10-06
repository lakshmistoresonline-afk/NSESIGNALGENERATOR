#!/usr/bin/env python3
"""Train a signal-only production candidate from a validated PIT feature dataset.
This script never executes trades and never promotes a model automatically.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from nse_signal.features.build import make_features
from nse_signal.models.production import fit_production_model, save_artifact
from nse_signal.models.registry import ModelRegistry

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True,help="Validated OHLCV/PIT CSV")
    ap.add_argument("--artifact",default="data/processed/model_candidates/nse_production.joblib")
    ap.add_argument("--model-id",default="nse-production")
    ap.add_argument("--horizon",type=int,default=5)
    ap.add_argument("--pt-atr",type=float,default=2.0)
    ap.add_argument("--sl-atr",type=float,default=1.0)
    args=ap.parse_args()
    raw=pd.read_csv(args.input)
    for c in ["open","high","low","close","volume"]:
        if c not in raw: raise SystemExit(f"missing required column: {c}")
    if "timestamp" in raw:
        raw["timestamp"]=pd.to_datetime(raw["timestamp"],utc=True,errors="coerce")
        raw=raw.sort_values(["symbol","timestamp"] if "symbol" in raw else ["timestamp"])
        raw=make_features(raw)
    else:
        raw=make_features(raw)
    artifact=fit_production_model(raw,horizon=args.horizon,pt_atr=args.pt_atr,sl_atr=args.sl_atr,model_id=args.model_id)
    path=save_artifact(artifact,args.artifact)
    reg=ModelRegistry()
    try:
        reg.register(args.model_id,artifact.contract_hash,{"artifact_path":str(path),"trained_through":artifact.trained_through,"features":len(artifact.features)})
        status = "REGISTERED_CANDIDATE"
    except Exception as exc:
        # Fail closed on model registration error rather than silent pass
        print(f"ERROR: Model registration failed: {exc}", file=sys.stderr)
        status = "REGISTRATION_FAILED"
        raise SystemExit(1)

    print(json.dumps({"status":status,"artifact":str(path),"model_id":artifact.model_id,"contract_hash":artifact.contract_hash,"trained_through":artifact.trained_through,"features":len(artifact.features),"signal_only":True,"real_trading":False},indent=2))
if __name__=="__main__":
    main()
