"""Conservative transaction-cost and market-impact diagnostics."""
from __future__ import annotations
import numpy as np


def square_root_impact_bps(order_value: float, daily_dollar_volume: float, sigma: float,
                           impact_coeff: float = 0.5) -> float:
    """Estimate temporary market impact in basis points.

    This is a conservative research model, not a broker/exchange execution model.
    It is used to reject economically marginal signals when liquidity is poor.
    """
    if order_value <= 0 or daily_dollar_volume <= 0 or sigma < 0:
        raise ValueError("order_value and daily_dollar_volume must be positive; sigma non-negative")
    participation = min(max(order_value / daily_dollar_volume, 0.0), 1.0)
    return float(10000.0 * impact_coeff * sigma * np.sqrt(participation))


def total_expected_cost_bps(expected_cost_bps: float, impact_bps: float, spread_bps: float = 0.0) -> float:
    return float(max(0.0, expected_cost_bps) + max(0.0, impact_bps) + max(0.0, spread_bps))
