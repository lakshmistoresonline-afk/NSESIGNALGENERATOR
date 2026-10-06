from __future__ import annotations
import os
SECONDARY_PROVIDER_NAMES={"tejhq","bharatstock","upstox","5paisa","angelone","fyers","dhan","groww","yahoo"}
AUTOMATIC_FALLBACK_PROVIDERS=("tejhq","bharatstock","upstox","5paisa","angelone","fyers","dhan","groww")
def secondary_allowed(): return os.getenv("ALLOW_SECONDARY_PROVIDER","false").lower()=="true"
def assert_secondary_allowed(provider):
    if provider not in SECONDARY_PROVIDER_NAMES: raise ValueError(f"Unsupported secondary provider: {provider}")
    if not secondary_allowed(): raise RuntimeError("Secondary provider access is disabled. Set ALLOW_SECONDARY_PROVIDER=true for research only.")
