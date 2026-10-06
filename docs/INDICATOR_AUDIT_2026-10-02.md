# Indicator / Parameter Audit — 2026-10-02

## Reference basis

The audit uses the current official TA-Lib catalogue and source documentation. TA-Lib documents formulas, inputs, outputs and parameters for each function and provides the official C/Rust/Java implementations.

The reference catalogue bundled by this project contains **223 named functions**:

| Family | Count |
|---|---:|
| Math operators | 12 |
| Math transforms | 15 |
| Cycle indicators | 5 |
| Momentum indicators | 58 |
| Overlap studies | 30 |
| Price transforms | 6 |
| Statistics | 13 |
| Volatility | 10 |
| Volume | 13 |
| Candlestick patterns | 61 |
| **Total** | **223** |

The 223 count is a catalogue count, not a claim that all 223 should be injected into the predictive model. Generic math functions and sparse candlestick patterns are available through the exact reference backend and are deliberately separated from the default ML feature matrix.

## Calculation corrections in this revision

1. EMA now uses an SMA seed followed by alpha = 2/(n+1), matching the current TA-Lib EMA definition.
2. Wilder/RMA remains SMA-seeded with alpha = 1/n.
3. SMI now implements the documented Blau formula:
   `100 * EMA(EMA(close - 0.5*(HH+LL), slow), fast) / (0.5 * EMA(EMA(HH-LL, slow), fast))`, with an independently configurable signal EMA.
4. Stochastic exposes FastK, SlowK period/MA type, SlowD period/MA type.
5. STOCHRSI exposes RSI period, stochastic window, D period and D MA type.
6. KDJ exposes FastK, K/D smoothing periods and both MA types; default smoothing is Wilder/RMA.
7. BBANDS exposes period, upper deviation, lower deviation and MA type.
8. APO/PPO/PVO expose MA type rather than silently assuming EMA.
9. Unsupported MA types in the dependency-light core now raise an error instead of silently falling back to another calculation. Exact unsupported types are delegated to the optional TA-Lib backend.
10. Donchian aliases and breakout features follow the configured first channel period instead of hard-coding 20.
11. Target/future-return labels remain outside the causal feature frame.

## Parameter authority

`config/indicator_parameters.yaml` controls the dependency-light core. The exact TA-Lib backend can retrieve the installed library's parameter metadata with `parameter_registry()`, avoiding a second stale copy of the upstream parameter definitions.

## Validation

The automated suite currently passes **22 tests**. It covers EMA/Wilder seeding, edge cases, feature coverage, prefix stability, breakout causality, fractal confirmation, beta convention, parameter wiring, SMI bounds, target isolation, walk-forward execution, signal-only enforcement, and reference-catalog completeness.

A 700-bar synthetic audit produced **212 registered candidate features and 226 total columns**, with zero missing registered candidate features and 501 fully populated rows after the combined warm-up period.

## Important limitation

The local dependency-light implementation is not claimed to be byte-identical to TA-Lib for every recursive/cycle/pattern function. Where an exact upstream implementation is required, use `src/nse_signal/features/talib_reference.py` with the optional TA-Lib package. The project explicitly labels proxies (for example, the causal Hilbert-style trendline proxy) rather than presenting them as exact implementations.
