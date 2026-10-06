"""Explicit, configurable transaction-cost model for Indian equity research."""
from __future__ import annotations
import math


def round_trip_cost_bps(*, fixed_bps=30.0, slippage_bps=10.0, spread_bps=0.0, dollar_volume=None, participation=0.0, impact_coefficient=0.0):
    impact=0.0
    if dollar_volume and dollar_volume>0 and participation>0 and impact_coefficient>0:
        impact=impact_coefficient*math.sqrt(participation)*1e4/math.sqrt(dollar_volume)
    return float(fixed_bps+slippage_bps+spread_bps+impact)
