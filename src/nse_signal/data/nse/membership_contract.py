"""Canonical Compatibility Wrapper for Historical-Universe Contract."""
from __future__ import annotations
import pandas as pd
from .membership import validate_half_open_membership

def validate_membership(df: pd.DataFrame) -> pd.DataFrame:
    """Compatibility wrapper delegates directly to canonical membership validation."""
    return validate_half_open_membership(df)
