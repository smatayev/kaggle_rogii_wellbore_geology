import math
from typing import Dict, List, Optional, Tuple

import pandas as pd

from src.config import FORMATION_COLORS


def compute_azimuth(df: pd.DataFrame) -> Optional[float]:
    """
    Compute azimuth from the first and last valid (X, Y) points.

    Convention: 0° = North, 90° = East, clockwise (standard geographic azimuth).
    Returns azimuth in degrees, or None if fewer than 2 valid points exist.
    """
    valid = df[["X", "Y"]].dropna()
    if len(valid) < 2:
        return None

    x0, y0 = float(valid.iloc[0]["X"]), float(valid.iloc[0]["Y"])
    x1, y1 = float(valid.iloc[-1]["X"]), float(valid.iloc[-1]["Y"])

    dx = x1 - x0  # East delta
    dy = y1 - y0  # North delta

    # atan2(east, north) gives clockwise-from-North azimuth
    azimuth = math.degrees(math.atan2(dx, dy)) % 360
    return round(azimuth, 1)


def compute_projection(df: pd.DataFrame, azimuth: float) -> pd.Series:
    """
    Project (X, Y) coordinates onto the azimuth direction.

    Returns a Series of projected horizontal distances relative to the first valid
    point. Rows with NaN X or Y are returned as NaN.

    Unit vector along azimuth (clockwise from North):
        u = (sin(az), cos(az))  in (East=X, North=Y) space
    """
    az_rad = math.radians(azimuth)
    ux = math.sin(az_rad)  # East (X) component
    uy = math.cos(az_rad)  # North (Y) component

    valid_mask = df["X"].notna() & df["Y"].notna()

    proj = pd.Series(float("nan"), index=df.index)

    if not valid_mask.any():
        return proj

    # Anchor to first valid point so projection starts at 0
    first_idx = valid_mask.idxmax()
    x0 = float(df.loc[first_idx, "X"])
    y0 = float(df.loc[first_idx, "Y"])

    proj.loc[valid_mask] = (
        (df.loc[valid_mask, "X"] - x0) * ux
        + (df.loc[valid_mask, "Y"] - y0) * uy
    )

    return proj


def find_prediction_start(df: pd.DataFrame) -> Optional[Tuple[float, int]]:
    """
    Find the first row where TVT_input is NaN.

    Returns (MD value, row index) or None if the column is absent or fully populated.
    This marks the boundary between the known zone and the prediction zone.
    """
    if "TVT_input" not in df.columns:
        return None

    nan_rows = df[df["TVT_input"].isna()]
    if nan_rows.empty:
        return None

    first_idx = int(nan_rows.index[0])
    md_val = float(df.loc[first_idx, "MD"]) if "MD" in df.columns else float("nan")
    return (md_val, first_idx)


def extract_geology_boundaries(df: pd.DataFrame) -> List[Dict]:
    """
    Detect Geology column transitions in a typewell DataFrame.

    A boundary is recorded at the TVT of the first row of each new formation unit.
    Returns a list of dicts: [{"tvt": float, "name": str, "color": str}, ...].

    Color is looked up from FORMATION_COLORS; unknown formations use gray.
    NaN Geology values and NaN TVT values are skipped silently.
    """
    if "Geology" not in df.columns or "TVT" not in df.columns:
        return []

    boundaries: List[Dict] = []
    prev_geo: Optional[str] = None

    for _, row in df.iterrows():
        geo = row["Geology"]
        tvt = row["TVT"]

        # Skip rows with missing data
        if pd.isna(geo) or pd.isna(tvt):
            continue

        geo = str(geo)

        if prev_geo is not None and geo != prev_geo:
            color = FORMATION_COLORS.get(geo, "gray")
            boundaries.append({"tvt": float(tvt), "name": geo, "color": color})

        prev_geo = geo

    return boundaries
