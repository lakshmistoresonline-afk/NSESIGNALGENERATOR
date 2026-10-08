"""Canonical Signal Data Contract: Enforces strict schema validation, deterministic signal identity hashing, and serialization/deserialization across LIVE and HISTORICAL generation modes."""
from __future__ import annotations
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
import hashlib
import json
from typing import Optional, Dict, Any

@dataclass(frozen=True)
class CanonicalSignal:
    signal_id: str
    symbol: str
    security_id: str
    isin: str
    exchange: str
    universe: str
    signal_type: str
    side: str
    signal_time: str
    asof_time: str
    market_date: str
    timeframe: str
    price: float
    entry_price: float
    stop_price: float
    target_price: float
    probability_up: float
    probability_down: float
    confidence: float
    quality_score: float
    model_name: str
    model_version: str
    model_hash: str
    feature_version: str
    feature_hash: str
    calibration_version: str
    conformal_version: str
    risk_gate_status: str
    publication_status: str
    data_freshness: str
    pit_provenance_verified: bool
    signal_only: bool = True
    real_trading: bool = False
    generation_mode: str = "LIVE"
    historical_asof_date: Optional[str] = None
    historical_run_id: Optional[str] = None
    live_session_id: Optional[str] = None
    latest_market_timestamp: Optional[str] = None

    @staticmethod
    def generate_signal_id(symbol: str, signal_time: str, timeframe: str, model_version: str, side: str, generation_mode: str) -> str:
        raw = f"{symbol}|{signal_time}|{timeframe}|{model_version}|{side}|{generation_mode}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def validate(self) -> tuple[bool, list[str]]:
        errors = []
        if self.real_trading is not False:
            errors.append("REAL_TRADING must be False")
        if self.signal_only is not True:
            errors.append("signal_only must be True")
        if self.generation_mode not in {"LIVE", "HISTORICAL"}:
            errors.append(f"Invalid generation_mode: {self.generation_mode}")
        if self.generation_mode == "HISTORICAL" and not self.historical_asof_date:
            errors.append("HISTORICAL mode requires historical_asof_date")
        if self.generation_mode == "LIVE" and not self.live_session_id:
            errors.append("LIVE mode requires live_session_id")
        if not 0 <= self.probability_up <= 1:
            errors.append("probability_up must be between 0 and 1")
        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CanonicalSignal:
        return cls(**data)
