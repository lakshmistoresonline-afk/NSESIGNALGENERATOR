# Quantitative Research Audit & Algorithmic Strategy Enhancement Blueprint

## Executive Summary
This forensic audit examines the current signal generation architecture of the NSE Signal Provider V31 platform. While the system adheres to strict point-in-time (PIT) governance and fail-closed safety (`REAL_TRADING = FALSE`), the technical indicator suite can be significantly enhanced to filter out false breakouts, suppress whipsaws during sideways market regimes, and optimize the Sharpe/Sortino ratio specifically for Indian equities (NSE / Nifty / BankNifty).

---

## 1. Gap Analysis Matrix: Current vs. Missing High-Conviction Indicators

| Current Method / Indicator | Missing High-Conviction Indicator / Filter | Quant Problem Solved | Recommended Math / Formula / Library |
| :--- | :--- | :--- | :--- |
| **Simple / Exponential Moving Averages** | **Multi-Timeframe Anchored VWAP (AVWAP)** | Eliminates lagging moving average whipsaws; anchors volume-weighted cost basis to structural swing highs, lows, and budget/earnings announcements. | `pandas`, custom vectorization |
| **Raw RSI (70/30)** | **RSI Regime & Divergence Detection** | Eliminates premature counter-trend entries in strong momentum regimes; identifies hidden and regular bullish/bearish divergences. | `pandas`, vectorised peak/trough detection |
| **Static Stop-Loss (% based)** | **Dynamic ATR Bands & Chandelier Exits** | Prevents premature shakeouts in high-beta NSE stocks while adapting to volatility expansion/compression. | `ATR(14)`, rolling max/min |
| **Basic Volatility Check** | **TTM Squeeze (Bollinger + Keltner)** | Anticipates explosive directional breakouts following periods of tight consolidation. | `BB width < Keltner channel width` |
| **Unfiltered Momentum** | **ADX + DMI Trend Strength Filter** | Rejects breakout trades when market is in a choppy, sideways regime (`ADX < 20`). | Wilder's ADX smoothing |
| **Single-Timeframe Signals** | **Multi-Timeframe Alignment (MTF)** | Ensures lower-timeframe execution (e.g. 15m) aligns with higher-timeframe trend (1h / Daily). | Resampling / Hierarchical merging |

---

## 2. Composite Signal Scoring Model (The Solution)
To combine multi-dimensional alpha sources without over-fitting, we introduce a **Weighted Multi-Factor Composite Scoring Model** (requiring a minimum confluence score of **$\ge 75\%$** before signal publication):

$$\text{Composite Score} = 0.30 \times S_{\text{Trend}} + 0.25 \times S_{\text{Momentum}} + 0.25 \times S_{\text{Volume/VWAP}} + 0.20 \times S_{\text{Regime}}$$

- **Trend ($S_{\text{Trend}}$ - 30%)**: ADX > 25, price above 50 EMA and 200 EMA.
- **Momentum ($S_{\text{Momentum}}$ - 25%)**: RSI between 50-70 (for longs) with MACD histogram expansion.
- **Volume / VWAP ($S_{\text{Volume/VWAP}}$ - 25%)**: Price > Anchored VWAP, volume > 1.5x 20-period volume MA.
- **Market Regime ($S_{\text{Regime}}$ - 20%)**: India VIX in normal expansion band (12–22), positive sector relative strength vs Nifty 500.

---

## 3. Step-by-Step Implementation Roadmap
- **Phase 1 (Quick Wins)**: Integrate ADX + DMI trend filters, dynamic ATR Chandelier exits, and volume multiplier checks into feature building.
- **Phase 2 (Advanced Indicators)**: Implement Multi-Timeframe Anchored VWAP and TTM Squeeze volatility compression detection.
- **Phase 3 (Backtesting & Governance)**: Vectorized out-of-sample backtesting with cost-adjusted expected value validation and strict publication gating.

---

## 4. Ready-to-Implement Python Code: Top 2 Critical Indicator Modules

### Module 1: TTM Squeeze (Volatility Compression & Expansion)
```python
import numpy as np
import pandas as pd


def compute_ttm_squeeze(
    df: pd.DataFrame,
    bb_length: int = 20,
    bb_std: float = 2.0,
    kc_length: int = 20,
    kc_mult: float = 1.5,
) -> pd.DataFrame:
  """Identifies TTM Squeeze volatility compression (Bollinger Bands inside Keltner Channels)."""
  c = df['close']
  h = df['high']
  l = df['low']

  # Bollinger Bands
  sma = c.rolling(bb_length).mean()
  std = c.rolling(bb_length).std()
  upper_bb = sma + (bb_std * std)
  lower_bb = sma - (bb_std * std)

  # Keltner Channels
  tr = pd.concat([h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()], axis=1).max(axis=1)
  atr = tr.rolling(kc_length).mean()
  ema = c.ewm(span=kc_length, adjust=False).mean()
  upper_kc = ema + (kc_mult * atr)
  lower_kc = ema - (kc_mult * atr)

  # Squeeze On when Bollinger Bands are inside Keltner Channels
  df['squeeze_on'] = (lower_bb > lower_kc) & (upper_bb < upper_kc)
  df['squeeze_off'] = (lower_bb < lower_kc) | (upper_bb > upper_kc)

  # Momentum oscillator for squeeze firing direction
  highest_high = h.rolling(kc_length).max()
  lowest_low = l.rolling(kc_length).min()
  avg_hl = (highest_high + lowest_low) / 2
  sma_c = c.rolling(kc_length).mean()
  val = c - ((avg_hl + sma_c) / 2)
  df['squeeze_momentum'] = val.ewm(span=5, adjust=False).mean()
  return df
```

### Module 2: Anchored VWAP (AVWAP)
```python
import numpy as np
import pandas as pd


def compute_anchored_vwap(df: pd.DataFrame, anchor_idx: int) -> pd.Series:
  """Computes Anchored Volume Weighted Average Price (AVWAP) from a structural anchor index."""
  sub = df.iloc[anchor_idx:].copy()
  typical_price = (sub['high'] + sub['low'] + sub['close']) / 3
  pv = typical_price * sub['volume']
  cum_pv = pv.cumsum()
  cum_vol = sub['volume'].cumsum()
  avwap = cum_pv / cum_vol

  # Realign to full dataframe index with NaN prior to anchor
  full_avwap = pd.Series(index=df.index, dtype=float)
  full_avwap.iloc[anchor_idx:] = avwap
  return full_avwap
```
