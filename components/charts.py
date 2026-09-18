from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from utils.formatting import compact_money, roi_text

_POSITIVE = "#22C55E"
_NEGATIVE = "#EF4444"
_BRAND = "#1A56DB"
_TEAL = "#0EA5E9"
_VIOLET = "#8B5CF6"
_AMBER = "#F59E0B"


# ── Sensitivity sweep helper ──────────────────────────────────────────────────

def _sweep_param(
    calc_fn,
    base_values: Dict[str, Any],
    param_key: str,
    base_val: float,
    pct_range: float = 0.30,
    steps: int = 11,
) -> Tuple[List[float], List[float], List[float]]:
    """Sweep param_key ±pct_range around base_val and return (x, roi_y, net_y)."""
    lo = base_val * (1 - pct_range)
    hi = base_val * (1 + pct_range)
    xs = np.linspace(lo, hi, steps)
    rois, nets = [], []
    for x in xs:
        trial = {**base_values, param_key: float(x)}
        try:
            r = calc_fn(trial)
            rois.append(float(r.metrics.get("roi", 0)))
            nets.append(float(r.metrics.get("net_profit_total", 0)))
        except Exception:
            rois.append(0.0)
            nets.append(0.0)
    return list(xs), rois, nets


# ── Tornado Chart ─────────────────────────────────────────────────────────────

def render_tornado_chart(
    calc_fn,
    base_values: Dict[str, Any],
    base_roi: float,
    sweep_keys: List[Tuple[str, str]],
) -> None:
    """
    Horizontal tornado chart showing ROI sensitivity.

    Parameters
    ----------
    calc_fn    : callable(values) -> CalculationResult
    base_values: current inputs dict
    base_roi   : ROI at base inputs
    sweep_keys : list of (param_key, display_label)
    """
    if not sweep_keys:
        st.info("No sweep parameters defined for this product.")
        return

    bars_low, bars_high, labels = [], [], []

    for param_key, label in sweep_keys:
        base_val = float(base_values.get(param_key, 0))
        if base_val == 0:
            continue
        _, rois, _ = _sweep_param(calc_fn, base_values, param_key, base_val)
        if not rois:
            continue
        roi_lo = min(rois) - base_roi
        roi_hi = max(rois) - base_roi
        bars_low.append(roi_lo)
        bars_high.append(roi_hi)
        labels.append(label)

    if not labels:
        st.info("Could not generate tornado data — base values may be zero.")
        return

    # Sort by total swing (largest first)
    swings = [h - l for h, l in zip(bars_high, bars_low)]
    order = sorted(range(len(labels)), key=lambda i: swings[i], reverse=True)
    labels = [labels[i] for i in order]
    bars_low = [bars_low[i] for i in order]
    bars_high = [bars_high[i] for i in order]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=labels,
            x=bars_low,
            orientation="h",
            name="Low scenario",
            marker_color=_NEGATIVE,
            hovertemplate="%{y}: %{x:+.3f}X<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            y=labels,
            x=bars_high,
            orientation="h",
            name="High scenario",
            marker_color=_POSITIVE,
            hovertemplate="%{y}: %{x:+.3f}X<extra></extra>",
        )
    )
    fig.add_vline(x=0, line_width=1.5, line_color="#475569", line_dash="dot")

    fig.update_layout(
        title=dict(
            text="ROI Sensitivity — Tornado (±30% each input)",
            font=dict(size=14, family="Inter, sans-serif"),
            x=0,
        ),
        barmode="overlay",
        template="plotly_white",
        height=max(280, 50 * len(labels) + 80),
        margin=dict(l=10, r=10, t=45, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#1E293B"),
        xaxis=dict(title="ΔROI vs Base", gridcolor="#F1F5F9", zeroline=False),
        yaxis=dict(gridcolor="#F1F5F9"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        bargap=0.3,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── 2×2 Sensitivity Grid ──────────────────────────────────────────────────────

def render_sensitivity_grid(
    calc_fn,
    base_values: Dict[str, Any],
    sweep_keys: List[Tuple[str, str]],
    max_panels: int = 4,
) -> None:
    """
    2×2 grid of line charts sweeping each input vs ROI and Net Profit.
    """
    if not sweep_keys:
        return

    active = [(k, label) for k, label in sweep_keys if float(base_values.get(k, 0)) != 0]
    active = active[:max_panels]
    if not active:
        return

    n = len(active)
    rows_n = (n + 1) // 2
    cols_n = 2 if n > 1 else 1

    subplot_titles = [f"{label}" for _, label in active]
    fig = make_subplots(
        rows=rows_n,
        cols=cols_n,
        subplot_titles=subplot_titles,
        shared_xaxes=False,
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
    )

    colours_roi = [_BRAND, _TEAL, _VIOLET, _AMBER]
    colours_net = [_POSITIVE, "#34D399", "#A78BFA", "#FCD34D"]

    for idx, (param_key, label) in enumerate(active):
        r = idx // 2 + 1
        c = idx % 2 + 1
        base_val = float(base_values.get(param_key, 0))
        xs, rois, nets = _sweep_param(calc_fn, base_values, param_key, base_val)

        # ROI trace
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=rois,
                mode="lines+markers",
                name="ROI",
                line=dict(color=colours_roi[idx % 4], width=2),
                marker=dict(size=5),
                showlegend=(idx == 0),
                hovertemplate=f"{label}: %{{x:.3f}}<br>ROI: %{{y:.2f}}X<extra></extra>",
            ),
            row=r,
            col=c,
        )
        # Base line
        fig.add_vline(x=base_val, line_width=1, line_dash="dot", line_color="#94A3B8", row=r, col=c)

    fig.update_layout(
        title=dict(
            text="Sensitivity Analysis — Key Inputs vs ROI",
            font=dict(size=14, family="Inter, sans-serif"),
            x=0,
        ),
        height=280 * rows_n,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#1E293B", size=11),
        margin=dict(l=10, r=10, t=55, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    for ax in fig.layout:
        if ax.startswith("xaxis") or ax.startswith("yaxis"):
            fig.layout[ax].update(gridcolor="#F1F5F9", showgrid=True)

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── Legacy single-metric sensitivity line ────────────────────────────────────

def render_sensitivity_chart(metric_name: str, data) -> None:
    if not data:
        return
    df = pd.DataFrame(list(data))
    fig = go.Figure(
        go.Scatter(
            x=df[metric_name],
            y=df["roi"],
            mode="lines+markers",
            line=dict(color=_BRAND, width=2),
            marker=dict(size=6, color=_BRAND),
        )
    )
    fig.update_layout(
        title=f"ROI sensitivity vs {metric_name}",
        template="plotly_white",
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif"),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
