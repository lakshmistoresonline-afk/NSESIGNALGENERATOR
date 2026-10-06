"""Signal-only publication layer with regime, liquidity, risk/reward and uncertainty gates."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import pandas as pd
from typing import Optional
import math
import pandas as pd
from ..integrations.trademind_core import AdaptiveRiskGeometry
from ..risk.publication import publication_gate

@dataclass(frozen=True)
class Signal:
    symbol: str
    timestamp: str
    side: str
    probability_up: float
    confidence: float
    factor_score: float
    entry_price: Optional[float]
    stop_price: Optional[float]
    target_price: Optional[float]
    expected_value: Optional[float]
    regime: str
    quality_score: float
    gates: tuple
    reason: str
    signal_only: bool = True
    real_trading: bool = False
    provenance: str = "oos_model+factor+regime+cost_gate"

    def to_dict(self): return asdict(self)

class SignalEngine:
    def __init__(self, real_trading=False, probability_floor=.55, high_vol_floor=.65, min_rr=2.0, max_atr_pct=.08, max_signal_age_minutes=1440, require_economic_context=True):
        if real_trading:
            raise RuntimeError('REAL_TRADING is prohibited in this signal-only application')
        self.real_trading=False
        self.probability_floor=float(probability_floor)
        self.high_vol_floor=float(high_vol_floor)
        self.min_rr=float(min_rr)
        self.max_atr_pct=float(max_atr_pct)
        self.max_signal_age_minutes=int(max_signal_age_minutes)
        self.require_economic_context=bool(require_economic_context)

    def generate(self, symbol: str, probability_up: float, factor_score: float, threshold=None, price=None, atr_pct=None,
                 atr=None, regime='UNKNOWN', adx=None, volume_ratio=None, trend_alignment=None,
                 sector_relative_strength=None, signal_age_minutes=0, expected_cost_bps=40,
                 uncertainty=None, market_trend=None, india_vix_percentile=None, event_blackout=False, sector=None,
                 prediction_persistence=1, min_prediction_persistence=1, signal_stability=None, min_signal_stability=0.0, meta_probability=None, min_meta_probability=0.55, horizon_agreement=None, min_horizon_agreement=0.60, model_dispersion=None, max_model_dispersion=0.12, conformal_abstain=False, restricted=False, near_price_band=False, short_sale_blocked=False, market_data_stale=False, impact_cost_bps=None, max_impact_cost_bps=100.0, pit_ready=True, provenance_ready=True, membership_ready=True, membership_required=True, model_ready=True, snapshot_ready=True, session_ok=True, decision_timestamp=None, market_context_source=None) -> Optional[Signal]:
        if not 0 <= probability_up <= 1:
            raise ValueError('probability_up must be between 0 and 1')
        if not 0 <= factor_score <= 1:
            raise ValueError('factor_score must be between 0 and 1')
        threshold=float(threshold if threshold is not None else self.probability_floor)
        high_vol = str(regime).upper() in {'HIGH_VOLATILITY','BEAR_HIGH_VOL','RISK_OFF'} or (india_vix_percentile is not None and india_vix_percentile >= .80)
        floor=max(threshold, self.high_vol_floor if high_vol else self.probability_floor)
        side='BUY' if probability_up >= floor else ('SELL' if probability_up <= 1-floor else None)
        if side is None or factor_score < .50:
            return None
        if restricted or market_data_stale or not pit_ready or not provenance_ready:
            return None
        if membership_required and not membership_ready:
            return None
        if near_price_band:
            return None
        if side == 'SELL' and short_sale_blocked:
            return None
        if impact_cost_bps is not None and float(impact_cost_bps) > float(max_impact_cost_bps):
            return None
        if int(prediction_persistence) < int(min_prediction_persistence):
            return None
        if signal_stability is not None and float(signal_stability) < float(min_signal_stability):
            return None
        if meta_probability is not None and float(meta_probability) < float(min_meta_probability):
            return None
        if horizon_agreement is not None and float(horizon_agreement) < float(min_horizon_agreement):
            return None
        if model_dispersion is not None and float(model_dispersion) > float(max_model_dispersion):
            return None
        if conformal_abstain:
            return None
        if market_context_source is not None and str(market_context_source).strip()=='':
            return None
        if market_context_source is not None and str(market_context_source).strip().lower()=='stock_proxy':
            return None
        p_side=probability_up if side=='BUY' else 1-probability_up
        confidence=2*abs(p_side-.5)
        gates=['factor_support']
        if adx is not None:
            if adx < 18: return None
            gates.append('adx_ok')
        if volume_ratio is not None:
            if volume_ratio < .70: return None
            gates.append('liquidity_ok')
        if trend_alignment is not None:
            if (side=='BUY' and trend_alignment < 0) or (side=='SELL' and trend_alignment > 0): return None
            gates.append('trend_alignment')
        if sector_relative_strength is not None:
            if (side=='BUY' and sector_relative_strength < -.02) or (side=='SELL' and sector_relative_strength > .02): return None
            gates.append('sector_support')
        if signal_age_minutes > self.max_signal_age_minutes or event_blackout: return None
        if uncertainty is not None and uncertainty > .25: return None
        if uncertainty is not None: gates.append('uncertainty_ok')
        if impact_cost_bps is not None: gates.append('impact_cost_ok')
        gates.append('restriction_check')
        if model_ready: gates.append('model_champion_ok')
        if snapshot_ready: gates.append('dataset_snapshot_ok')
        if session_ok: gates.append('session_ok')
        if min_prediction_persistence > 1: gates.append('prediction_persistence')
        if signal_stability is not None: gates.append('signal_stability')
        if meta_probability is not None: gates.append('meta_label_ok')
        if horizon_agreement is not None: gates.append('multi_horizon_ok')
        if model_dispersion is not None: gates.append('model_agreement_ok')
        if conformal_abstain is False: gates.append('conformal_ok')
        entry=stop=target=expected=None
        if self.require_economic_context and (price is None or atr is None or atr <= 0):
            return None
        if price is not None and atr is not None and atr > 0:
            geom=AdaptiveRiskGeometry.levels(float(price),float(atr),side,str(regime),rr=self.min_rr)
            entry=float(price); stop=float(geom['stop']); target=float(geom['target'])
            if stop <= 0 or target <= 0: return None
            risk=abs(entry-stop); reward=abs(target-entry)
            rr=reward/risk if risk > 0 else 0.0
            if rr + 1e-12 < self.min_rr: return None
            cost=float(expected_cost_bps)/10000.0*entry
            expected=p_side*reward-(1-p_side)*risk-cost
            if expected <= 0: return None
            gates.append('positive_cost_adjusted_ev')
            if atr_pct is not None and atr_pct > self.max_atr_pct: return None
        regime_upper=str(regime).upper()
        regime_score=0.5 if regime_upper in {'UNKNOWN','SIDEWAYS'} else (0.75 if regime_upper in {'BULL','RISK_ON'} else 0.35 if regime_upper in {'BEAR','RISK_OFF'} else 0.45)
        gate=publication_gate(
            probability=p_side, factor_score=factor_score, regime_score=regime_score,
            uncertainty=float(uncertainty or 0), expected_value=expected, atr_pct=atr_pct,
            volume_ratio=volume_ratio, event_blackout=event_blackout,
            stale_minutes=signal_age_minutes, max_stale_minutes=self.max_signal_age_minutes,
            high_vol=high_vol, min_probability=floor, high_vol_probability=self.high_vol_floor,
            max_atr_pct=self.max_atr_pct, min_factor=.50, min_regime_score=.30,
            restricted=restricted, near_price_band=near_price_band,
            short_sale_blocked=(short_sale_blocked and side=='SELL'),
            market_data_stale=market_data_stale, impact_cost_bps=impact_cost_bps,
            max_impact_cost_bps=max_impact_cost_bps, pit_ready=pit_ready,
            provenance_ready=provenance_ready, membership_ready=membership_ready,
            membership_required=membership_required, model_ready=model_ready,
            snapshot_ready=snapshot_ready, session_ok=session_ok)
        if not gate['publish']:
            return None
        quality=.30*p_side+.25*factor_score+.20*confidence+.15*(1 if trend_alignment is None else max(0,min(1,(1+trend_alignment)/2)))+.10*(1 if adx is None else min(1,adx/40))
        return Signal(symbol=symbol,timestamp=(pd.Timestamp(decision_timestamp, tz='UTC').isoformat() if decision_timestamp is not None and pd.Timestamp(decision_timestamp).tzinfo is None else (pd.Timestamp(decision_timestamp).tz_convert('UTC').isoformat() if decision_timestamp is not None else datetime.now(timezone.utc).isoformat())),side=side,probability_up=probability_up,confidence=confidence,factor_score=factor_score,entry_price=entry,stop_price=stop,target_price=target,expected_value=expected,regime=str(regime),quality_score=float(quality),gates=tuple(gates),reason='calibrated OOS probability + optional meta-label/multi-horizon + factor/regime/liquidity/risk gates',signal_only=True,real_trading=False)

    @staticmethod
    def frame(signals): return pd.DataFrame([asdict(s) for s in signals])
