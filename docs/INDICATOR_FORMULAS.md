# Indicator Calculation Reference

The implementation in `src/nse_signal/features/indicators.py` is the executable source. This document records the intended calculation semantics.

## Trend
- SMA(n) = mean(C[t-n+1:t]).
- EMA uses recursive smoothing with alpha = 2/(n+1).
- Wilder smoothing uses alpha = 1/n.
- DEMA = 2*EMA - EMA(EMA).
- TEMA = 3*EMA1 - 3*EMA2 + EMA3.
- HMA(n) = WMA(2*WMA(C,n/2)-WMA(C,n), sqrt(n)).
- KAMA uses efficiency ratio ER = |C[t]-C[t-n]| / sum(|ΔC|), with smoothing constant between fast=2 and slow=30.
- Aroon uses the age/location of the highest high and lowest low in the lookback.
- Donchian upper/lower = rolling max(high)/min(low). Breakouts are compared with the **previous** channel.
- Keltner = EMA(close,20) ± 2*ATR(10).
- Supertrend uses HL2 ± multiplier*ATR and recursive final bands.

## Volatility
- True Range = max(H-L, |H-Cprev|, |L-Cprev|).
- ATR(n) = Wilder-smoothed True Range.
- NATR(n) = 100*ATR(n)/Close.
- Realized volatility(n) = stdev(simple close returns,n)*sqrt(252).
- Bollinger(20,2): middle=SMA20; bands=middle ± 2*population standard deviation; position=(C-middle)/(2*std).
- Range z-score = (range - rolling mean)/rolling standard deviation.

## Momentum
- RSI = 100 - 100/(1+AvgGain/AvgLoss), using Wilder smoothing; zero-loss windows resolve to 100 and zero-gain/zero-loss windows to 50.
- ROC(n) = 100*(C/C[n]-1).
- MACD = EMA12 - EMA26; signal=EMA9(MACD); histogram=MACD-signal.
- PPO = 100*(EMA12-EMA26)/EMA26; signal and histogram as MACD.
- Stochastic %K = 100*(C-Ln)/(Hn-Ln); %D=SMA(%K,3).
- Stochastic RSI applies stochastic normalization to RSI.
- ADX follows Wilder +DM/-DM, +DI/-DI, DX and Wilder-smoothed ADX. ADX measures strength, not direction; +DI/-DI provide direction.
- ADXR=(ADX[t]+ADX[t-n+1])/2.
- CCI=(TP-SMA(TP,n))/(0.015*MAD), where MAD is the rolling mean absolute deviation around the rolling TP mean.
- Williams %R=-100*(Hn-C)/(Hn-Ln).
- MFI uses typical price*volume and separates positive/negative money flow; zero negative flow resolves to 100 and a completely neutral window to 50.
- TSI = 100*double-EMA(momentum)/double-EMA(abs(momentum)).
- CMO = 100*(sum gains - sum losses)/(sum gains + sum losses).
- Ultimate Oscillator = weighted average of 7/14/28 buying-pressure/TR ratios with weights 4/2/1.
- Vortex provides VI+ and VI- from summed directional movement divided by summed True Range; `vortex_14` stores VI+ - VI-.
- Efficiency Ratio = directional change / total absolute change.
- VHF=(highest close-lowest close)/sum absolute close changes.

## Volume / flow
- OBV cumulatively adds/subtracts volume according to close direction.
- A/D = cumulative money-flow multiplier*volume.
- Chaikin oscillator = EMA3(A/D)-EMA10(A/D).
- CMF = rolling money-flow-volume / rolling volume.
- PVT = cumulative percentage-price-change*volume.
- Force Index = EMA13(price change*volume).
- Market Facilitation = (High-Low)/Volume.
- PVI/NVI start at 1000 and change with price returns only when volume respectively rises/falls.
- VWAP = cumulative typical-price*volume / cumulative volume; if `session_id` exists it resets at each session.

## Price structure
- Gap%=(Open-Cprev)/Cprev.
- Intraday range%=(High-Low)/Close.
- Body%=(Close-Open)/Open.
- Upper/lower wick percentages are measured from the candle body extremes to high/low.
- Price/MA gaps = Close/MA - 1.
- ATR% = ATR14/Close.

## Relative and NSE context
- Beta(n)=rolling Cov(stock return, benchmark return)/rolling Var(benchmark return).
- Correlation is rolling Pearson correlation.
- Optional India VIX, NIFTY, sector, FII/DII, breadth and derivatives inputs are provider-supplied context. The feature engine never invents missing market data.

## Research-label rule
`future_return` and `target` are labels only. They must never enter the feature matrix used to predict the same timestamp. The target currently represents the sign of the five-bar forward return and must be shifted/handled appropriately by the walk-forward trainer.

## Additional implemented families
- ROCP = C/C[n]-1; ROCR = C/C[n].
- APO = EMA_fast - EMA_slow; PVO = 100*(EMA_fast(volume)-EMA_slow(volume))/EMA_slow(volume), with signal EMA and histogram.
- Fast stochastic = smoothed raw %K and smoothed %D.
- +DM/-DM are Wilder-smoothed directional movements; DX = 100*abs(+DI--DI)/(+DI+-DI).
- VWMA = sum(C*V,n)/sum(V,n); RVOL = V/SMA(V,n).
- Average Price=(O+H+L+C)/4; Median Price=(H+L)/2; Typical Price=(H+L+C)/3; Weighted Close=(H+L+2C)/4.
- Heikin-Ashi: HA-Close=(O+H+L+C)/4; HA-Open=(prior HA-Open+prior HA-Close)/2; HA-High=max(H,HA-Open,HA-Close); HA-Low=min(L,HA-Open,HA-Close).
- Rolling linear regression uses least-squares slope/intercept over a fixed x-grid; TSF extrapolates the fitted line to the current endpoint; angle=atan(slope) in degrees.
- Percentile rank = percentage of observations in the trailing window less than or equal to the current observation.
- ADR = SMA(H-L,n). Chaikin Volatility = percentage change of EMA(H-L,n) over n bars. Mass Index = rolling sum of EMA(H-L,9)/EMA(EMA(H-L,9),9) over 25 bars.
- Momentum=C-C[n]; BOP=(C-O)/(H-L); Qstick=SMA(C-O,n); Elder Ray bull/bear power = H/L-EMA(C,n); WAD is cumulative Williams Accumulation/Distribution.
- TRIX = 1-period percentage change of a triple EMA; DPO removes the long-period moving-average component; Coppock is WMA(ROC14+ROC11,10); IMI uses intraday up/down bodies.
- Acceleration Bands expand H/L around a rolling mean using a range-dependent acceleration factor.
- ZLEMA applies an input de-lag transform before EMA; TRIMA is a double-smoothed SMA; T3 is the generalized Tillson triple-EMA formulation with configurable volume factor.


## Newly added formulas

### Internal Bar Strength
IBS = (Close - Low) / (High - Low).

### Choppiness Index
CHOP = 100 * log10(sum(TR,n) / (HighestHigh(n)-LowestLow(n))) / log10(n).

### Connors RSI
CRSI = mean(RSI(price, r1), RSI(streak, r2), PercentRank(ROC(price,1), rank_window)).

### Stochastic Momentum Index
The implementation centers the close relative to the rolling high/low midpoint, double-smooths the centered distance and range, then scales the ratio to the conventional SMI range.

### KST
KST = 1*SMA(ROC10,10) + 2*SMA(ROC15,10) + 3*SMA(ROC20,10) + 4*SMA(ROC30,15), with a configurable signal moving average.

### EMV
EMV is based on one-bar midpoint displacement normalized by the high-low box and volume, followed by configurable smoothing.

### Refined RVI
The refined RVI variant separates high/low range volatility by the direction of the close change and applies Wilder smoothing before forming the 0-100 ratio.
