"""Leakage-safe event labels for financial ML research."""
from __future__ import annotations
import numpy as np
import pandas as pd


def triple_barrier_labels(
    df: pd.DataFrame,
    horizon: int = 5,
    pt_atr: float = 2.0,
    sl_atr: float = 1.0,
    atr_col: str = "atr_14",
    side: pd.Series | None = None,
    entry: str = "next_open",
) -> pd.DataFrame:
    """Create execution-consistent triple-barrier labels.

    A signal is formed at close[t]. The default entry is open[t+1], so the
    label and economic backtest share the same execution contract. ATR is
    frozen at signal time t. Barrier monitoring begins at the entry bar and
    continues through the configured horizon. If both barriers are touched
    within one OHLC bar, stop-first is used conservatively because intrabar
    ordering is unknown.
    """
    if horizon < 1 or pt_atr <= 0 or sl_atr <= 0:
        raise ValueError("horizon and barrier multipliers must be positive")
    if entry not in {"next_open", "next_close"}:
        raise ValueError("entry must be next_open or next_close")
    req = {"open", "high", "low", "close", atr_col}
    missing = req - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    x = df.copy()
    if side is None:
        s = pd.Series(1.0, index=x.index)
    else:
        s = side.reindex(x.index).fillna(0.0).astype(float)
    labels = pd.Series(np.nan, index=x.index, dtype=float)
    returns = pd.Series(np.nan, index=x.index, dtype=float)
    hit = pd.Series("", index=x.index, dtype=object)
    entry_prices = pd.Series(np.nan, index=x.index, dtype=float)
    for i in range(len(x) - horizon - 1):
        atr = float(x.iloc[i][atr_col]) if np.isfinite(x.iloc[i][atr_col]) else np.nan
        if not np.isfinite(atr) or atr <= 0 or s.iloc[i] == 0:
            continue
        entry_i = i + 1
        entry_price = float(x.iloc[entry_i].open if entry == "next_open" else x.iloc[entry_i].close)
        direction = 1.0 if s.iloc[i] > 0 else -1.0
        pt = entry_price + direction * pt_atr * atr
        sl = entry_price - direction * sl_atr * atr
        chosen = 0
        chosen_return = direction * (float(x.iloc[min(i + 1 + horizon, len(x)-1)].close) / entry_price - 1.0)
        chosen_hit = "time"
        # Horizon is measured from the actual entry bar: entry=t+1,
        # therefore the final monitored/timeout bar is t+1+horizon.
        last_j = min(i + 1 + horizon, len(x) - 1)
        for j in range(entry_i, last_j + 1):
            bar_open=float(x.iloc[j].open); hi=float(x.iloc[j].high); lo=float(x.iloc[j].low)
            # Overnight/gap-through events are executed at the actual next-bar
            # open, not at an impossible barrier price.
            # If a later bar opens through a barrier, the tradable exit is the
            # actual open. On the entry bar this is also the execution price,
            # so the branch remains explicit for auditability.
            if direction > 0 and bar_open >= pt:
                chosen, chosen_hit, chosen_return = 1, "profit_gap_at_entry" if j == entry_i else "profit_gap", direction*(bar_open/entry_price-1.0)
                break
            if direction > 0 and bar_open <= sl:
                chosen, chosen_hit, chosen_return = -1, "stop_gap_at_entry" if j == entry_i else "stop_gap", direction*(bar_open/entry_price-1.0)
                break
            if direction < 0 and bar_open <= pt:
                chosen, chosen_hit, chosen_return = 1, "profit_gap_at_entry" if j == entry_i else "profit_gap", direction*(bar_open/entry_price-1.0)
                break
            if direction < 0 and bar_open >= sl:
                chosen, chosen_hit, chosen_return = -1, "stop_gap_at_entry" if j == entry_i else "stop_gap", direction*(bar_open/entry_price-1.0)
                break
            if direction > 0:
                pt_hit, sl_hit = hi >= pt, lo <= sl
            else:
                pt_hit, sl_hit = lo <= pt, hi >= sl
            if pt_hit and sl_hit:
                chosen, chosen_hit, chosen_return = -1, "both_same_bar_stop_first", direction * (sl / entry_price - 1.0)
                break
            if pt_hit:
                chosen, chosen_hit, chosen_return = 1, "profit", direction * (pt / entry_price - 1.0)
                break
            if sl_hit:
                chosen, chosen_hit, chosen_return = -1, "stop", direction * (sl / entry_price - 1.0)
                break
        labels.iloc[i] = chosen
        returns.iloc[i] = chosen_return
        hit.iloc[i] = chosen_hit
        entry_prices.iloc[i] = entry_price
    return pd.DataFrame({"tb_label": labels, "tb_return": returns, "tb_event": hit, "tb_entry_price": entry_prices}, index=x.index)


def directional_label(df: pd.DataFrame, horizon: int = 5, threshold: float = 0.0) -> pd.DataFrame:
    """Simple directional benchmark label.

    Panel frames are shifted within symbol; a single global shift is unsafe
    because adjacent rows can belong to different NSE securities.
    """
    if int(horizon) < 1:
        raise ValueError('horizon must be >= 1')
    if 'symbol' in df.columns:
        order=df.sort_values(['symbol'] + (['timestamp'] if 'timestamp' in df.columns else [])).copy()
        r=order.groupby('symbol',sort=False)['close'].shift(-int(horizon))/order['close']-1.0
        target=(r>threshold).astype(float).where(r.notna())
        return pd.DataFrame({'future_return':r,'target':target},index=order.index).reindex(df.index)
    r=df.close.shift(-int(horizon))/df.close-1.0
    return pd.DataFrame({'future_return':r,'target':(r>threshold).astype(float).where(r.notna())},index=df.index)


def execution_consistent_target(df: pd.DataFrame, horizon: int = 5, pt_atr: float = 2.0,
                                sl_atr: float = 1.0, atr_col: str = "atr_14",
                                timeout_policy: str = "exclude") -> pd.DataFrame:
    """Binary training target aligned to the production next-open economic contract.

    Profit-barrier events are class 1, stop-barrier events are class 0. Timeout
    events are excluded rather than being silently treated as wins/losses.
    """
    if timeout_policy not in {"exclude", "directional"}:
        raise ValueError("timeout_policy must be exclude or directional")
    tb = triple_barrier_labels(df, horizon=horizon, pt_atr=pt_atr, sl_atr=sl_atr, atr_col=atr_col)
    out = df.copy()
    out["tb_label"] = tb.tb_label
    out["tb_return"] = tb.tb_return
    out["tb_event"] = tb.tb_event
    out["tb_entry_price"] = tb.tb_entry_price
    valid = out.tb_label.isin([-1.0, 1.0])
    target = np.where(valid, (out.tb_label > 0).astype(float), np.nan)
    if timeout_policy == "directional":
        timeout = out.tb_label.eq(0) & out.tb_return.notna()
        target = np.where(timeout, (out.tb_return > 0).astype(float), target)
    out["target"] = target
    out["future_return"] = out.tb_return
    return out
