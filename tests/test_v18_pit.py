from datetime import date
import json
import pandas as pd
from pathlib import Path

def test_official_catalog_contains_required_layers():
    from nse_signal.data.nse.authoritative import catalog, required_layers
    c=catalog(); layers={x['layer'] for x in c['sources']}
    assert set(required_layers()).issubset(layers)
    assert c['authority_policy']=='official_nse_only_for_production'

def test_archive_manifest_is_idempotent_and_immutable(tmp_path, monkeypatch):
    import nse_signal.data.nse.archives as a
    target=tmp_path/'cm_bhavcopy'/'2026-09-25.csv.zip'
    target.parent.mkdir(parents=True); target.write_bytes(b'first')
    monkeypatch.setattr(a,'_download',lambda url,dest: dest.write_bytes(b'second'))
    art=a.download_artifact('cm_bhavcopy',date(2026,9,25),str(tmp_path))
    assert art.sha256 == __import__('hashlib').sha256(b'first').hexdigest()
    try: a.download_artifact('cm_bhavcopy',date(2026,9,25),str(tmp_path),overwrite=True); assert False
    except RuntimeError: pass

def test_pit_eod_signal_is_next_session_not_same_day():
    from nse_signal.data.nse.normalize import normalize_cash
    p=Path('data/processed/sample_cash.csv'); p.parent.mkdir(parents=True,exist_ok=True)
    pd.DataFrame([{'SYMBOL':'ABC','TradDt':'2026-09-25','OpnPric':100,'HghPric':101,'LwPric':99,'ClsPric':100.5,'TtlTradgVol':1000}]).to_csv(p,index=False)
    try:
        x=normalize_cash(p)
        assert x.loc[0,'market_time'] < x.loc[0,'asof_time']
        assert pd.Timestamp(x.loc[0,'signal_time']) > pd.Timestamp(x.loc[0,'market_time'])
    finally: p.unlink(missing_ok=True)

def test_snapshot_is_content_addressed(tmp_path):
    from nse_signal.data.nse.snapshot import snapshot_csv
    src=tmp_path/'pit.csv'
    pd.DataFrame([{'symbol':'ABC','date':'2026-09-25','signal_time':'2026-09-28T03:45:00Z','asof_time':'2026-09-28T03:45:00Z'}]).to_csv(src,index=False)
    a=snapshot_csv(src,tmp_path/'snap')
    b=snapshot_csv(src,tmp_path/'snap')
    assert a['snapshot_id']==b['snapshot_id']
    assert (tmp_path/'snap'/a['snapshot_id']/'manifest.json').exists()

def test_model_registry_requires_valid_lifecycle(tmp_path):
    from nse_signal.models.registry import ModelRegistry
    r=ModelRegistry(tmp_path/'registry.json'); r.register('m1','abc',{'auc':.6,'gate':{'pass':True}}); r.transition('m1','VALIDATED'); r.transition('m1','PAPER'); r.transition('m1','CHAMPION'); assert r.champion()['model_id']=='m1'
    try: r.transition('m1','REGISTERED'); assert False
    except ValueError: pass

def test_publication_requires_model_snapshot_and_session():
    from nse_signal.risk.publication import publication_gate
    r=publication_gate(probability=.9,factor_score=.9,model_ready=False,snapshot_ready=False,session_ok=False)
    assert r['publish'] is False
    assert {'model_champion_not_ready','dataset_snapshot_not_ready','invalid_market_session'}.issubset(r['reasons'])
