"""Meta-labeling utilities applied only to genuinely OOS primary predictions."""
from __future__ import annotations
import numpy as np
import pandas as pd
from ..research.labels import triple_barrier_labels


def build_meta_labels(df: pd.DataFrame, oos_predictions: pd.DataFrame, probability_threshold=.55, pt_atr=2.0, sl_atr=1.0, horizon=5):
    p=oos_predictions.copy().sort_index()
    side=np.where(p.p_up>=probability_threshold,1,np.where(p.p_up<=1-probability_threshold,-1,0))
    side_s=pd.Series(side,index=p.index)
    tb=triple_barrier_labels(df.reindex(p.index),horizon=horizon,pt_atr=pt_atr,sl_atr=sl_atr,side=side_s)
    tb=tb.rename(columns={'tb_label':'tb_label_calc','tb_return':'tb_return_calc','tb_event':'tb_event_calc','tb_entry_price':'tb_entry_price_calc'})
    out=p.join(tb,how='left')
    for a,b in [('tb_label_calc','tb_label'),('tb_return_calc','tb_return'),('tb_event_calc','tb_event'),('tb_entry_price_calc','tb_entry_price')]:
        if b not in out and a in out: out[b]=out[a]
    out['primary_side']=side_s
    out['meta_target']=((out.tb_label==1)&(out.primary_side!=0)).astype(int)
    out['meta_confidence']=np.maximum(out.p_up,1-out.p_up)
    return out
