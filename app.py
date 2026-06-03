import streamlit as st

from src.calculations import (
    compute_azimuth,
    compute_projection,
    extract_geology_boundaries,
    find_prediction_start,
)
from src.data_loader import (
    load_horizontal_well,
    load_typewell,
    scan_typewell_files,
    scan_well_files,
)
from src.plotting import (
    make_gr_figure,
    make_tvt_figure,
    make_tvt_zoom_figure,
    make_well_path_figure,
)
from src.validators import validate_horizontal_well, validate_typewell

st.set_page_config(page_title="Wellbore Geology Visualizer", layout="wide")

# ---------------------------------------------------------------------------
# Scan available data files
# ---------------------------------------------------------------------------

well_files = scan_well_files()
typewell_files = scan_typewell_files()

if not well_files:
    st.error(
        "No horizontal well files found in data/. "
        "Expected pattern: {WELLID}__horizontal_well.csv"
    )
    st.stop()

if not typewell_files:
    st.error(
        "No typewell files found in data/. "
        "Expected pattern: {WELLID}__typewell.csv"
    )
    st.stop()

well_options = sorted(well_files.keys())
all_typewell_options = sorted(typewell_files.keys())

# ---------------------------------------------------------------------------
# Header: title + dropdowns
# ---------------------------------------------------------------------------

st.title("Wellbore Geology Visualizer")

# Well selector comes first so we can use its value to filter typewells.
col_w, col_filter, col_t = st.columns([2, 1, 2])

with col_w:
    selected_well = st.selectbox("Select Well", well_options, index=0)

# Determine which typewells share the same well-ID prefix as the selected well.
matched_typewells = [tw for tw in all_typewell_options if tw == selected_well]
has_match = bool(matched_typewells)

with col_filter:
    # Push the checkbox down a bit so it aligns with the dropdowns.
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    filter_to_match = st.checkbox(
        "Matched only",
        value=has_match,          # on by default when a match exists
        disabled=not has_match,   # greyed out when no match found
        help=(
            "When checked, only the typewell with the same well ID as the "
            "selected horizontal well is shown. Uncheck to browse all typewells."
        ),
    )

# Decide which options to expose in the typewell dropdown.
if filter_to_match and has_match:
    typewell_options = matched_typewells
    # Auto-select the matching entry.
    typewell_default_idx = 0
else:
    typewell_options = all_typewell_options
    # When showing all, try to keep the matching typewell pre-selected if present.
    typewell_default_idx = (
        typewell_options.index(selected_well)
        if selected_well in typewell_options
        else 0
    )

with col_t:
    hint = (
        f"✓ Matched to well **{selected_well}**"
        if filter_to_match and has_match
        else (
            f"⚠ No typewell for **{selected_well}** — showing all"
            if not has_match
            else "Showing all typewells"
        )
    )
    st.caption(hint)
    selected_typewell = st.selectbox(
        "Select Typewell",
        typewell_options,
        index=typewell_default_idx,
    )

# ---------------------------------------------------------------------------
# Load and validate data
# ---------------------------------------------------------------------------

h_df = None
t_df = None
h_errors: list[str] = []
t_errors: list[str] = []

try:
    h_df = load_horizontal_well(well_files[selected_well])
    h_errors = validate_horizontal_well(h_df)
except Exception as e:
    h_errors = [f"Failed to load well file: {e}"]

try:
    t_df = load_typewell(typewell_files[selected_typewell])
    t_errors = validate_typewell(t_df)
except Exception as e:
    t_errors = [f"Failed to load typewell file: {e}"]

for err in h_errors:
    st.warning(f"Horizontal well — {err}")
for err in t_errors:
    st.warning(f"Typewell — {err}")

# ---------------------------------------------------------------------------
# Compute azimuth and show info line
# ---------------------------------------------------------------------------

azimuth = None
if h_df is not None and not h_errors:
    azimuth = compute_azimuth(h_df)

azimuth_display = f"{azimuth:.1f}°" if azimuth is not None else "N/A"
st.info(
    f"Well: **{selected_well}** | Typewell: **{selected_typewell}** | "
    f"Azimuth = **{azimuth_display}**"
)

# Stop rendering charts if critical data is missing
if h_errors or t_errors:
    st.stop()

# ---------------------------------------------------------------------------
# Compute derived values
# ---------------------------------------------------------------------------

proj_x = compute_projection(h_df, azimuth) if azimuth is not None else None
prediction_start = find_prediction_start(h_df)
boundaries = extract_geology_boundaries(t_df) if t_df is not None else []

has_tvt = (
    "TVT" in h_df.columns
    and h_df["TVT"].dropna().shape[0] > 0
)

# ---------------------------------------------------------------------------
# Layout: left large column | middle narrow | right narrow
# ---------------------------------------------------------------------------
# Ratio 3 : 1.5 : 1.5 approximated as [4, 2, 2] for st.columns integer weights

col1, col2, col3 = st.columns([4, 2, 2])

with col1:
    # 1. Gamma Ray Log
    if "GR" in h_df.columns and proj_x is not None:
        st.plotly_chart(make_gr_figure(h_df, proj_x), use_container_width=True)
    else:
        st.warning("Gamma Ray Log unavailable: missing GR column or no valid X/Y for projection.")

    # 2. Well Path Projection — same x-axis as GR Log (horizontal distance along azimuth)
    if azimuth is not None and proj_x is not None:
        st.plotly_chart(
            make_well_path_figure(h_df, azimuth, proj_x, prediction_start),
            use_container_width=True,
        )
    else:
        st.warning(
            "Well Path Projection unavailable: "
            "could not compute azimuth (no valid X/Y points)."
        )

with col2:
    # 3. TVT plot
    if has_tvt:
        st.plotly_chart(
            make_tvt_figure(h_df, t_df, boundaries),
            use_container_width=True,
        )
    else:
        st.warning(
            "TVT plot unavailable: horizontal well has no TVT column "
            "or all TVT values are NaN."
        )

with col3:
    # 4. TVT plot (last 200 FT)
    if has_tvt:
        st.plotly_chart(
            make_tvt_zoom_figure(h_df, t_df, boundaries),
            use_container_width=True,
        )
    else:
        st.warning(
            "TVT plot (last 200 FT) unavailable: horizontal well has no TVT column "
            "or all TVT values are NaN."
        )
