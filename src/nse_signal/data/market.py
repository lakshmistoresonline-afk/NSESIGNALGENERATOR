"""Market-data loading with an explicit no-unlicensed-production-source policy."""
from pathlib import Path
import numpy as np
import pandas as pd


def download_symbol(*args, **kwargs):
    raise RuntimeError(
        "No third-party market-data downloader is enabled by default. Use scripts/acquire_secondary_market_data.py for explicitly enabled "
        "research/current-data providers. Secondary providers are never authoritative PIT sources."
    )

def load_symbol_from_provider(symbol: str, provider: str, start, end, interval="1d", **kwargs) -> pd.DataFrame:
    """Fetch secondary data only when explicitly enabled. Never satisfies PIT readiness."""
    from .providers.registry import build_registry
    from .providers.policy import assert_secondary_allowed
    assert_secondary_allowed(provider)
    result = build_registry().historical(provider, symbol, start, end, interval, **kwargs)
    df = result.dataframe.copy()
    if df.empty:
        raise ValueError(f"Secondary provider {provider} returned no rows for {symbol}")
    return df


def load_symbol(symbol: str, cache_dir="data/raw") -> pd.DataFrame:
    p = Path(cache_dir) / f"{symbol.replace('.', '_')}.csv"
    if not p.exists():
        raise FileNotFoundError(
            f"Authoritative local market data not found for {symbol}: {p}. "
            "Production signals require validated NSE PIT data; no third-party fallback is used."
        )
    df = pd.read_csv(p, index_col=0, parse_dates=True)
    required = {"open", "high", "low", "close", "volume"}
    missing = required - set(df.columns.str.lower())
    if missing:
        raise ValueError(f"Local market file is missing required columns: {sorted(missing)}")
    return df


def synthetic_symbol(symbol="TEST.NS", n=700, seed=42) -> pd.DataFrame:
    """Synthetic data for software/invariant tests only; never a production source."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2022-01-03", periods=n)
    returns = rng.normal(0.0004, 0.018, n)
    close = 100 * np.exp(np.cumsum(returns))
    open_ = close * (1 + rng.normal(0, 0.004, n))
    high = np.maximum(open_, close) * (1 + rng.uniform(0, .012, n))
    low = np.minimum(open_, close) * (1 - rng.uniform(0, .012, n))
    volume = rng.lognormal(13, .35, n)
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": volume, "symbol": symbol}, index=dates)
