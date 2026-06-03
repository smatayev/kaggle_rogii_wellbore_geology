import re
from pathlib import Path
from typing import Dict

import pandas as pd

from src.config import DATA_DIR

# File-name patterns: {8-char hex}__horizontal_well.csv / __typewell.csv
_HORIZONTAL_RE = re.compile(r"^(?P<well_id>[0-9a-f]{8})__horizontal_well\.csv$")
_TYPEWELL_RE = re.compile(r"^(?P<well_id>[0-9a-f]{8})__typewell\.csv$")


def scan_well_files(data_dir: Path = DATA_DIR) -> Dict[str, Path]:
    """Scan data_dir for horizontal well CSV files. Returns {well_id: path}."""
    result: Dict[str, Path] = {}
    if not data_dir.exists():
        return result
    for path in sorted(data_dir.glob("*.csv")):
        m = _HORIZONTAL_RE.match(path.name)
        if m:
            result[m.group("well_id")] = path
    return result


def scan_typewell_files(data_dir: Path = DATA_DIR) -> Dict[str, Path]:
    """Scan data_dir for typewell CSV files. Returns {well_id: path}."""
    result: Dict[str, Path] = {}
    if not data_dir.exists():
        return result
    for path in sorted(data_dir.glob("*.csv")):
        m = _TYPEWELL_RE.match(path.name)
        if m:
            result[m.group("well_id")] = path
    return result


def load_horizontal_well(path: Path) -> pd.DataFrame:
    """Load a horizontal well CSV and coerce all columns to numeric where possible."""
    df = pd.read_csv(path)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_typewell(path: Path) -> pd.DataFrame:
    """
    Load a typewell CSV.
    Geology is kept as string; TVT and GR are coerced to numeric.
    """
    df = pd.read_csv(path)
    for col in ["TVT", "GR"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df
