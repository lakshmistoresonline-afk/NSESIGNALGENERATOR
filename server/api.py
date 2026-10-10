from pathlib import Path
import json
import os
import sys
from typing import Optional
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from fastapi import FastAPI, HTTPException, Header, Depends, Security
from fastapi.responses import FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from nse_signal.data.market import synthetic_symbol
from nse_signal.features.build import make_features
from nse_signal.models.walk_forward import walk_forward
from nse_signal.backtest.engine import backtest_oos
from nse_signal.research.factors import factor_snapshot
from nse_signal.signals.engine import SignalEngine
from nse_signal.utils.config import load_config
from nse_signal.data.providers.catalog import get_provider_catalog
from nse_signal.data.providers.registry import build_registry

ROOT = Path(__file__).resolve().parents[1]
PIT_ROOT = ROOT / 'data' / 'processed' / 'nse_pit'
MANIFEST = ROOT / 'data' / 'raw' / 'nse' / 'manifest.jsonl'

app = FastAPI(title='NSE Signal Provider API', version='3.8.0')
CONFIG = load_config()
NSE_CFG = CONFIG.get('nse_data_integration', {})
PUBLICATION_CFG = CONFIG.get('publication', {})
origins = [x.strip() for x in os.getenv('NSE_DASHBOARD_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',') if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=['GET', 'POST'],
    allow_headers=['Content-Type'],
)

class SignalRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=30)
    probability_up: float = Field(ge=0, le=1)
    factor_score: float = Field(default=0.5, ge=0, le=1)
    threshold: float = Field(default=0.55, ge=0.5, le=0.99)
    price: Optional[float] = Field(default=None, gt=0)
    atr_pct: Optional[float] = Field(default=None, gt=0)
    atr: Optional[float] = Field(default=None, gt=0)
    source: str = Field(default='research_only', min_length=1, max_length=80)

class ResearchRequest(BaseModel):
    symbol: str = Field(default='RELIANCE.NS', min_length=1, max_length=30)
    rows: int = Field(default=700, ge=300, le=5000)

REQUIRED_LAYERS = list(NSE_CFG.get('production_required_layers', [
    'cash', 'derivatives', 'security_master', 'delivery', 'impact_cost',
    'breadth', 'india_vix', 'surveillance', 'price_bands', 'short_selling'
]))


def _csv_rows(name: str) -> int:
    p = PIT_ROOT / f'{name}.csv'
    if not p.exists():
        return 0
    try:
        import pandas as pd
        return int(pd.read_csv(p, usecols=[0]).shape[0])
    except Exception:
        return 0


def _latest_asof() -> Optional[str]:
    import pandas as pd
    latest = None
    if not PIT_ROOT.exists():
        return None
    for p in PIT_ROOT.glob('*.csv'):
        try:
            cols = pd.read_csv(p, nrows=0).columns
            if 'asof_time' not in cols:
                continue
            x = pd.read_csv(p, usecols=['asof_time'])
            if x.empty:
                continue
            v = pd.to_datetime(x['asof_time'], utc=True, errors='coerce').max()
            if pd.notna(v) and (latest is None or v > latest):
                latest = v
        except Exception:
            continue
    return latest.isoformat() if latest is not None else None


def _manifest_count() -> int:
    if not MANIFEST.exists():
        return 0
    try:
        return sum(1 for line in MANIFEST.read_text(encoding='utf-8').splitlines() if line.strip())
    except Exception:
        return 0


def dashboard_overview():
    layers = {}
    rows = {}
    from nse_signal.data.db import table_row_count
    for layer in REQUIRED_LAYERS:
        db_tbl = {
            'cash': 'cash_daily',
            'index': 'index_close',
            'derivatives': 'fo_bhavcopy',
            'security_master': 'security_master',
            'delivery': 'delivery',
            'impact_cost': 'impact_cost',
            'breadth': 'breadth',
            'india_vix': 'india_vix',
            'surveillance': 'surveillance',
            'price_bands': 'price_bands',
            'short_selling': 'short_selling',
            'corporate_adjustments': 'corporate_adjustments',
            'corporate_events': 'corporate_events'
        }.get(layer, layer)
        cnt = table_row_count(db_tbl)
        layers[layer] = cnt > 0
        rows[layer] = cnt
    issues = [f'{k} dataset missing' for k, ok in layers.items() if not ok]
    membership = ROOT / 'data' / 'reference' / 'nifty200_membership.csv'
    membership_ready = False
    try:
        import pandas as pd
        from nse_signal.data.nse.membership import load_membership, assert_no_overlap
        if membership.exists():
            m = load_membership(str(membership))
            assert_no_overlap(m)
            membership_ready = len(m) > 0
    except Exception:
        membership_ready = False
    universe_mode = str(NSE_CFG.get('universe_mode', 'broad_nse')).lower()
    if universe_mode == 'nifty200' and bool(NSE_CFG.get('require_effective_dated_membership', True)) and not membership_ready:
        issues.append('effective-dated NIFTY 200 membership missing or empty')
    manifest_present = MANIFEST.exists() and _manifest_count() > 0
    if bool(NSE_CFG.get('checksum_manifest_required', True)) and not manifest_present:
        issues.append('NSE checksum/provenance manifest missing or empty')
    max_impact = float(PUBLICATION_CFG.get('max_impact_cost_bps', 100.0))
    return {
        'status': 'ok' if not issues else 'blocked', 'version': app.version, 'signal_only': True, 'real_trading': False,
        'pit': {'ready': not issues, 'required_layers': layers, 'rows': rows, 'last_asof': _latest_asof(), 'issues': issues, 'membership_ready': membership_ready},
        'provenance': {'manifest_records': _manifest_count(), 'manifest_present': manifest_present},
        'publication': {'fail_closed': bool(PUBLICATION_CFG.get('fail_closed', True)), 'max_impact_cost_bps': max_impact, 'reject_restricted_securities': bool(PUBLICATION_CFG.get('reject_restricted_securities', True))},
        'signals': {'count': 0, 'items': []},
        'warnings': [] if not issues else ['Production publication remains blocked until every required PIT layer, universe, and provenance requirement is satisfied.'],
    }

@app.get('/', include_in_schema=False)
def root_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url='/dashboard')

@app.get('/health')
@app.get('/api/health')
def health():
    return {'status': 'ok', 'version': app.version, 'product': 'NSE signal provider', 'signal_only': True, 'real_trading': False}

@app.get('/favicon.ico', include_in_schema=False)
def favicon():
    return Response(status_code=204)

@app.get('/dashboard', include_in_schema=False)
@app.get('/dashboard/', include_in_schema=False)
def dashboard_page():
    return FileResponse(ROOT / 'frontend' / 'index.html')

@app.get('/dashboard/styles.css', include_in_schema=False)
def dashboard_css():
    return FileResponse(ROOT / 'frontend' / 'styles.css', media_type='text/css')

@app.get('/dashboard/app.js', include_in_schema=False)
def dashboard_js():
    return FileResponse(ROOT / 'frontend' / 'app.js', media_type='application/javascript')

@app.get('/api/dashboard/overview')
def dashboard():
    return dashboard_overview()

@app.get('/api/dashboard/tickers')
def market_tickers():
    from nse_signal.data.db import get_connection
    import pandas as pd
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT symbol, close, date FROM index_close ORDER BY date DESC LIMIT 10", conn)
        if df.empty:
            return {"tickers": []}
        tickers = []
        for sym, grp in df.groupby('symbol'):
            row = grp.iloc[0]
            tickers.append({"symbol": str(sym), "price": float(row['close']), "date": str(row['date'])})
        return {"tickers": tickers}
    except Exception:
        return {"tickers": []}
    finally:
        conn.close()

@app.get('/api/dashboard/signals')
def published_signals():
    from nse_signal.data.production_gate import evaluate_production_gate
    from nse_signal.signals.contract import CanonicalSignal

    candidates = [ROOT / 'data' / 'processed' / 'published_signals.json', ROOT / 'reports' / 'published_signals.json']
    for p in candidates:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding='utf-8'))
                if isinstance(data, dict):
                    if data.get('real_trading', False) is True or data.get('signal_only', True) is not True:
                        raise ValueError('published signal artifact violates signal-only safety boundary')
                    items = data.get('items', [])
                elif isinstance(data, list):
                    items = data
                else:
                    items = []

                for item in items:
                    if isinstance(item, dict):
                        if item.get('real_trading', False) is True or item.get('signal_only', True) is not True:
                            raise ValueError('published signal artifact violates signal-only safety boundary')
            except HTTPException:
                raise
            except Exception as exc:
                raise HTTPException(500, f'Invalid published signal artifact: {p.name}: {exc}') from exc

    gate = evaluate_production_gate()
    is_eligible = gate.get('eligible', False)
    blockers = gate.get('blocking_reasons', [])

    if not is_eligible:
        return {
            'signal_only': True,
            'real_trading': False,
            'live_items': [],
            'historical_items': [],
            'items': [],
            'publication_gate': 'BLOCKED',
            'blockers': blockers
        }

    for p in candidates:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding='utf-8'))
                items = data if isinstance(data, list) else data.get('items', [])
                live_items = data.get('live_items', []) if isinstance(data, dict) else []
                historical_items = data.get('historical_items', []) if isinstance(data, dict) else []
                if not isinstance(items, list):
                    raise ValueError('published signal artifact must contain a list of items')
                safe = []
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    if item.get('real_trading', False) is True or item.get('signal_only', True) is not True:
                        raise ValueError('published signal artifact violates signal-only safety boundary')
                    try:
                        sig = CanonicalSignal.from_dict(item)
                        valid, _ = sig.validate()
                        if not valid:
                            continue
                    except Exception:
                        continue
                    safe.append(item)
                if not live_items and not historical_items:
                    live_items = [it for it in safe if it.get('generation_mode') == 'LIVE']
                    historical_items = [it for it in safe if it.get('generation_mode') == 'HISTORICAL']
                return {
                    'signal_only': True,
                    'real_trading': False,
                    'live_items': live_items,
                    'historical_items': historical_items,
                    'items': safe,
                    'publication_gate': 'PASS'
                }
            except Exception as exc:
                raise HTTPException(500, f'Invalid published signal artifact: {p.name}: {exc}') from exc
    return {'signal_only': True, 'real_trading': False, 'live_items': [], 'historical_items': [], 'items': [], 'publication_gate': 'BLOCKED'}

@app.post('/signal')
@app.post('/api/signal')
def signal(req: SignalRequest):
    # This endpoint is explicitly a research evaluator, not a production prediction source.
    if req.source != 'research_only':
        raise HTTPException(403, 'Production signal publication must originate from the validated OOS/PIT pipeline')
    engine = SignalEngine(real_trading=False)
    result = engine.generate(req.symbol.upper(), req.probability_up, req.factor_score, req.threshold, price=req.price, atr_pct=req.atr_pct, atr=req.atr)
    return {'signal': None if result is None else result.to_dict(), 'real_trading': False, 'mode': 'research_only'}

@app.post('/research')
@app.post('/api/research')
def research(req: ResearchRequest):
    if os.getenv('ALLOW_SYNTHETIC_RESEARCH', 'false').lower() != 'true':
        raise HTTPException(403, 'Synthetic research generation is disabled in production by default. Set ALLOW_SYNTHETIC_RESEARCH=true for isolated demo mode.')
    try:
        raw = synthetic_symbol(symbol=req.symbol.upper(), n=req.rows)
        features = make_features(raw)
        oos = walk_forward(features, min_train=250, horizon=5)
        _, stats = backtest_oos(oos.predictions)
        factors = factor_snapshot(raw)
        latest = oos.predictions.iloc[-1]
        return {'symbol': req.symbol.upper(), 'latest_probability_up': float(latest.p_up), 'factor_snapshot': factors, 'oos_metrics': oos.metrics, 'backtest': stats, 'signal_only': True, 'real_trading': False, 'data_mode': 'synthetic_demo_not_market_data'}
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc

@app.get('/api/providers')
def providers():
    return {'providers': get_provider_catalog(), 'secondary_enabled': os.getenv('ALLOW_SECONDARY_PROVIDER','false').lower() == 'true', 'yahoo_automation': os.getenv('ALLOW_YAHOO_AUTOMATION','false').lower() == 'true'}

@app.get('/api/provider-health')
def provider_health():
    reg = build_registry()
    return {'providers': [{'name': n, 'configured': True} for n in reg.names()], 'signal_only': True, 'real_trading': False}

@app.get('/api/readiness')
def readiness():
    ov=dashboard_overview()
    from nse_signal.data.nse.data_governance import data_governance_status
    dg=data_governance_status(ROOT/'data'/'reference'/'authoritative_pit_data_gap_register.json')
    reasons=list(ov['pit']['issues'])
    if not dg['production_eligible']:
        reasons.append(f"{dg['blocker_count']} authoritative PIT datasets are not supplied/licensed")
    return {'ready':bool(ov['pit']['ready']) and dg['production_eligible'],'signal_only':True,'real_trading':False,'reasons':reasons,'data_governance':dg}

@app.get('/api/data-health')
def data_health():
    ov=dashboard_overview()
    from nse_signal.data.nse.data_governance import data_governance_status
    dg=data_governance_status(ROOT/'data'/'reference'/'authoritative_pit_data_gap_register.json')
    return {'status':'ok' if ov['pit']['ready'] and dg['production_eligible'] else 'blocked','pit':ov['pit'],'provenance':ov['provenance'],'data_governance':dg}

@app.get('/api/data-governance')
def data_governance():
    from nse_signal.data.nse.data_governance import data_governance_status
    return data_governance_status(ROOT/'data'/'reference'/'authoritative_pit_data_gap_register.json')

@app.get('/api/model-health')
def model_health():
    try:
        from nse_signal.models.registry import ModelRegistry
        c=ModelRegistry(str(ROOT/'data'/'processed'/'model_registry.json')).champion()
        return {'status':'ok' if c else 'blocked','champion':c,'reason':None if c else 'no_champion'}
    except Exception as exc:
        return {'status':'blocked','champion':None,'reason':str(exc)}

@app.get('/api/publication-health')
def publication_health():
    ov=dashboard_overview(); mh=model_health()
    from nse_signal.data.nse.data_governance import data_governance_status
    dg=data_governance_status(ROOT/'data'/'reference'/'authoritative_pit_data_gap_register.json')
    ready=bool(ov['pit']['ready']) and bool(mh.get('champion')) and dg['production_eligible']
    return {'status':'ok' if ready else 'blocked','pit_ready':ov['pit']['ready'],'model_ready':bool(mh.get('champion')),'data_governance_ready':dg['production_eligible'],'signal_only':True,'real_trading':False}

@app.get('/api/v1/health')
def v1_health():
    from datetime import datetime, timezone
    return {
        'status': 'ok',
        'version': app.version,
        'product': 'NSE Signal Provider',
        'signal_only': True,
        'real_trading': False,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

_firebase_admin_initialized = False

def init_firebase_admin():
    global _firebase_admin_initialized
    if _firebase_admin_initialized:
        return
    env = os.getenv("NSE_ENV", "production").lower()
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    try:
        import firebase_admin
        from firebase_admin import credentials
        if cred_path and Path(cred_path).exists():
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            _firebase_admin_initialized = True
        else:
            firebase_admin.initialize_app()
            _firebase_admin_initialized = True
    except Exception as exc:
        if env == "production" and os.getenv("NSE_TEST_MODE", "false").lower() != "true":
            raise RuntimeError(f"Production startup failed closed: Firebase Admin SDK initialization failed: {exc}")

def verify_auth_token(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not Authenticated: Missing or invalid token format")
    token = authorization.split(" ")[1]

    test_mode = os.getenv("NSE_TEST_MODE", "false").lower() == "true"
    if test_mode:
        if token == "dev-analyst-token" or token.startswith("dev-analyst"):
            return {"uid": "test-analyst-uid", "role": "analyst"}
        if token == "dev-non-analyst-token":
            raise HTTPException(status_code=403, detail="Not Authorized: User does not have analyst role")

    try:
        init_firebase_admin()
        from firebase_admin import auth
        decoded_token = auth.verify_id_token(token)
        role = decoded_token.get("role") or decoded_token.get("claims", {}).get("role")
        if role != "analyst":
            raise HTTPException(status_code=403, detail="Not Authorized: User does not have analyst role")
        return decoded_token
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Not Authenticated: Invalid or expired Firebase ID token: {exc}") from exc

@app.get('/api/v1/signals')
def v1_signals(universe: Optional[str] = None, signal_filter: Optional[str] = None, auth = Depends(verify_auth_token)):
    ov = dashboard_overview()
    from nse_signal.data.nse.data_governance import data_governance_status
    dg = data_governance_status(ROOT / 'data' / 'reference' / 'authoritative_pit_data_gap_register.json')
    production_ready = bool(ov['pit']['ready']) and dg['production_eligible']

    items = []
    if production_ready:
        candidates = [ROOT / 'data' / 'processed' / 'published_signals.json', ROOT / 'reports' / 'published_signals.json']
        for p in candidates:
            if p.exists():
                try:
                    data = json.loads(p.read_text(encoding='utf-8'))
                    raw_items = data if isinstance(data, list) else data.get('items', [])
                    if isinstance(raw_items, list):
                        for item in raw_items:
                            if isinstance(item, dict) and item.get('signal_only', True) is True and item.get('real_trading', False) is False:
                                items.append(item)
                    break
                except Exception:
                    pass

    if universe:
        items = [it for it in items if str(it.get('universe', 'NSE EQ')).upper() == universe.upper()]
    if signal_filter:
        items = [it for it in items if str(it.get('signal', '')).upper() == signal_filter.upper()]
    return {"signal_only": True, "real_trading": False, "count": len(items), "items": items}

@app.get('/api/v1/signals/{symbol}')
def v1_signal_symbol(symbol: str, auth = Depends(verify_auth_token)):
    res = v1_signals(auth=auth)
    match = next((it for it in res['items'] if it.get('symbol', '').upper() == symbol.upper()), None)
    if not match:
        return {
            "symbol": symbol.upper(),
            "exchange": "NSE",
            "signal": "NO_SIGNAL",
            "confidence": None,
            "price": None,
            "signal_time": None,
            "regime": None,
            "publication_status": "NOT_AVAILABLE",
            "conformal_status": None,
            "model_dispersion": None,
            "signal_only": True,
            "real_trading": False,
            "reason": "SYMBOL_NOT_PUBLISHED"
        }
    return match

@app.get('/api/v1/market-status')
def v1_market_status(auth = Depends(verify_auth_token)):
    from datetime import datetime, timezone
    from nse_signal.data.nse.session_calendar import classify
    now = datetime.now(timezone.utc)
    status = classify(now)
    return {
        "exchange": "NSE",
        "market_status": status,
        "timestamp": now.isoformat(),
        "timezone": "Asia/Kolkata",
        "signal_only": True,
        "real_trading": False
    }

@app.get('/api/v1/universe')
def v1_universe(auth = Depends(verify_auth_token)):
    return {
        "signal_only": True,
        "real_trading": False,
        "universes": [
            {"name": "NSE EQ", "count": 1850, "description": "Broad NSE equity universe"},
            {"name": "NIFTY 50", "count": 50, "description": "Benchmark large-cap index"},
            {"name": "NIFTY 100", "count": 100, "description": "Large-cap index"},
            {"name": "NIFTY 200", "count": 200, "description": "Benchmark/research universe"},
            {"name": "F&O", "count": 182, "description": "Futures & options enabled equities"}
        ]
    }

@app.get('/api/v1/signal/{symbol}/details')
def v1_signal_details(symbol: str, auth = Depends(verify_auth_token)):
    res = v1_signals(auth=auth)
    match = next((it for it in res['items'] if it.get('symbol', '').upper() == symbol.upper()), None)
    if not match:
        return {
            "symbol": symbol.upper(),
            "exchange": "NSE",
            "signal": "NO_SIGNAL",
            "confidence": None,
            "price": None,
            "signal_time": None,
            "regime": None,
            "publication_status": "NOT_AVAILABLE",
            "conformal_status": None,
            "model_dispersion": None,
            "model_agreement": None,
            "data_freshness": "UNAVAILABLE",
            "pit_provenance_verified": None,
            "conformal_calibration_status": None,
            "risk_gates": [],
            "publication_gate": "BLOCKED",
            "signal_only": True,
            "real_trading": False,
            "reason": "SYMBOL_NOT_PUBLISHED"
        }
    detail = dict(match)
    detail.setdefault("model_agreement", match.get("model_agreement"))
    detail.setdefault("data_freshness", match.get("data_freshness", "AVAILABLE"))
    detail.setdefault("pit_provenance_verified", match.get("pit_provenance_verified"))
    detail.setdefault("conformal_calibration_status", match.get("conformal_status"))
    detail.setdefault("risk_gates", match.get("risk_gates", []))
    detail.setdefault("publication_gate", match.get("publication_status"))
    return detail
