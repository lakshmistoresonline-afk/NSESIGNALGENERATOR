# Indicator Coverage Matrix

The implementation is deliberately split into **implemented/calculated**, **provider-supplied**, and **not-used-by-the-model** families. TA-Lib's current catalogue contains 200+ technical-analysis functions across cycle, math, momentum, overlap, pattern, price-transform, statistics, volatility and volume groups. This project implements the market-relevant subset as executable features and does not pretend that generic scalar math functions are trading indicators.

## Implemented executable families

- Trend/overlap: SMA, EMA, RMA/Wilder, DEMA, TEMA, HMA, KAMA, ZLEMA, TRIMA, T3, VWMA, midpoint, midprice, Parabolic SAR, Supertrend, Donchian, Keltner, Aroon, classic pivots, acceleration bands.
- Momentum: RSI, ROC/ROCP/ROCR, MACD, PPO, APO, Stochastic/fast stochastic, StochRSI, ADX, ADXR, DX, +DI/-DI, +DM/-DM, CCI, Williams %R, MFI, TSI, AO, CMO, Ultimate Oscillator, Vortex, RVI, ER, VHF, momentum, BOP, Qstick, Elder Ray, TRIX, DPO, Coppock, IMI.
- Volatility/statistics: TR, ATR, NATR, realized volatility, Bollinger, ADR, Chaikin volatility, Mass Index, rolling standard deviation/variance, rolling linear regression slope/intercept/angle, TSF, percentile and percent-rank, beta and correlation.
- Volume/flow: OBV, A/D, Chaikin oscillator, CMF, PVT, Force Index, Market Facilitation, PVI, NVI, PVO, RVOL, VWAP, VWMA, volume ratios/z-score, dollar volume and turnover z-score.
- Price transforms: average price, median price, typical price, weighted close, Heikin-Ashi.
- Price action: gaps, range, candle body, wick geometry, breakout/breakdown, channel position and normalized distances.

## Provider-supplied context

These must come from a historical/live data provider and are never synthesized by the feature engine:

- India VIX
- NIFTY benchmark return
- sector return
- advance/decline breadth
- FII/DII flow
- options PCR
- open-interest change
- futures basis
- externally calculated relative-strength series

The engine derives z-scores, beta, correlation and compounded relative strength from provider data when available.

## Deliberately excluded

Generic arithmetic/trigonometric functions and the full 60+ candlestick-recognition catalogue are not automatically injected into the predictive feature matrix. Candlestick recognition requires a separate pattern specification and extensive regression tests for candle-body/average-range rules; blindly adding every pattern creates highly correlated sparse features and increases multiple-testing risk. Such patterns can be added through the same registry → implementation → test → OOS-validation pipeline.

## Research rule

An indicator is **not** assumed predictive because its historical name or conventional threshold is popular. Every new parameter or feature must be evaluated using purged/embargoed walk-forward validation, realistic Indian costs and out-of-sample statistical controls.

## Extended executable coverage
Additional executable indicators now include WMA, Aroon Oscillator, ROCR100, CMOU, Accelerator Oscillator, KDJ, configurable MACDEXT, MACDFIX, Forecast Oscillator, Williams fractal confirmation, and a causal Hilbert-style trendline proxy. The Hilbert-style trendline is explicitly a causal proxy and is not represented as byte-for-byte TA-Lib HT_TRENDLINE.


## Full TA-Lib reference catalogue (exact optional backend)
The current TA-Lib catalogue is broader than the dependency-light core. The bundled exact reference catalogue contains 223 named functions. The package therefore includes `src/nse_signal/features/talib_reference.py`, which enumerates the current cycle, momentum, overlap, price-transform, statistics, volatility, volume and candlestick families. When the optional `TA-Lib` package is installed, `call(name, ...)` delegates to the upstream implementation for exact regression/reference calculations. The core package does not silently label proxies such as its causal Hilbert-style trendline as exact TA-Lib equivalents.

Optional dependency: `requirements-reference.txt`.

Candlestick functions remain a separate namespace because TA-Lib's candle-setting/range rules are distinct from the continuous indicator feature matrix. They are available through the exact reference backend rather than being injected into the predictive model automatically.

## Exact parameter metadata

When TA-Lib is installed, `talib_reference.parameter_registry()` retrieves the installed upstream function metadata, including inputs, outputs and optional parameters. This is the authoritative source for exact TA-Lib parameter signatures; the YAML remains the source of truth for the dependency-light research feature set.
