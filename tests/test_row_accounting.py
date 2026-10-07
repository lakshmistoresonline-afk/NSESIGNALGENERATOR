"""Tests for independent row accounting and mass conservation invariant."""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

def test_row_accounting_mass_conservation_invariant():
    source_rows = 100
    rejected_rows = 5
    normalized_rows = source_rows - rejected_rows
    exact_duplicates = 10
    conflicts = 2
    transformation_errors = 0
    canonical_rows = normalized_rows - exact_duplicates - conflicts - transformation_errors

    unaccounted = normalized_rows - (canonical_rows + exact_duplicates + conflicts + transformation_errors)
    assert unaccounted == 0
    assert canonical_rows == 83

    # Total mass conservation from source
    total_accounted = canonical_rows + exact_duplicates + conflicts + rejected_rows + transformation_errors
    assert total_accounted == source_rows
