"""Secondary market-data provider adapters.

These providers are useful for development, current-data supplementation and
research cross-checks. They are NOT authoritative NSE PIT sources.
"""
from .registry import ProviderRegistry, build_registry
from .providers import UpstoxProvider, FivePaisaProvider
from .catalog import get_provider_catalog
from .reconcile import reconcile_candles

__all__ = ["ProviderRegistry", "build_registry", "UpstoxProvider", "FivePaisaProvider", "get_provider_catalog", "reconcile_candles"]
