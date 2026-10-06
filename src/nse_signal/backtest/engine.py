"""Economic backtesting with explicit next-bar entry and barrier-aware exits."""
from __future__ import annotations
import numpy as np
import pandas as pd
from ..research.metrics import performance_report


def backtest_oos(pred: pd.DataFrame, cost_bps=30, slippage_bps=10, threshold=.55, holding_bars=5, allow_short=True):
    """Economic backtest with next-session execution.

    Panel inputs are evaluated independently per symbol so a symbol can never
    consume another symbol's future bar. The pooled report is computed only
    after symbol-safe trade construction.
    """
    required={'open','close','p_up'}
    x=pred.copy()
    if not required.issubset(x.columns):
        if 'close' not in x.columns:
            raise ValueError("backtest requires close and p_up")
        x['open']=x['close']
    cost=(cost_bps+slippage_bps)/10000.0

    def _one(g, symbol=None):
        g=g.sort_values('timestamp').copy() if 'timestamp' in g.columns else g.sort_index().copy()
        g['side']=np.where(g.p_up>=threshold,1,np.where(allow_short & (g.p_up<=1-threshold),-1,0))
        rows=[]
        for i in range(len(g)-holding_bars-1):
            side=int(g.iloc[i].side)
            if side==0: continue
            entry_i=i+1; exit_i=i+1+holding_bars
            entry=float(g.iloc[entry_i].open); exitp=float(g.iloc[exit_i].close)
            gross=side*(exitp/entry-1.0)
            signal_time=g.iloc[i]['timestamp'] if 'timestamp' in g.columns else g.index[i]
            rows.append((signal_time, symbol, side, entry, exitp, gross, gross-cost))
        return rows

    rows=[]
    if {'timestamp','symbol'}.issubset(x.columns):
        for sym,g in x.groupby('symbol',sort=False):
            rows.extend(_one(g,sym))
    else:
        rows=_one(x)
    trades=pd.DataFrame(rows,columns=['signal_time','symbol','side','entry','exit','gross_return','net_return'])
    if not trades.empty:
        trades=trades.set_index('signal_time').sort_index()
    stats=performance_report(trades.net_return if not trades.empty else pd.Series(dtype=float), annualization=252, trials=1)
    stats.update({'trades':int(len(trades)),'round_trip_cost_bps':cost_bps,'slippage_bps':slippage_bps,'holding_bars':holding_bars})
    return trades,stats


def backtest_triple_barrier(df: pd.DataFrame, predictions: pd.DataFrame, threshold=.55, pt_atr=2.0, sl_atr=1.0, max_holding=5, cost_bps=30, slippage_bps=10):
    """Event-driven barrier backtest; panel rows are processed symbol-by-symbol."""
    from ..research.labels import triple_barrier_labels
    p=predictions.copy()
    cost=(cost_bps+slippage_bps)/10000.0
    rows=[]

    def _one(gdf, gp, symbol=None):
        gdf=gdf.sort_values('timestamp' if 'timestamp' in gdf.columns else gdf.index.name or gdf.index).copy()
        if {'timestamp','symbol'}.issubset(gp.columns):
            gp=gp.sort_values('timestamp').copy()
            gp=gp[gp['symbol'].eq(symbol)]
        else:
            gp=gp.sort_index()
        common=gp.index.intersection(gdf.index)
        gp=gp.loc[common]; gdf=gdf.loc[common]
        side=np.where(gp.p_up>=threshold,1,np.where(gp.p_up<=1-threshold,-1,0))
        labels=triple_barrier_labels(gdf,horizon=max_holding,pt_atr=pt_atr,sl_atr=sl_atr,side=pd.Series(side,index=gp.index))
        for idx,row in labels.iterrows():
            if pd.isna(row.tb_label) or side[list(labels.index).index(idx)]==0:
                continue
            gross=float(row.tb_return)
            rows.append((idx,symbol,side[list(labels.index).index(idx)],gross,gross-cost,row.tb_event))

    if {'timestamp','symbol'}.issubset(p.columns) and {'timestamp','symbol'}.issubset(df.columns):
        for sym,gp in p.groupby('symbol',sort=False):
            _one(df[df.symbol.eq(sym)],gp,sym)
    else:
        _one(df,p)

    out=pd.DataFrame(rows,columns=['signal_time','symbol','side','gross_return','net_return','tb_event'])
    if not out.empty: out=out.set_index('signal_time').sort_index()
    stats=performance_report(out.net_return if not out.empty else pd.Series(dtype=float), trials=1)
    stats.update({'trades':int(len(out)),'pt_atr':pt_atr,'sl_atr':sl_atr,'max_holding':max_holding,'round_trip_cost_bps':cost_bps,'slippage_bps':slippage_bps})
    return out,stats

