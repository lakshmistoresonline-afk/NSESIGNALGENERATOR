# NSE Signal Provider — Indicator & Parameter Registry

This is an executable research feature library, not a claim that every technical indicator is predictive. TA-Lib currently documents 200+ technical-analysis functions across cycle, math, momentum, overlap, pattern, price-transform, statistics, volatility and volume groups. The project implements a broad market-relevant subset and explicitly documents provider-only data and excluded families.

## Trend / overlap
SMA 5/10/20/50/100/200; EMA 5/10/20/50/100/200; DEMA-20; TEMA-20; HMA-20; KAMA(10,2,30); ZLEMA-20; TRIMA-20; T3(5,0.7); VWMA-20; midpoint/midprice-14; Parabolic SAR(0.02,0.20); Supertrend(10,3); Donchian(20,55); Keltner(20,10,2); Aroon(25); classic pivots; acceleration bands(20,4).

## Momentum / direction
RSI(7,14,21); ROC(5,10,20); ROCP/ROCR(20); MACD(12,26,9); PPO(12,26,9); APO(12,26); Stochastic(14,3); fast stochastic(14,3,3); StochRSI(14,14,3); ADX/+DI/-DI/ADXR/DX/+DM/-DM(14); CCI(20); Williams %R(14); MFI(14); TSI(25,13); Awesome Oscillator(5,34); CMO(14); Ultimate Oscillator(7,14,28); Vortex(14); RVI(14,10); Efficiency Ratio(10); VHF(28); Momentum(10); BOP; Qstick(14); Elder Ray(13); TRIX(30); DPO(20); Coppock(14,11,10); IMI(14).

## Volatility / statistics
True Range; ATR/NATR(5,14,20); annualized realized volatility(5,10,20,60); Bollinger(20,2); ADR(14); Chaikin Volatility(10); Mass Index(9,25); rolling standard deviation/variance(20); linear regression slope/intercept/angle and TSF(20); percentile/percent-rank(20); ATR/range z-scores; beta/correlation(60).

## Volume / flow
OBV; OBV z-score(20); A/D; Chaikin A/D oscillator(3,10); CMF(20); MFI(14); PVT; Force Index(13); Market Facilitation Index; PVI; NVI; PVO(12,26,9); RVOL(20); VWAP; VWMA; volume ratio(20,50); volume z-score(20); dollar volume; turnover z-score(20).

## Price transforms / structure
Average Price; Median Price; Typical Price; Weighted Close; Heikin-Ashi; 1/3/5/20/60/120-bar returns; opening gap; candle body; wick geometry; intraday range; 20-bar breakout/breakdown; channel position; price-to-average gaps; SAR/Supertrend gaps; pivot relationships.

## NSE context / derivatives
Provider-supplied: India VIX, NIFTY return, sector return, advance/decline ratio, FII net, DII net, PCR, OI change, futures basis and external relative-strength series. The feature engine calculates z-scores and stock-vs-benchmark beta/correlation/compounded relative strength when those inputs exist, but never fabricates missing data.

NSE defines India VIX from NIFTY option order-book prices as expected volatility over the next 30 calendar days. citeturn0search0 NIFTY 200 contains NIFTY 100 and NIFTY Midcap 100 constituents. citeturn0search3

## Parameter governance
`config/indicator_parameters.yaml` is the parameter registry. `add_all()` reads that registry by default. Parameters that affect model feature names/periods must be changed together with the candidate feature registry and then validated with purged/embargoed walk-forward OOS tests.

## Calculation governance
- Wilder/RMA uses an SMA seed and recursive alpha=1/n.
- Bollinger/RVI/rolling volatility use population standard deviation where the formula calls for it.
- Breakouts compare against the previous channel.
- Pivots use prior-bar OHLC.
- VWAP can reset by explicit `session_id`.
- Forward labels are never members of the feature matrix.
- Degenerate divisions return bounded values or NaN; missing external context remains missing.
- Indicator additions require formula tests, prefix-stability tests and OOS evaluation.
