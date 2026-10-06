#!/usr/bin/env python3
"""Offline accuracy/research audit. Uses synthetic data only; it is not a performance claim."""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from nse_signal.data.market import synthetic_symbol
from nse_signal.data.quality import validate_ohlcv
from nse_signal.features.build import make_features, FEATURES
from nse_signal.models.walk_forward import walk_forward
from nse_signal.backtest.engine import backtest_oos, backtest_triple_barrier
from nse_signal.research.meta import build_meta_labels
from nse_signal.research.validation import combinatorial_purged_splits

raw=synthetic_symbol(n=700)
quality=validate_ohlcv(raw)
features=make_features(raw)
oos=walk_forward(features,min_train=300,step=20,horizon=5,embargo=10,max_features=80)
trades,bt=backtest_oos(oos.predictions,threshold=.60,holding_bars=5)
tb,tb_stats=backtest_triple_barrier(features,oos.predictions,threshold=.60)
meta=build_meta_labels(features,oos.predictions,probability_threshold=.60,horizon=5)
cpcv=combinatorial_purged_splits(len(features),n_groups=6,test_groups=2,purge_bars=10,embargo_bars=10)
report={
  'synthetic_only': True,
  'warning': 'Synthetic results are validation diagnostics, not evidence of market alpha.',
  'data_quality': quality,
  'candidate_features': len(FEATURES),
  'generated_columns': len(features.columns),
  'oos_metrics': oos.metrics,
  'fixed_horizon_backtest': bt,
  'triple_barrier_backtest': tb_stats,
  'meta_label_rows': len(meta),
  'meta_positive_rate': float(meta.meta_target.mean()),
  'cpcv_paths': len(cpcv),
  'signal_only': True,
  'real_trading': False,
}
print(json.dumps(report,indent=2,default=str))
Path('data/processed/accuracy_audit_report.json').parent.mkdir(parents=True,exist_ok=True)
Path('data/processed/accuracy_audit_report.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
