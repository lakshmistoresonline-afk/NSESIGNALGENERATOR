"""TradeMindAI-inspired components integrated into the unified signal engine.

Only research/signal concepts are implemented here: regime overlay, ATR geometry,
quality gating, provenance, and immutable outcome lifecycle. No order execution.
"""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Regime:
    label: str
    risk_mode: str
    score: float

class TradeMindRegime:
    @staticmethod
    def classify(trend_score: float, volatility_score: float, breadth_score: float) -> Regime:
        sentiment=(trend_score+breadth_score+(1-volatility_score))/3
        if trend_score>.7 and volatility_score<.6: return Regime('BULL','RISK_ON',sentiment)
        if trend_score<.3 and volatility_score>.4: return Regime('BEAR','RISK_OFF',sentiment)
        if volatility_score>.75: return Regime('HIGH_VOLATILITY','DELEVERAGE',sentiment)
        if abs(trend_score-.5)<.1 and volatility_score<.35: return Regime('LOW_VOLATILITY','ACCUMULATION',sentiment)
        return Regime('SIDEWAYS','NEUTRAL',sentiment)

class AdaptiveRiskGeometry:
    @staticmethod
    def levels(price: float, atr: float, side: str, regime: str, rr: float=2.0):
        if not all(isfinite(x) and x>0 for x in (price,atr)): raise ValueError('invalid price/ATR')
        mult = 2.8 if regime=='HIGH_VOLATILITY' else 1.8 if regime in ('SIDEWAYS','LOW_VOLATILITY') else 2.2
        risk=atr*mult
        if side=='BUY': stop=price-risk; target=price+risk*rr
        else: stop=price+risk; target=price-risk*rr
        return {'stop':round(stop,2),'target':round(target,2),'risk_per_unit':round(risk,2),'rr':rr}
