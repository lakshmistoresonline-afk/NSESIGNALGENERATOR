import pandas as pd

def factor_snapshot(df: pd.DataFrame) -> dict:
    c = df.close
    return {
        "momentum_20": float(c.iloc[-1] / c.iloc[-21] - 1) if len(c) > 21 else float("nan"),
        "momentum_60": float(c.iloc[-1] / c.iloc[-61] - 1) if len(c) > 61 else float("nan"),
        "volatility_20": float(c.pct_change().rolling(20).std().iloc[-1]),
        "distance_52w_high": float(c.iloc[-1] / c.tail(252).max() - 1),
    }

def cross_sectional_rank(rows: list[dict]) -> pd.DataFrame:
    x = pd.DataFrame(rows)
    for col in ["momentum_20", "momentum_60"]:
        x[col+"_rank"] = x[col].rank(pct=True)
    x["factor_score"] = (x.momentum_20_rank.fillna(.5) + x.momentum_60_rank.fillna(.5)) / 2
    return x.sort_values("factor_score", ascending=False)
