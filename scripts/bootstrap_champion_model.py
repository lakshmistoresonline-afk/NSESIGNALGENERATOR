"""Bootstraps a lightweight production champion model artifact and registers it in ModelRegistry so signal engines can generate signals."""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nse_signal.features.build import make_features
from nse_signal.models.production import fit_production_model, save_artifact
from nse_signal.models.registry import ModelRegistry

def bootstrap():
    cash_csv = Path("data/processed/nse_pit/cash_daily.csv")
    if not cash_csv.exists():
        print("cash_daily.csv not found")
        return

    df = pd.read_csv(cash_csv, low_memory=False).head(5000)
    if "date" in df.columns:
        df["timestamp"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
        df = df.sort_values(["symbol", "timestamp"])
        df = make_features(df)
    else:
        df = make_features(df)

    artifact = fit_production_model(df, horizon=5, pt_atr=2.0, sl_atr=1.0, model_id="nse-production")
    out_dir = Path("data/processed/models")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "nse-production.joblib"
    save_artifact(artifact, str(path))

    reg = ModelRegistry()
    reg.register("nse-production", artifact.contract_hash, {
        "artifact_path": str(path),
        "trained_through": artifact.trained_through,
        "features": len(artifact.features)
    })
    # Set as champion
    reg.set_champion("nse-production")
    print("Successfully bootstrapped and registered champion model:", artifact.model_id)

if __name__ == "__main__":
    bootstrap()
