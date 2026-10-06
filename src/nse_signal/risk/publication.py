"""Pre-publication gates designed to reject statistically weak or operationally unsafe signals."""
from __future__ import annotations
import numpy as np
import pandas as pd


def publication_gate(*, probability, factor_score, regime_score=0.5, uncertainty=0.0,
                     expected_value=None, atr_pct=None, volume_ratio=None,
                     event_blackout=False, stale_minutes=0, max_stale_minutes=1440,
                     high_vol=False, min_probability=.55, high_vol_probability=.65,
                     max_atr_pct=.08, min_factor=.50, min_regime_score=.35,
                     restricted=False, near_price_band=False, short_sale_blocked=False,
                     market_data_stale=False, impact_cost_bps=None, max_impact_cost_bps=100.0,
                     pit_ready=True, provenance_ready=True, membership_ready=True,
                     membership_required=True, model_ready=True, snapshot_ready=True,
                     session_ok=True, signal_expired=False):
    reasons=[]
    p=float(probability)
    if p < (high_vol_probability if high_vol else min_probability): reasons.append('probability_below_floor')
    if factor_score < min_factor: reasons.append('factor_below_floor')
    if not pit_ready: reasons.append('pit_not_ready')
    if not provenance_ready: reasons.append('provenance_not_ready')
    if membership_required and not membership_ready: reasons.append('membership_not_ready')
    if not model_ready: reasons.append('model_champion_not_ready')
    if not snapshot_ready: reasons.append('dataset_snapshot_not_ready')
    if not session_ok: reasons.append('invalid_market_session')
    if signal_expired: reasons.append('signal_expired')
    if regime_score < min_regime_score: reasons.append('regime_weak')
    if uncertainty > .25: reasons.append('model_disagreement_high')
    if expected_value is not None and expected_value <= 0: reasons.append('non_positive_cost_adjusted_ev')
    if atr_pct is not None and atr_pct > max_atr_pct: reasons.append('volatility_too_high')
    if volume_ratio is not None and volume_ratio < .70: reasons.append('liquidity_too_low')
    if event_blackout: reasons.append('corporate_event_blackout')
    if stale_minutes > max_stale_minutes: reasons.append('stale_signal')
    if restricted: reasons.append('security_restricted')
    if near_price_band: reasons.append('near_price_band')
    if short_sale_blocked: reasons.append('short_sale_blocked')
    if market_data_stale: reasons.append('market_data_stale')
    if impact_cost_bps is not None and float(impact_cost_bps) > float(max_impact_cost_bps): reasons.append('impact_cost_too_high')
    return {'publish': not reasons, 'reasons': reasons}
