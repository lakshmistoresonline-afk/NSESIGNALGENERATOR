import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

def test_missing_ohlcv_columns_fail_cleanly():
    from nse_signal.data.quality import validate_ohlcv
    out=validate_ohlcv(pd.DataFrame({"open":[1.0],"close":[1.0]}))
    assert out["pass"] is False
    assert "high" in out["missing_columns"]

def test_unknown_calendar_year_fails_closed():
    from nse_signal.data.nse.session_calendar import is_trading_day
    try:
        is_trading_day("2012-01-02")
    except RuntimeError:
        return
    raise AssertionError("unknown NSE calendar year must fail closed")

def test_broad_pit_builder_does_not_require_nifty200(monkeypatch, tmp_path):
    # Static source-contract check: default universe is broad_nse.
    text=(Path(__file__).resolve().parents[1] / "scripts" / "build_pit_dataset.py").read_text()
    assert "choices=['broad_nse','nifty200']" in text
    assert "default='broad_nse'" in text

def test_panel_walk_forward_is_required_for_panel_inputs():
    from nse_signal.models.walk_forward import walk_forward
    x=pd.DataFrame({
        "timestamp":pd.date_range("2026-01-01",periods=20,tz="UTC").repeat(2),
        "symbol":["A","B"]*20, "close":1.0, "open":1.0, "high":1.1, "low":.9, "volume":100
    })
    try:
        walk_forward(x, min_train=5)
    except ValueError as e:
        assert "panel_walk_forward" in str(e)
    else:
        raise AssertionError("row-based walk_forward must reject panel data")

def test_production_signal_script_has_no_hardcoded_factor_floor():
    text=(Path(__file__).resolve().parents[1] / "scripts" / "generate_signal.py").read_text()
    assert "factor_score=.5" not in text
    assert "causal trailing momentum" in text


def test_conformal_classification_uses_class_conditional_pvalues():
    import numpy as np
    from nse_signal.research.robustness import conformal_classification
    y=np.array([0,0,0,1,1,1,0,1,0,1]*3)
    p=np.array([.2,.3,.25,.7,.8,.75,.35,.65,.4,.6]*3)
    out=conformal_classification(p,y,np.array([.05,.5,.95]),alpha=.1)
    assert {'p_value_0','p_value_1'}.issubset(out.columns)
    assert len(out)==3
    assert ((out[['p_value_0','p_value_1']] >= 0) & (out[['p_value_0','p_value_1']] <= 1)).all().all()


def test_production_artifact_contract_contains_frozen_threshold_and_conformal_v2():
    import inspect
    from nse_signal.models.production import ProductionArtifact
    fields=ProductionArtifact.__dataclass_fields__
    assert 'publication_threshold' in fields
    assert 'conformal_scores_0' in fields and 'conformal_scores_1' in fields
    assert fields['conformal_version'].default == 2
