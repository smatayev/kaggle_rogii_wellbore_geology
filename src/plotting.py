from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go

from src.config import FORMATION_COLORS, FORMATION_COLUMNS, GR_RANGE

# ---------------------------------------------------------------------------
# Shared dashboard style
# ---------------------------------------------------------------------------

_TITLE_FONT = {"size": 15, "color": "#1a1a2e", "family": "Arial Black, Arial, sans-serif"}
_AXIS_FONT  = {"size": 12, "color": "#333333", "family": "Arial, sans-serif"}
_TICK_FONT  = {"size": 11, "color": "#555555", "family": "Arial, sans-serif"}

_GRID_COLOR  = "rgba(200, 210, 220, 0.6)"
_ZERO_COLOR  = "rgba(150, 160, 175, 0.8)"
_PAPER_COLOR = "#ffffff"
_PLOT_COLOR  = "#f8f9fc"


def _axis_style(title: str, **extra: Any) -> Dict:
    """Return a consistent axis config dict for one axis."""
    cfg: Dict = {
        "title": {"text": title, "font": _AXIS_FONT, "standoff": 10},
        "tickfont": _TICK_FONT,
        "gridcolor": _GRID_COLOR,
        "gridwidth": 1,
        "zeroline": True,
        "zerolinecolor": _ZERO_COLOR,
        "zerolinewidth": 1,
        "showgrid": True,
        "linecolor": "#cccccc",
        "linewidth": 1,
        "showline": True,
        "ticks": "outside",
        "ticklen": 4,
    }
    cfg.update(extra)
    return cfg


def _base_layout(**extra: Any) -> Dict:
    """Return the shared layout dict applied to every dashboard figure."""
    layout: Dict = {
        "template": "plotly_white",
        "paper_bgcolor": _PAPER_COLOR,
        "plot_bgcolor": _PLOT_COLOR,
        "font": {"family": "Arial, sans-serif", "size": 12, "color": "#333333"},
        "title_font": _TITLE_FONT,
        "title_x": 0.0,
        "title_xanchor": "left",
        "title_pad": {"l": 4, "t": 4},
        "legend": {
            "bgcolor": "rgba(255,255,255,0.85)",
            "bordercolor": "#cccccc",
            "borderwidth": 1,
            "font": {"size": 11, "color": "#333333"},
            "x": 1.02,
            "y": 1.0,
            "xanchor": "left",
            "yanchor": "top",
        },
        "margin": {"l": 60, "r": 20, "t": 60, "b": 50},
        "hoverlabel": {"bgcolor": "white", "bordercolor": "#aaaaaa",
                       "font_size": 12, "font_family": "Arial, sans-serif"},
    }
    layout.update(extra)
    return layout


def make_gr_figure(df: pd.DataFrame, proj_x: pd.Series) -> go.Figure:
    """
    Gamma Ray Log: GR (y-axis) vs projected horizontal distance (x-axis).
    X-axis matches the Well Path Projection below it for direct visual correlation.
    Black line with a green filled area underneath (fill='tozeroy').
    """
    fig = go.Figure()

    plot_df = pd.DataFrame({"proj": proj_x, "GR": df["GR"]}).dropna()

    fig.add_trace(
        go.Scatter(
            x=plot_df["proj"],
            y=plot_df["GR"],
            mode="lines",
            line={"color": "black", "width": 1.5},
            fill="tozeroy",
            fillcolor="rgba(0, 160, 0, 0.25)",
            name="GR",
        )
    )

    fig.update_layout(
        **_base_layout(
            title="Gamma Ray Log",
            showlegend=False,
            margin={"l": 60, "r": 20, "t": 60, "b": 50},
            height=400,
        ),
        xaxis=_axis_style("Horizontal Distance Along Azimuth (m)"),
        yaxis=_axis_style("GR (API)"),
    )
    return fig


def make_well_path_figure(
    df: pd.DataFrame,
    azimuth: float,
    proj_x: pd.Series,
    prediction_start: Optional[Tuple[float, int]] = None,
) -> go.Figure:
    """
    Well Path Projection on Vertical Plane.

    X-axis = projected horizontal distance along azimuth — same scale as GR Log.
    Y-axis = Z (True Vertical Depth). Z values are stored as negative numbers
    (depth below sea level), so no axis reversal is needed: Plotly's default
    ascending y-axis places shallower (less-negative) values at the top and
    deeper (more-negative) values at the bottom — depth increases downward.

    Legend is rendered inside the plot area so both left-column charts have
    identical widths.

    Includes:
    - Thick blue well path line
    - Red circle marker at prediction start (first NaN TVT_input row), if found
    - Dotted colored lines for each present formation column (ANCC, ASTNU, etc.)
    """
    fig = go.Figure()

    # Well path trace — projected horizontal distance vs Z
    path_df = pd.DataFrame({"proj": proj_x, "Z": df["Z"]}).dropna()
    fig.add_trace(
        go.Scatter(
            x=path_df["proj"],
            y=path_df["Z"],
            mode="lines",
            line={"color": "blue", "width": 3},
            name="Well Path",
        )
    )

    # Prediction start marker
    if prediction_start is not None:
        md_val, row_idx = prediction_start
        if row_idx in proj_x.index and pd.notna(proj_x.loc[row_idx]):
            px_val = float(proj_x.loc[row_idx])
            z_val = None
            if "Z" in df.columns and pd.notna(df.loc[row_idx, "Z"]):
                z_val = float(df.loc[row_idx, "Z"])
            if z_val is not None:
                fig.add_trace(
                    go.Scatter(
                        x=[px_val],
                        y=[z_val],
                        mode="markers+text",
                        marker={"color": "red", "size": 12, "symbol": "circle"},
                        text=[f"Prediction start (MD={md_val:.0f} ft)"],
                        textposition="top right",
                        name="Prediction Start",
                    )
                )

    # Formation surface lines — projected horizontal distance vs formation depth
    for formation in FORMATION_COLUMNS:
        if formation not in df.columns:
            continue
        f_df = pd.DataFrame({"proj": proj_x, "val": df[formation]}).dropna()
        if f_df.empty:
            continue
        color = FORMATION_COLORS.get(formation, "gray")
        fig.add_trace(
            go.Scatter(
                x=f_df["proj"],
                y=f_df["val"],
                mode="lines",
                line={"color": color, "width": 1.5, "dash": "dot"},
                name=formation,
                opacity=0.85,
            )
        )

    fig.update_layout(
        **_base_layout(
            title=f"Well Path Projection — Azimuth {azimuth:.1f}°",
            # Right margin matches GR chart (no space reserved for outside legend)
            margin={"l": 60, "r": 20, "t": 60, "b": 50},
            height=400,
            legend={
                # Inside overlay: top-right, white 50% transparent, with border
                "x": 0.99,
                "y": 0.99,
                "xanchor": "right",
                "yanchor": "top",
                "bgcolor": "rgba(255, 255, 255, 0.5)",
                "bordercolor": "#aaaaaa",
                "borderwidth": 1,
                "font": {"size": 11, "color": "#333333"},
            },
        ),
        xaxis=_axis_style("Horizontal Distance Along Azimuth (m)"),
        # No autorange reversal — Z is negative-downward so default ordering is correct
        yaxis=_axis_style("Depth — Z (ft)"),
    )
    return fig


def make_tvt_figure(
    h_df: pd.DataFrame,
    t_df: pd.DataFrame,
    boundaries: List[Dict],
) -> go.Figure:
    """
    TVT plot: GR vs TVT for horizontal well (black solid) and typewell (red dotted).

    Y-axis is reversed so depth increases downward.
    GR x-range defaults to 0–200.
    Horizontal dashed lines mark geology formation boundaries derived from typewell.
    """
    fig = _build_tvt_base(h_df, t_df, boundaries)

    fig.update_layout(
        title="TVT Correlation",
        xaxis=_axis_style("GR (API)", range=GR_RANGE),
        yaxis=_axis_style("TVT (ft)", autorange="reversed"),
    )

    fig.add_annotation(
        text="GR range: 0–200",
        xref="paper", yref="paper",
        x=0.01, y=1.06,
        showarrow=False,
        font={"size": 10, "color": "#888888", "family": "Arial, sans-serif"},
        xanchor="left",
    )

    return fig


def make_tvt_zoom_figure(
    h_df: pd.DataFrame,
    t_df: pd.DataFrame,
    boundaries: List[Dict],
) -> go.Figure:
    """
    TVT plot (last 200 FT): same as TVT plot but y-range clamped to
    [max_tvt - 200, max_tvt] so the viewer sees the deepest 200 ft interval.
    """
    fig = _build_tvt_base(h_df, t_df, boundaries)

    # Determine max TVT across both sources
    max_tvt: Optional[float] = None
    for source_df in [h_df, t_df]:
        if "TVT" in source_df.columns:
            col_max = source_df["TVT"].dropna().max()
            if pd.notna(col_max):
                val = float(col_max)
                max_tvt = val if max_tvt is None else max(max_tvt, val)

    y_range = [max_tvt - 200, max_tvt] if max_tvt is not None else None

    yaxis_cfg: Dict = {"autorange": False}
    if y_range is not None:
        # Plotly reversed + explicit range: set autorange=False then apply range.
        # Use [shallow, deep] — Plotly reversal shows deep at bottom.
        yaxis_cfg["range"] = [y_range[0], y_range[1]]
        yaxis_cfg["autorange"] = "reversed"
    else:
        yaxis_cfg["autorange"] = "reversed"

    # Merge shared axis style FIRST, then overlay the range/autorange values
    merged = _axis_style("TVT (ft)")
    merged.update(yaxis_cfg)
    yaxis_cfg = merged

    fig.update_layout(
        title="TVT Correlation — Last 200 ft",
        xaxis=_axis_style("GR (API)", range=GR_RANGE),
        yaxis=yaxis_cfg,
    )

    fig.add_annotation(
        text="GR range: 0–200",
        xref="paper", yref="paper",
        x=0.01, y=1.06,
        showarrow=False,
        font={"size": 10, "color": "#888888", "family": "Arial, sans-serif"},
        xanchor="left",
    )

    return fig


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _build_tvt_base(
    h_df: pd.DataFrame,
    t_df: pd.DataFrame,
    boundaries: List[Dict],
) -> go.Figure:
    """
    Shared base for both TVT figures.

    Adds:
    - Horizontal well GR vs TVT (black solid line)
    - Typewell GR vs TVT (red dotted line)
    - Horizontal dashed lines at geology boundary depths
    - Formation name annotations on the right margin
    """
    fig = go.Figure()

    # Horizontal well curve (black) — slightly thicker for readability
    if "TVT" in h_df.columns and "GR" in h_df.columns:
        h_plot = h_df[["TVT", "GR"]].dropna()
        if not h_plot.empty:
            fig.add_trace(
                go.Scatter(
                    x=h_plot["GR"],
                    y=h_plot["TVT"],
                    mode="lines",
                    line={"color": "#111111", "width": 2},
                    name="Horizontal Well",
                )
            )

    # Typewell curve (red dashed)
    if "TVT" in t_df.columns and "GR" in t_df.columns:
        t_plot = t_df[["TVT", "GR"]].dropna()
        if not t_plot.empty:
            fig.add_trace(
                go.Scatter(
                    x=t_plot["GR"],
                    y=t_plot["TVT"],
                    mode="lines",
                    line={"color": "#cc0000", "width": 2, "dash": "dot"},
                    name="Typewell",
                )
            )

    # Geology boundary horizontal dashed lines
    for boundary in boundaries:
        fig.add_shape(
            type="line",
            x0=0, x1=1,
            xref="paper",
            y0=boundary["tvt"],
            y1=boundary["tvt"],
            yref="y",
            line={"color": boundary["color"], "width": 1.5, "dash": "dash"},
        )
        # Formation label pinned to right margin
        fig.add_annotation(
            text=f"<b>{boundary['name']}</b>",
            x=1.01,
            y=boundary["tvt"],
            xref="paper",
            yref="y",
            showarrow=False,
            font={"size": 10, "color": boundary["color"], "family": "Arial, sans-serif"},
            xanchor="left",
        )

    fig.update_layout(
        **_base_layout(
            margin={"l": 60, "r": 110, "t": 60, "b": 50},
            height=820,
        ),
    )

    return fig
