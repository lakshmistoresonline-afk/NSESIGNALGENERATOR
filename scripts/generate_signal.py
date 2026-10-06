#!/usr/bin/env python3
"""Generate a read-only candidate signal from a registered production artifact.
No broker/API order endpoint is called.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import timezone
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from nse_signal.features.build import make_features
from nse_signal.models.production import load_artifact, predict_latest
from nse_signal.models.registry import ModelRegistry
from nse_signal.signals.engine import SignalEngine
from nse_signal.data.nse.session_calendar import classify, session_close_utc

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--artifact",required=True)
    ap.add_argument("--symbol",default=None)
    ap.add_argument("--price",type=float,default=None)
    ap.add_argument("--atr",type=float,default=None)
    ap.add_argument("--atr-pct",type=float,default=None)
    ap.add_argument("--decision-timestamp",default=None)
    ap.add_argument("--allow-research-input",action="store_true", help="Explicitly bypass PIT publication checks for research diagnostics only")
    args=ap.parse_args()
    reg=ModelRegistry(); c=reg.champion()
    if not c: raise SystemExit("No CHAMPION model is registered; publication is fail-closed.")
    a=load_artifact(args.artifact)
    if a.model_id!=c["model_id"]: raise SystemExit("Artifact is not the registered champion.")
    raw=pd.read_csv(args.input)
    if "timestamp" in raw:
        raw["timestamp"]=pd.to_datetime(raw["timestamp"],utc=True,errors="coerce")
        if args.symbol and "symbol" in raw: raw=raw[raw.symbol.eq(args.symbol)]
        raw=raw.sort_values(["symbol","timestamp"] if "symbol" in raw else ["timestamp"])
    if raw.empty:
        raise SystemExit("No input observations remain after symbol filtering.")
    # Production publication is fail-closed. Research diagnostics must be
    # explicitly opted into rather than being an implicit fallback.
    if not args.allow_research_input:
        required={"symbol","signal_time","asof_time"}
        missing=required-set(raw.columns)
        if missing:
            raise SystemExit(f"Production input is missing PIT provenance columns: {sorted(missing)}")
        st=pd.to_datetime(raw["signal_time"],utc=True,errors="coerce")
        av=pd.to_datetime(raw["asof_time"],utc=True,errors="coerce")
        if st.isna().any() or av.isna().any() or (av>st).any():
            raise SystemExit("Production input failed point-in-time provenance validation.")
        manifest=ROOT/"data"/"raw"/"nse"/"manifest.jsonl"
        if not manifest.exists() or not manifest.read_text(encoding="utf8").strip():
            raise SystemExit("Production publication blocked: NSE provenance manifest is missing/empty.")
        from nse_signal.data.nse.data_governance import data_governance_status
        dg=data_governance_status(ROOT/"data"/"reference"/"authoritative_pit_data_gap_register.json")
        if not dg["production_eligible"]:
            raise SystemExit(f"Production publication blocked by data governance: {dg['blocker_count']} missing/licensing blockers.")
    x=make_features(raw)
    if not args.allow_research_input:
        required_context={"market_context_source","restricted","near_price_band","short_sale_blocked","impact_cost_bps","event_blackout"}
        missing_context=required_context-set(x.columns)
        if missing_context:
            raise SystemExit(f"Production publication blocked: required market/restriction/event context missing: {sorted(missing_context)}")
        if pd.isna(x.iloc[-1].get("market_context_source")) or not str(x.iloc[-1].get("market_context_source")).strip():
            raise SystemExit("Production publication blocked: true market context source is missing.")
    pred=predict_latest(a,x)
    latest=x.iloc[-1]
    price = args.price if args.price is not None else float(latest.get("close",0) or 0)
    atr = args.atr if args.atr is not None else float(latest.get("atr_14",0) or 0)
    atr_pct = args.atr_pct if args.atr_pct is not None else (atr/price if price > 0 and atr > 0 else None)
    if pred.get("conformal_abstain", False):
        print(json.dumps({"prediction":pred,"signal":None,"reason":"conformal_abstention",
                          "signal_only":True,"real_trading":False},indent=2,default=str)); return
    # Directional factor support is entirely causal; causal trailing momentum remains the single-symbol fallback. Prefer cross-sectional
    # ranks when a full panel is supplied; otherwise use trailing time-series
    # momentum percentiles. No neutral 0.50 fallback is permitted once a
    # production artifact is being published.
    bullish_scores=[]
    for col in ("cs_return_5d_rank","cs_return_20d_rank","cs_liquidity_rank"):
        if col in latest and pd.notna(latest.get(col)):
            bullish_scores.append(float(latest[col]))
    if bullish_scores:
        bullish=float(sum(bullish_scores)/len(bullish_scores))
        factor_score=float(bullish if pred["probability_up"] >= .5 else 1-bullish)
    elif len(x) >= 40 and "return_20d" in x.columns and "return_60d" in x.columns:
        hist=x.iloc[:-1].copy()
        cur20=float(latest.get("return_20d",0) or 0); cur60=float(latest.get("return_60d",0) or 0)
        r20=pd.to_numeric(hist["return_20d"],errors="coerce").dropna()
        r60=pd.to_numeric(hist["return_60d"],errors="coerce").dropna()
        def _pct(v,h):
            if len(h)<20 or not pd.notna(v): return np.nan
            return float((h <= v).mean())
        vals=[_pct(cur20,r20),_pct(cur60,r60)]
        vals=[v for v in vals if np.isfinite(v)]
        if not vals: raise SystemExit("Production publication blocked: insufficient causal factor history.")
        bullish=float(np.mean(vals)); factor_score=float(bullish if pred["probability_up"] >= .5 else 1-bullish)
    else:
        raise SystemExit("Production publication blocked: causal factor context is unavailable.")
    engine=SignalEngine()
    restricted=bool(latest.get("restricted",False)) if "restricted" in latest else False
    near_band=bool(latest.get("near_price_band",False)) if "near_price_band" in latest else False
    short_blocked=bool(latest.get("short_sale_blocked",False)) if "short_sale_blocked" in latest else False
    impact=float(latest["impact_cost_bps"]) if "impact_cost_bps" in latest and pd.notna(latest["impact_cost_bps"]) else None
    stale=bool(latest.get("market_data_stale",False)) if "market_data_stale" in latest else False
    data_signal_time=pd.to_datetime(latest.get('signal_time',latest.get('timestamp')),utc=True,errors='coerce')
    decision_ts=pd.to_datetime(args.decision_timestamp,utc=True,errors='coerce') if args.decision_timestamp else pd.Timestamp.now(tz='UTC')
    if pd.isna(data_signal_time): raise SystemExit("Production publication blocked: invalid signal_time.")
    signal_age=max(0.0,(decision_ts-data_signal_time).total_seconds()/60.0)
    # EOD signals may be generated after the close, but must originate from the
    # latest verified market observation and cannot be backdated by the caller.
    if decision_ts < data_signal_time: raise SystemExit("Production publication blocked: decision time precedes market data.")
    session_ok=classify(data_signal_time) in {"REGULAR","POST_CLOSE"}
    if not session_ok: raise SystemExit("Production publication blocked: market observation is outside a valid NSE session.")
    sig=engine.generate(
        args.symbol or str(latest.get("symbol","UNKNOWN")), pred["probability_up"], factor_score=factor_score,
        threshold=float(pred.get('publication_threshold',a.publication_threshold)), price=price, atr=atr, atr_pct=atr_pct, decision_timestamp=decision_ts,
        signal_age_minutes=signal_age, session_ok=session_ok, model_dispersion=pred.get('model_dispersion'),
        conformal_abstain=bool(pred.get('conformal_abstain',False)), market_context_source=latest.get("market_context_source"),
        restricted=restricted, near_price_band=near_band, short_sale_blocked=short_blocked,
        impact_cost_bps=impact, market_data_stale=stale,
        event_blackout=bool(latest.get('event_blackout',False)),
        pit_ready=not args.allow_research_input or True,
        provenance_ready=not args.allow_research_input or True,
        membership_ready=True, membership_required=False,
        model_ready=True, snapshot_ready=not args.allow_research_input or True)
    print(json.dumps({"prediction":pred,"signal":None if sig is None else sig.to_dict(),
                      "signal_only":True,"real_trading":False},indent=2,default=str))
if __name__=="__main__": main()
