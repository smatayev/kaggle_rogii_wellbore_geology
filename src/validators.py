from typing import List

import pandas as pd

from src.config import HORIZONTAL_REQUIRED_COLS, TYPEWELL_REQUIRED_COLS


def validate_horizontal_well(df: pd.DataFrame) -> List[str]:
    """
    Validate a horizontal well DataFrame.
    Returns a list of human-readable error strings (empty means valid).
    """
    errors: List[str] = []

    if df is None or df.empty:
        return ["DataFrame is empty or could not be loaded."]

    for col in HORIZONTAL_REQUIRED_COLS:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")
        elif df[col].dropna().empty:
            errors.append(f"Column '{col}' contains no valid values (all NaN).")

    return errors


def validate_typewell(df: pd.DataFrame) -> List[str]:
    """
    Validate a typewell DataFrame.
    Returns a list of human-readable error strings (empty means valid).
    Geology is allowed to have NaN values — it is only warned, not an error.
    """
    errors: List[str] = []

    if df is None or df.empty:
        return ["DataFrame is empty or could not be loaded."]

    for col in TYPEWELL_REQUIRED_COLS:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")
        elif col != "Geology" and df[col].dropna().empty:
            errors.append(f"Column '{col}' contains no valid values (all NaN).")

    return errors
