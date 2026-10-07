"""Adversarial tests for the production model lifecycle ensuring fail-closed champion selection and artifact validation."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nse_signal.models.registry import ModelRegistry
from nse_signal.models.production import load_artifact, ProductionArtifact

def test_champion_promotion_fails_without_governance_pass(tmp_path):
    reg_path = tmp_path / "registry.json"
    registry = ModelRegistry(str(reg_path))
    mod = registry.register("test-model", "hash123", {"gate": {"pass": False}})
    registry.transition("test-model", "VALIDATED")
    registry.transition("test-model", "PAPER")
    with pytest.raises(ValueError, match="champion promotion requires metrics.gate.pass=true"):
        registry.transition("test-model", "CHAMPION")

def test_missing_model_artifact_raises_file_not_found(tmp_path):
    missing_path = tmp_path / "nonexistent.joblib"
    with pytest.raises(FileNotFoundError):
        load_artifact(str(missing_path))

def test_incompatible_artifact_version_fails_closed(tmp_path):
    art_path = tmp_path / "old.joblib"
    art = ProductionArtifact(
        model_id="old",
        features=["f1"],
        median_values={"f1": 0.0},
        models=[],
        calibrator=None,
        trained_through="2020-01-01",
        contract_hash="abc",
        conformal_version=1
    )
    import joblib
    joblib.dump(art, art_path)
    with pytest.raises(ValueError, match="Incompatible artifact version"):
        load_artifact(str(art_path))
