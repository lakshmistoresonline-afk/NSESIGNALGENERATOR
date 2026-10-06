#!/usr/bin/env python3
"""Run non-market accuracy-control diagnostics on synthetic data."""
from pathlib import Path
import json, sys
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from nse_signal.data.market import synthetic_symbol
from nse_signal.features.build import make_features
from nse_signal.models.walk_forward import walk_forward
from nse_signal.research.robustness import combinatorial_purged_splits, population_stability_index, feature_stability_by_fold
from nse_signal.research.thresholds import choose_threshold
from nse_signal.research.regime_eval import regime_report

raw=synthetic_symbol(n=700)
features=make_features(raw)
oos=walk_forward(features,min_train=300,step=20,horizon=5,embargo=10,max_features=80)
p=oos.predictions
threshold=choose_threshold(p.target.to_numpy(),p.p_up.to_numpy())
splits=list(combinatorial_purged_splits(len(features),6,2,10,10))
report={
 'synthetic_only': True,
 'warning':'Diagnostics only; no market-alpha claim.',
 'oos_metrics':oos.metrics,
 'cpcv_splits':len(splits),
 'validation_threshold':threshold,
 'regime_report':regime_report(p),
 'self_psi':population_stability_index(p.p_up,p.p_up),
 'feature_selection_stability': 'available from walk-forward fold history',
 'next_open_label_contract': True,
}
Path('data/processed').mkdir(exist_ok=True)
Path('data/processed/accuracy_controls_report.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
print(json.dumps(report,indent=2,default=str))
