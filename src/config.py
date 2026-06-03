from pathlib import Path

DATA_DIR = Path("data")

# Geological formation column names present in horizontal well files
FORMATION_COLUMNS = ["ANCC", "ASTNU", "ASTNL", "EGFDU", "EGFDL", "BUDA"]

# Consistent colors for formation curves across all charts
FORMATION_COLORS: dict[str, str] = {
    "ANCC": "red",
    "ASTNU": "orange",
    "ASTNL": "purple",
    "EGFDU": "green",
    "EGFDL": "cyan",
    "BUDA": "magenta",
}

# Columns that must be present for a horizontal well file to be usable
HORIZONTAL_REQUIRED_COLS: list[str] = ["MD", "X", "Y", "Z", "GR"]

# Columns that must be present for a typewell file to be usable
TYPEWELL_REQUIRED_COLS: list[str] = ["TVT", "GR", "Geology"]

# Default display range for GR on TVT plots
GR_RANGE: list[int] = [0, 200]
