from __future__ import annotations
from .providers import YahooProvider, AngelOneProvider, GrowwProvider, DhanProvider, FyersProvider, UpstoxProvider, FivePaisaProvider, TejHQProvider, BharatStockProvider

class ProviderRegistry:
    def __init__(self, providers): self.providers = providers
    def names(self): return list(self.providers)
    def get(self, name):
        if name not in self.providers: raise KeyError(f"Unknown provider: {name}")
        return self.providers[name]
    def historical(self, provider, *args, **kwargs): return self.get(provider).historical(*args, **kwargs)

def build_registry():
    return ProviderRegistry({
        "tejhq": TejHQProvider(), "bharatstock": BharatStockProvider(),
        "upstox": UpstoxProvider(), "5paisa": FivePaisaProvider(), "yahoo": YahooProvider(),
        "angelone": AngelOneProvider(), "groww": GrowwProvider(), "dhan": DhanProvider(), "fyers": FyersProvider(),
    })
