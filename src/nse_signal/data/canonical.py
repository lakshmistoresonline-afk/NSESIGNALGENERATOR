"""Canonical data models and PIT provenance schemas for V31 free/public NSE reconstruction."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Literal

QualityStatus = Literal["AUTHORITATIVE_PUBLIC", "SECONDARY_CONFIRMED", "RECONSTRUCTED", "UNVERIFIED", "MISSING"]
ReconstructionStatus = Literal["RAW", "NORMALIZED", "RECONCILED", "PIT_VALIDATED", "REJECTED"]

@dataclass(frozen=True)
class DataProvenance:
    signal_timestamp: str
    market_timestamp: str
    sources_used: list[str]
    source_priority: str
    data_age_seconds: float
    cross_provider_agreement: float
    quality_score: float
    pit_status: str
    fields_missing: list[str]
    reconstruction_status: ReconstructionStatus
    raw_file_hash: Optional[str] = None
    source_url_or_identifier: Optional[str] = None

@dataclass(frozen=True)
class InstrumentPIT:
    instrument_id: str
    symbol: str
    exchange: str
    segment: str
    event_date: str
    effective_from: str
    effective_to: Optional[str]
    ingested_at: str
    source: str
    source_type: str
    source_url_or_identifier: Optional[str]
    retrieval_timestamp: str
    raw_file_hash: Optional[str]
    quality_status: QualityStatus
    reconstruction_status: ReconstructionStatus
    isin: Optional[str] = None
    series: Optional[str] = None

@dataclass(frozen=True)
class PriceBar:
    instrument_id: str
    symbol: str
    exchange: str
    segment: str
    event_date: str
    effective_from: str
    effective_to: Optional[str]
    ingested_at: str
    source: str
    source_type: str
    source_url_or_identifier: Optional[str]
    retrieval_timestamp: str
    raw_file_hash: Optional[str]
    quality_status: QualityStatus
    reconstruction_status: ReconstructionStatus
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: Optional[float] = None
    deliverable_volume: Optional[float] = None
    delivery_pct: Optional[float] = None

@dataclass(frozen=True)
class DerivativeContractPIT:
    instrument_id: str
    symbol: str
    exchange: str
    segment: str
    event_date: str
    effective_from: str
    effective_to: Optional[str]
    ingested_at: str
    source: str
    source_type: str
    source_url_or_identifier: Optional[str]
    retrieval_timestamp: str
    raw_file_hash: Optional[str]
    quality_status: QualityStatus
    reconstruction_status: ReconstructionStatus
    underlying: str
    instrument_type: str
    expiry: str
    strike: float
    option_type: str
    settlement_price: float

@dataclass(frozen=True)
class OpenInterestPIT:
    instrument_id: str
    symbol: str
    exchange: str
    segment: str
    event_date: str
    effective_from: str
    effective_to: Optional[str]
    ingested_at: str
    source: str
    source_type: str
    source_url_or_identifier: Optional[str]
    retrieval_timestamp: str
    raw_file_hash: Optional[str]
    quality_status: QualityStatus
    reconstruction_status: ReconstructionStatus
    open_interest: float
    change_in_oi: float
    futures_basis: Optional[float] = None
    pcr: Optional[float] = None

@dataclass(frozen=True)
class DeliveryPIT:
    instrument_id: str
    symbol: str
    exchange: str
    segment: str
    event_date: str
    effective_from: str
    effective_to: Optional[str]
    ingested_at: str
    source: str
    source_type: str
    source_url_or_identifier: Optional[str]
    retrieval_timestamp: str
    raw_file_hash: Optional[str]
    quality_status: QualityStatus
    reconstruction_status: ReconstructionStatus
    traded_quantity: float
    deliverable_quantity: float
    delivery_percentage: float

@dataclass(frozen=True)
class CorporateActionPIT:
    instrument_id: str
    symbol: str
    exchange: str
    segment: str
    event_date: str
    effective_from: str
    effective_to: Optional[str]
    ingested_at: str
    source: str
    source_type: str
    source_url_or_identifier: Optional[str]
    retrieval_timestamp: str
    raw_file_hash: Optional[str]
    quality_status: QualityStatus
    reconstruction_status: ReconstructionStatus
    action_type: Literal["SPLIT", "BONUS", "RIGHTS", "DIVIDEND", "MERGER", "DEMERGER", "SYMBOL_CHANGE"]
    ratio: float
    ex_date: str
    record_date: Optional[str] = None

@dataclass(frozen=True)
class IndexMembershipPIT:
    instrument_id: str
    symbol: str
    exchange: str
    segment: str
    event_date: str
    effective_from: str
    effective_to: Optional[str]
    ingested_at: str
    source: str
    source_type: str
    source_url_or_identifier: Optional[str]
    retrieval_timestamp: str
    raw_file_hash: Optional[str]
    quality_status: QualityStatus
    reconstruction_status: ReconstructionStatus
    index_name: str
    membership_status: Literal["MEMBER", "ADDED", "REMOVED", "UNKNOWN"]

@dataclass(frozen=True)
class SymbolHistoryPIT:
    instrument_id: str
    symbol: str
    exchange: str
    segment: str
    event_date: str
    effective_from: str
    effective_to: Optional[str]
    ingested_at: str
    source: str
    source_type: str
    source_url_or_identifier: Optional[str]
    retrieval_timestamp: str
    raw_file_hash: Optional[str]
    quality_status: QualityStatus
    reconstruction_status: ReconstructionStatus
    old_symbol: str
    new_symbol: str
    reason: str

@dataclass(frozen=True)
class MarketBreadthPIT:
    instrument_id: str
    symbol: str
    exchange: str
    segment: str
    event_date: str
    effective_from: str
    effective_to: Optional[str]
    ingested_at: str
    source: str
    source_type: str
    source_url_or_identifier: Optional[str]
    retrieval_timestamp: str
    raw_file_hash: Optional[str]
    quality_status: QualityStatus
    reconstruction_status: ReconstructionStatus
    advances: int
    declines: int
    unchanged: int
    advance_decline_ratio: float

@dataclass(frozen=True)
class VolatilityPIT:
    instrument_id: str
    symbol: str
    exchange: str
    segment: str
    event_date: str
    effective_from: str
    effective_to: Optional[str]
    ingested_at: str
    source: str
    source_type: str
    source_url_or_identifier: Optional[str]
    retrieval_timestamp: str
    raw_file_hash: Optional[str]
    quality_status: QualityStatus
    reconstruction_status: ReconstructionStatus
    india_vix: float
    realized_vol_20: Optional[float] = None
