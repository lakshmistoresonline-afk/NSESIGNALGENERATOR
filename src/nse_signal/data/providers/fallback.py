from __future__ import annotations
from .registry import build_registry
from .base import ProviderError
import inspect

class SecondaryFallback:
    """Explicit secondary provider cascade. Never changes PIT authority."""
    def __init__(self, order=None):
        self.order = order or ["tejhq", "bharatstock", "upstox", "5paisa", "angelone", "fyers", "dhan", "groww"]
        self.registry = build_registry()

    def historical(self, symbol, start, end, interval="1d", **kwargs):
        errors = {}
        for name in self.order:
            try:
                provider = self.registry.get(name)
                sig = inspect.signature(provider.historical)
                allowed = {k:v for k,v in kwargs.items() if k in sig.parameters}
                result = provider.historical(symbol, start, end, interval, **allowed)
                if len(result.dataframe):
                    return result, errors
            except Exception as exc:
                errors[name] = str(exc)
        raise ProviderError(f"All secondary providers failed for {symbol}: {errors}")
