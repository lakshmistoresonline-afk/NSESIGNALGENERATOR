"""Iteration 9.9 Forensic Framework: Data Models."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ExecutionEvidence:
    command: str
    cwd: str
    start_time: str
    end_time: str
    duration_seconds: float
    exit_code: int
    stdout: str
    stderr: str

@dataclass
class MutationRecord:
    mutation_id: str
    description: str
    target_file: str
    original_sha256: str
    mutated_sha256: str
    mutation_applied: bool
    validator_exit_code: int
    expected_check_id: str
    actual_detected: bool
    restored: bool
    restored_sha256: str
    status: str
    evidence_output: str

@dataclass
class TestOfTestRecord:
    baseline_detected: bool
    weakened_detection_lost: bool
    restored_detection_returned: bool
    validator_baseline_hash: str
    validator_weakened_hash: str
    validator_restored_hash: str
    status: str
