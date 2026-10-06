"""Point-in-time canonical store with deterministic deduplication and provenance."""
from __future__ import annotations
from pathlib import Path
import json,pandas as pd,os
from nse_signal.data.provenance import validate_asof_data, merge_point_in_time
from nse_signal.data.nse.pit_quality import dedupe_latest

class PITStore:
    def __init__(self,root='data/processed/nse_pit'):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
    def write(self,name,df,key_cols=None):
        if 'asof_time' not in df: raise ValueError(f'{name}: asof_time required')
        if 'symbol' not in df: raise ValueError(f'{name}: symbol required')
        x=df.copy()
        if key_cols: x=dedupe_latest(x,key_cols)
        check=validate_asof_data(x,'signal_time','asof_time') if 'signal_time' in x else {'pass':True}
        if not check['pass']: raise ValueError(f'PIT violation: {check}')
        path=self.root/f'{name}.csv'; tmp=path.with_suffix('.tmp'); x.to_csv(tmp,index=False); os.replace(tmp,path)
        meta=path.with_suffix('.meta.json'); mtmp=meta.with_suffix('.tmp'); mtmp.write_text(json.dumps({'rows':len(x),'columns':list(x.columns),'asof_check':check,'keys':key_cols or []},indent=2,default=str)); os.replace(mtmp,meta)
        return path
    def read(self,name):
        p=self.root/f'{name}.csv'; cols=pd.read_csv(p,nrows=0).columns
        return pd.read_csv(p,parse_dates=[c for c in ['date','signal_time','asof_time','expiry','nearest_expiry'] if c in cols])
    @staticmethod
    def asof_join(left,right,by='symbol'): return merge_point_in_time(left,right,'signal_time','asof_time',by=by)
