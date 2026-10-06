"""Leakage-safe execution labels for multi-symbol panels."""
from __future__ import annotations
import numpy as np
import pandas as pd
from .labels import triple_barrier_labels


def execution_consistent_target_panel(df: pd.DataFrame, *, symbol_col='symbol', time_col='timestamp', horizon=5, pt_atr=2.0, sl_atr=1.0, atr_col='atr_14', timeout_policy='exclude') -> pd.DataFrame:
    """Apply the next-open triple-barrier contract independently per symbol."""
    req={symbol_col,time_col,'open','high','low','close',atr_col}
    missing=req-set(df.columns)
    if missing: raise ValueError(f"missing panel label columns: {sorted(missing)}")
    parts=[]
    for symbol, g in df.groupby(symbol_col, sort=False):
        g=g.sort_values(time_col).copy()
        tb=triple_barrier_labels(g,horizon=horizon,pt_atr=pt_atr,sl_atr=sl_atr,atr_col=atr_col)
        g['tb_label']=tb.tb_label; g['tb_return']=tb.tb_return; g['tb_event']=tb.tb_event; g['tb_entry_price']=tb.tb_entry_price
        # Event end is the last information needed to determine the label.
        g['event_end_time']=g[time_col].shift(-(horizon+1))
        # For an early barrier hit, event_end_time can be refined from the event
        # string only if a future bar index is recorded; the conservative horizon
        # endpoint is retained for purging.
        valid=g.tb_label.isin([-1.0,1.0])
        g['target']=np.where(valid,(g.tb_label>0).astype(float),np.nan)
        if timeout_policy == 'directional':
            timeout=g.tb_label.eq(0) & g.tb_return.notna()
            g['target']=np.where(timeout,(g.tb_return>0).astype(float),g['target'])
        elif timeout_policy != 'exclude':
            raise ValueError('timeout_policy must be exclude or directional')
        g['future_return']=g.tb_return
        parts.append(g)
    return pd.concat(parts).sort_values([time_col,symbol_col])
