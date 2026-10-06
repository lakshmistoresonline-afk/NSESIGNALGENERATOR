from nse_signal.risk.publication import publication_gate
from nse_signal.signals.engine import SignalEngine

def test_publication_gate_enforces_pit_and_restrictions():
    r = publication_gate(probability=.9, factor_score=.9, expected_value=1, pit_ready=False)
    assert r['publish'] is False and 'pit_not_ready' in r['reasons']
    r = publication_gate(probability=.9, factor_score=.9, expected_value=1, restricted=True)
    assert r['publish'] is False and 'security_restricted' in r['reasons']
    r = publication_gate(probability=.9, factor_score=.9, expected_value=1, impact_cost_bps=101, max_impact_cost_bps=100)
    assert r['publish'] is False and 'impact_cost_too_high' in r['reasons']

def test_signal_engine_requires_pit_readiness():
    e=SignalEngine()
    assert e.generate('ABC', .9, .9, price=100, atr=2, pit_ready=False) is None
    assert e.generate('ABC', .9, .9, price=100, atr=2, membership_ready=False) is None


def test_dashboard_artifact_rejects_execution_enabled(tmp_path, monkeypatch):
    import json
    import server.api as api
    target = api.ROOT / 'data' / 'processed' / 'published_signals.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    original = target.read_text(encoding='utf-8') if target.exists() else None
    try:
        target.write_text(json.dumps([{'symbol':'ABC','signal_only':True,'real_trading':True}]), encoding='utf-8')
        from fastapi.testclient import TestClient
        response = TestClient(api.app).get('/api/dashboard/signals')
        assert response.status_code == 500
    finally:
        if original is None:
            target.unlink(missing_ok=True)
        else:
            target.write_text(original, encoding='utf-8')
