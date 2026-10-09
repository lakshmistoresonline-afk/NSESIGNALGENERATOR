"""Causal market-structure, microstructure, and advanced alpha proxies (TTM Squeeze, Anchored VWAP, and volume profile features) derived only from OHLCV.

These are deliberately lightweight substitutes for richer point-in-time feeds.
They never use future observations and should still be validated OOS.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def add_advanced_features(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    o, h, l, c, v = (x[k].astype(float) for k in ("open", "high", "low", "close", "volume"))
    eps = 1e-12
    log_hl = np.log((h + eps) / (l + eps))
    log_co = np.log((c + eps) / (o + eps))
    log_oc = np.log((o + eps) / (c.shift(1) + eps))

    # Alternative realized-volatility estimators: useful when ATR alone is unstable.
    x["parkinson_vol_20"] = np.sqrt((log_hl.pow(2).rolling(20).mean()) / (4*np.log(2))) * np.sqrt(252)
    rs = np.log((h+eps)/(c+eps))*np.log((h+eps)/(o+eps)) + np.log((l+eps)/(c+eps))*np.log((l+eps)/(o+eps))
    x["garman_klass_vol_20"] = np.sqrt(rs.rolling(20).mean().clip(lower=0)) * np.sqrt(252)
    x["overnight_return_1d"] = log_oc
    x["intraday_return_1d"] = np.log((c+eps)/(o+eps))
    x["overnight_intraday_gap_20_z"] = (x.overnight_return_1d - x.overnight_return_1d.rolling(20).mean()) / x.overnight_return_1d.rolling(20).std()

    # Liquidity / price-impact proxies, causal and cost-aware.
    dollar_volume = (c.abs() * v).replace([np.inf, -np.inf], np.nan)
    x["amihud_20"] = (x.close.pct_change().abs() / dollar_volume.replace(0, np.nan)).rolling(20).mean()
    x["dollar_volume_z20"] = (dollar_volume - dollar_volume.rolling(20).mean()) / dollar_volume.rolling(20).std()
    x["range_per_volume_20"] = ((h-l) / v.replace(0, np.nan)).rolling(20).mean()

    # Signed-volume proxies: not true order flow, but useful as a separate candidate family.
    signed = np.sign(c.diff()).fillna(0.0) * v
    x["signed_volume_ratio_20"] = signed.rolling(20).sum() / (v.rolling(20).sum().replace(0, np.nan))
    x["close_location_value"] = ((2*c-l-h) / (h-l).replace(0, np.nan)).clip(-1, 1)
    x["clv_volume_20"] = (x.close_location_value * v).rolling(20).sum() / v.rolling(20).sum().replace(0, np.nan)

    # Trend quality / compression rather than another raw oscillator.
    ret = c.pct_change()
    direction = ret.rolling(20).sum().abs()
    path = ret.abs().rolling(20).sum().replace(0, np.nan)
    x["directional_efficiency_20"] = direction / path
    x["return_skew_20"] = ret.rolling(20).skew()
    x["return_kurtosis_20"] = ret.rolling(20).kurt()
    x["vol_of_vol_20"] = ret.rolling(5).std().rolling(20).std()
    x["range_compression_20"] = (h-l).rolling(5).mean() / (h-l).rolling(20).mean()
    x["close_to_high_20"] = (c - h.rolling(20).min()) / (h.rolling(20).max() - h.rolling(20).min()).replace(0, np.nan)
    x["distance_from_20d_vwap"] = c / ((c*v).rolling(20).sum()/v.rolling(20).sum().replace(0,np.nan)) - 1

    # TTM Squeeze Volatility Compression & Momentum
    sma = c.rolling(20).mean()
    std = c.rolling(20).std()
    upper_bb = sma + (2.0 * std)
    lower_bb = sma - (2.0 * std)
    tr = pd.concat([h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()], axis=1).max(axis=1)
    atr = tr.rolling(20).mean()
    ema = c.ewm(span=20, adjust=False).mean()
    upper_kc = ema + (1.5 * atr)
    lower_kc = ema - (1.5 * atr)
    x["squeeze_on"] = ((lower_bb > lower_kc) & (upper_bb < upper_kc)).astype(float)
    highest_high = h.rolling(20).max()
    lowest_low = l.rolling(20).min()
    avg_hl = (highest_high + lowest_low) / 2
    val = c - ((avg_hl + sma) / 2)
    x["squeeze_momentum"] = val.ewm(span=5, adjust=False).mean()

    # Anchored VWAP / Volume Profile proxy (rolling 20-period anchor)
    typical_price = (h + l + c) / 3
    pv = typical_price * v
    x["anchored_vwap_20"] = pv.rolling(20).sum() / v.rolling(20).sum().replace(0, np.nan)
    x["avwap_gap_20"] = c / x["anchored_vwap_20"] - 1.0

    return x.replace([np.inf, -np.inf], np.nan)

# Optional stationarity-preserving transforms. Imported lazily to keep the core
# indicator library dependency-light and backwards compatible.
def add_fractional_features(df, d_values=(0.2, 0.4), window=50):
    from .market_state import fractional_difference
    out = df.copy()
    for d in d_values:
        out[f"close_fracdiff_{str(d).replace('.', '_')}"] = fractional_difference(out["close"], d=d, window=window)
        out[f"log_return_fracdiff_{str(d).replace('.', '_')}"] = fractional_difference(np.log(out["close"]).diff(), d=d, window=window)
    return out
