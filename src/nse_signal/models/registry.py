"""Atomic champion/challenger model registry with fail-closed lifecycle."""
from __future__ import annotations
from pathlib import Path
import json, os, hashlib, time
STATUSES={'REGISTERED','VALIDATED','PAPER','CHAMPION','RETIRED'}
TRANSITIONS={
 'REGISTERED':{'VALIDATED','RETIRED'},
 'VALIDATED':{'PAPER','RETIRED'},
 'PAPER':{'CHAMPION','RETIRED'},
 'CHAMPION':{'RETIRED'},
 'RETIRED':set(),
}
class ModelRegistry:
    def __init__(self,path='data/processed/model_registry.json'):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def _read(self):
        if not self.path.exists(): return {'version':1,'models':{},'champion':None}
        return json.loads(self.path.read_text(encoding='utf-8'))
    def _write(self,obj):
        raw=json.dumps(obj,sort_keys=True,indent=2); tmp=self.path.with_suffix('.tmp'); tmp.write_text(raw,encoding='utf-8'); os.replace(tmp,self.path)
    def register(self,model_id,contract_hash,metrics):
        if not model_id or model_id in self._read()['models']: raise ValueError('model already registered')
        d=self._read(); d['models'][model_id]={'model_id':model_id,'status':'REGISTERED','contract_hash':contract_hash,'metrics':metrics,'registered_at':time.time()}; self._write(d); return d['models'][model_id]
    def transition(self,model_id,status):
        if status not in STATUSES: raise ValueError(status)
        d=self._read(); m=d['models'].get(model_id)
        if not m: raise KeyError(model_id)
        if status not in TRANSITIONS[m['status']]: raise ValueError(f"invalid transition {m['status']} -> {status}")
        if status=='CHAMPION':
            gate=m.get('metrics',{}).get('gate')
            if not isinstance(gate,dict) or gate.get('pass') is not True:
                raise ValueError('champion promotion requires metrics.gate.pass=true from the full governance pipeline')
            if not m.get('contract_hash'):
                raise ValueError('champion promotion requires a non-empty contract hash')
            old=d.get('champion')
            if old and old in d['models']: d['models'][old]['status']='RETIRED'
            d['champion']=model_id
        m['status']=status; m['transitioned_at']=time.time(); self._write(d); return m
    def champion(self):
        d=self._read(); cid=d.get('champion'); m=d['models'].get(cid) if cid else None
        if not m or m.get('status')!='CHAMPION': return None
        return m
    @staticmethod
    def contract_hash(contract): return hashlib.sha256(json.dumps(contract,sort_keys=True).encode()).hexdigest()
