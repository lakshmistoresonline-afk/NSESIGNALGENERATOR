#!/usr/bin/env python3
"""Build a strict, deduplicated PIT panel from normalized official layers with explicit feature dependencies."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
import argparse,pandas as pd
from nse_signal.data.nse.store import PITStore
from nse_signal.data.nse.pit_quality import dedupe_latest
from nse_signal.data.provenance import validate_asof_data
from nse_signal.data.nse.membership import load_membership
from nse_signal.data.nse.corporate_actions import normalize_adjustments, apply_adjustments
from nse_signal.data.nse.restrictions import restriction_flags
from nse_signal.data.nse.session_calendar import next_trading_day, IST

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--cash',default='cash_daily'); ap.add_argument('--out',default='data/processed/nse_pit/pit_features.csv'); ap.add_argument('--layers',default='delivery,impact_cost,india_vix,breadth,derivatives_context,restrictions'); ap.add_argument('--root',default='data/processed/nse_pit'); ap.add_argument('--membership',default='data/reference/nifty200_membership.csv'); ap.add_argument('--universe',choices=['broad_nse','nifty200'],default='broad_nse'); ap.add_argument('--allow-empty-membership',action='store_true'); ap.add_argument('--corporate-event-gate',action='store_true'); args=ap.parse_args()
 st=PITStore(args.root); base=st.read(args.cash)
 if 'signal_time' not in base: raise ValueError('cash base lacks signal_time')

 adj_path=Path(args.root)/'corporate_adjustments.csv'
 if adj_path.exists():
  adj=normalize_adjustments(adj_path)
  base=apply_adjustments(base,adj)
 else:
  print('WARNING: corporate_adjustments.csv missing; research may be unadjusted.')

 base=base.copy(); base['date']=pd.to_datetime(base['date'],errors='coerce')
 if 'series' in base.columns:
  base=base[base['series'].astype(str).str.upper().eq('EQ')].copy()

 if args.universe == 'nifty200':
  m=load_membership(args.membership,allow_empty=args.allow_empty_membership)
  if m.empty and not args.allow_empty_membership:
   raise ValueError('NIFTY 200 universe requested but effective-dated membership is empty')
  if not m.empty:
   keep=[]
   for _,r in base[['symbol','date']].drop_duplicates().iterrows():
    # Half-open interval contract [effective_from, effective_to)
    mm=m[(m.symbol==str(r.symbol).upper())&(m.effective_from<=r.date)&(m.effective_to.isna()|(m.effective_to>r.date))]
    keep.append((r.symbol,r.date) if len(mm) else None)
   allowed=set(keep); base=base[base.apply(lambda r:(r.symbol,r.date) in allowed,axis=1)].copy()

 for name in [x.strip() for x in args.layers.split(',') if x.strip()]:
  p=Path(args.root)/(name+'.csv')
  if not p.exists():
   if name in {'derivatives_context','restrictions','delivery','impact_cost'}: continue
   raise FileNotFoundError(f'missing normalized layer: {name}')
  right=st.read(name)
  if name in {'delivery','impact_cost','restrictions','derivatives_context'}:
   if 'symbol' not in right: raise ValueError(f'{name} requires symbol')
   keys=['symbol','date'] if 'date' in right else ['symbol','asof_time']; right=dedupe_latest(right,keys)
   right=right.sort_values('asof_time'); base=base.sort_values('signal_time')
   base=pd.merge_asof(base,right,left_on='signal_time',right_on='asof_time',by='symbol',direction='backward',suffixes=('','_'+name))
  else:
   right=right.drop(columns=['symbol'],errors='ignore').drop_duplicates(['asof_time'])
   right=right.sort_values('asof_time'); base=base.sort_values('signal_time')
   base=pd.merge_asof(base,right,left_on='signal_time',right_on='asof_time',direction='backward',suffixes=('','_'+name))

 if 'impact_cost' in base.columns and 'impact_cost_bps' not in base.columns:
  base['impact_cost_bps']=pd.to_numeric(base['impact_cost'],errors='coerce')
 if {'surveillance','upper_band','lower_band','short_selling_allowed','close'}.issubset(base.columns):
  flags=base.apply(lambda r: restriction_flags(r, price=r.get('close'), side='SELL'),axis=1,result_type='expand')
  for c in ['restricted','near_price_band','short_sale_blocked']:
   base[c]=flags[c].fillna(False).astype(bool)
 elif 'restrictions' in args.layers:
  print('WARNING: restriction fields incomplete in layers.')

 # Corporate events handling based on explicit corporate_event_gate dependency
 evp=Path(args.root)/'corporate_events.csv'
 if evp.exists():
  ev=pd.read_csv(evp)
  if 'announcement_time' in ev.columns and 'symbol' in ev.columns:
   ev['announcement_time']=pd.to_datetime(ev['announcement_time'],utc=True,errors='coerce')
   for c in ['ex_date','record_date']:
    if c in ev: ev[c]=pd.to_datetime(ev[c],errors='coerce')
   ev_flag=[]; ev_block=[]
   for _,r in base[['symbol','signal_time']].iterrows():
    sym=str(r.symbol).upper(); st=pd.Timestamp(r.signal_time)
    g=ev[ev.symbol.astype(str).str.upper().eq(sym)]
    recent=((g.announcement_time<=st)&(g.announcement_time>st-pd.Timedelta(days=2))).any() if not g.empty else False
    sig_date=st.tz_convert(IST).date() if st.tzinfo else st.date()
    try: nxt=next_trading_day(sig_date)
    except Exception: nxt=None
    imminent=False
    if nxt is not None and not g.empty:
     for c in ['ex_date','record_date']:
      if c in g:
       dates=pd.to_datetime(g[c],errors='coerce').dt.date
       imminent |= dates.isin([sig_date,nxt]).any()
    ev_flag.append(bool(recent or imminent)); ev_block.append(bool(imminent))
   base['corporate_event_flag']=ev_flag
   base['event_blackout']=ev_block
 else:
  if args.corporate_event_gate:
   raise FileNotFoundError('corporate_events.csv is required because corporate_event_gate=true')
  else:
   base['corporate_event_flag']=False
   base['event_blackout']=False

 base['market_context_source']='NSE_OFFICIAL_PIT'
 checks={}
 for c in [c for c in base.columns if c=='asof_time' or c.startswith('asof_time_')]:
  checks[c]=validate_asof_data(base[['signal_time',c]].rename(columns={c:'asof_time'}))
 bad={k:v for k,v in checks.items() if not v['pass']}
 if bad: raise ValueError(f'PIT validation failed: {bad}')
 Path(args.out).parent.mkdir(parents=True,exist_ok=True); base.to_csv(args.out,index=False); print(f'WROTE {args.out} rows={len(base)} columns={len(base.columns)}')
if __name__=='__main__': main()
