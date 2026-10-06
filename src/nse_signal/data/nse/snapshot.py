"""Content-addressed immutable PIT dataset snapshots."""
from __future__ import annotations
import hashlib,json,os
from pathlib import Path
import pandas as pd

def _sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def snapshot_csv(source, out_root='data/processed/nse_pit/snapshots', contract='PIT_DATA_CONTRACT_V2'):
    src=Path(source)
    if not src.exists(): raise FileNotFoundError(src)
    df=pd.read_csv(src)
    required={'symbol','date','signal_time','asof_time'}
    if not required.issubset(df.columns): raise ValueError(f'snapshot requires {sorted(required)}')
    for c in ['date','signal_time','asof_time']: df[c]=pd.to_datetime(df[c],utc=True,errors='coerce') if c!='date' else pd.to_datetime(df[c],errors='coerce')
    if df[['signal_time','asof_time']].isna().any().any(): raise ValueError('snapshot contains invalid PIT timestamps')
    if (df['asof_time']>df['signal_time']).any(): raise ValueError('snapshot contains future-asof rows')
    canonical=df.sort_values(['date','symbol']).copy()
    payload=canonical.to_csv(index=False,date_format='%Y-%m-%dT%H:%M:%S%z').encode()
    sid=hashlib.sha256(payload).hexdigest()[:32]
    root=Path(out_root)/sid; root.mkdir(parents=True,exist_ok=False) if not root.exists() else None
    data_path=root/'dataset.csv'; meta_path=root/'manifest.json'
    if not data_path.exists():
        tmp=data_path.with_suffix('.tmp'); tmp.write_bytes(payload); os.replace(tmp,data_path)
    meta={'snapshot_id':sid,'contract':contract,'source_sha256':_sha(src),'rows':len(canonical),'symbols':int(canonical.symbol.nunique()),'date_min':str(canonical.date.min().date()) if len(canonical) else None,'date_max':str(canonical.date.max().date()) if len(canonical) else None,'dataset_sha256':_sha(data_path),'immutable':True}
    if meta_path.exists() and json.loads(meta_path.read_text()) != meta: raise RuntimeError('snapshot manifest conflict')
    else:
        tmp=meta_path.with_suffix('.tmp'); tmp.write_text(json.dumps(meta,indent=2,sort_keys=True)); os.replace(tmp,meta_path)
    return meta
