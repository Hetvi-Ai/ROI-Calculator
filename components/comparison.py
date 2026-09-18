from __future__ import annotations

from typing import Any, Dict, Iterable, List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.formatting import compact_money, money, number, roi_text

_POSITIVE = "#22C55E"
_WARNING = "#F59E0B"
_NEGATIVE = "#EF4444"
_NEUTRAL = "#94A3B8"
_BRAND = "#1A56DB"


# ── Control vs Treatment Delta Table ─────────────────────────────────────────

def render_delta_table(comparison: List[Dict[str, Any]]) -> None:
    """Styled comparison table with colour-coded delta column."""
    if not comparison:
        st.info("No comparison data available for this product.")
        return

    df = pd.DataFrame(comparison)
    if df.empty:
        st.info("No comparison data available for this product.")
        return

    # Try to produce a readable styled version
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


def render_control_treatment_cards(comparison: List[Dict[str, Any]]) -> None:
    """Render a premium 2-column control vs treatment card layout."""
    if not comparison:
        return

    df = pd.DataFrame(comparison)
    if df.empty or "metric" not in df.columns:
        render_delta_table(comparison)
        return

    # Expect columns: metric, control, treatment, delta, delta_pct
    cols_needed = {"metric", "control", "treatment"}
    if not cols_needed.issubset(set(df.columns)):
        render_delta_table(comparison)
        return

    _card = lambda title, bg, border: f"""
        <div style='background:{bg};border:1.5px solid {border};border-radius:14px;
                    padding:18px 20px;box-shadow:0 2px 8px rgba(0,0,0,0.05);'>
          <div style='font-size:12px;font-weight:700;text-transform:uppercase;
                      letter-spacing:.1em;color:{border};margin-bottom:10px;'>{title}</div>
    """

    for _, row in df.iterrows():
        metric = str(row.get("metric", ""))
        control = row.get("control", 0)
        treatment = row.get("treatment", 0)
        try:
            delta = float(treatment) - float(control)
            delta_pct = (delta / float(control) * 100) if float(control) != 0 else 0
        except (TypeError, ValueError):
            delta = 0.0
            delta_pct = 0.0

        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "—")
        delta_colour = _POSITIVE if delta > 0 else (_NEGATIVE if delta < 0 else _NEUTRAL)

        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            st.markdown(
                f"<div style='padding:10px 0;border-bottom:1px solid #F1F5F9;'>"
                f"<div style='font-size:11px;color:#94A3B8;font-weight:600;"
                f"text-transform:uppercase;letter-spacing:.06em;'>Control</div>"
                f"<div style='font-size:1.1rem;font-weight:700;color:#1E293B;margin-top:2px;'>"
                f"{_fmt(control)}</div>"
                f"<div style='font-size:10px;color:#94A3B8;margin-top:1px;'>{metric}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"<div style='padding:10px 0;border-bottom:1px solid #F1F5F9;'>"
                f"<div style='font-size:11px;color:{_BRAND};font-weight:600;"
                f"text-transform:uppercase;letter-spacing:.06em;'>Treatment</div>"
                f"<div style='font-size:1.1rem;font-weight:700;color:#1E293B;margin-top:2px;'>"
                f"{_fmt(treatment)}</div>"
                f"<div style='font-size:10px;color:#94A3B8;margin-top:1px;'>{metric}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f"<div style='padding:10px 0;border-bottom:1px solid #F1F5F9;text-align:center;'>"
                f"<div style='font-size:11px;color:#94A3B8;font-weight:600;"
                f"text-transform:uppercase;letter-spacing:.06em;'>Delta</div>"
                f"<div style='font-size:1rem;font-weight:800;color:{delta_colour};margin-top:2px;'>"
                f"{arrow} {abs(delta_pct):.1f}%</div>"
                f"<div style='font-size:10px;color:#94A3B8;margin-top:1px;'>"
                f"{compact_money(delta) if abs(delta) >= 1 else number(abs(delta))}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )


def _fmt(val: Any) -> str:
    try:
        v = float(val)
        if abs(v) >= 1000:
            return compact_money(v)
        return number(v, 3)
    except (TypeError, ValueError):
        return str(val)


# ── Radar / Spider Chart ──────────────────────────────────────────────────────

def render_radar_chart(metrics: Dict[str, Any]) -> None:
    """Radar chart of normalised benefit components."""
    keys = [
        ("Weight Gain", "weight_gain_benefit"),
        ("Mortality", "mortality_benefit"),
        ("Net Profit", "net_profit_total"),
        ("ROI (×10)", "roi"),
        ("Benefit/Bird", "benefit_per_bird"),
    ]

    available = [(label, k) for label, k in keys if k in metrics and float(metrics.get(k, 0)) != 0]
    if len(available) < 3:
        st.info("Not enough benefit components for a radar chart on this product.")
        return

    labels = [label for label, _ in available]
    raw = [float(metrics.get(k, 0)) * (10 if k == "roi" else 1) for _, k in available]
    max_val = max(abs(v) for v in raw) or 1
    normalised = [v / max_val for v in raw]
    normalised.append(normalised[0])
    labels.append(labels[0])

    fig = go.Figure(
        go.Scatterpolar(
            r=normalised,
            theta=labels,
            fill="toself",
            fillcolor=f"rgba(26,86,219,0.15)",
            line=dict(color=_BRAND, width=2),
            name="Current scenario",
            hovertemplate="%{theta}: %{r:.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1.1], showticklabels=False, gridcolor="#E2E8F0"),
            angularaxis=dict(gridcolor="#E2E8F0"),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#1E293B"),
        height=320,
        margin=dict(l=40, r=40, t=30, b=30),
        title=dict(text="Benefit Component Radar", font=dict(size=14, family="Inter, sans-serif"), x=0.5),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── Product Comparison Table (legacy) ────────────────────────────────────────

def render_product_comparison(rows: Iterable[Any]) -> None:
    df = pd.DataFrame(list(rows))
    if df.empty:
        st.info("No comparable products available for this selection.")
        return
    st.dataframe(df, use_container_width=True, hide_index=True)
