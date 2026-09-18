from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.formatting import compact_money, delta_badge, money, number, roi_text


# ── Colour palette ────────────────────────────────────────────────────────────
_BRAND_BLUE = "#1A56DB"
_BRAND_TEAL = "#0EA5E9"
_POSITIVE = "#22C55E"
_WARNING = "#F59E0B"
_NEGATIVE = "#EF4444"
_CARD_BG = "rgba(255,255,255,0.55)"
_CARD_BORDER = "rgba(99,120,160,0.15)"
_NAVY = "#0A1628"


# ── KPI Cards ─────────────────────────────────────────────────────────────────

_KPI_CARD_STYLE = """
    background: {bg};
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid {border};
    border-radius: 16px;
    padding: 20px 18px 16px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(10,22,40,0.06);
    transition: box-shadow 0.2s;
"""

_ICON_MAP = {
    "Investment": "💸",
    "Total Benefit": "📈",
    "Net Profit": "💰",
    "ROI": "🎯",
    "Benefit / Bird": "🐔",
    "Cost / Bird": "🏷️",
}

_ACCENT_MAP = {
    "Investment": "#6366F1",
    "Total Benefit": "#0EA5E9",
    "Net Profit": "#22C55E",
    "ROI": "#F59E0B",
    "Benefit / Bird": "#14B8A6",
    "Cost / Bird": "#8B5CF6",
}


def render_kpis(metrics: Dict[str, Any], previous_metrics: Optional[Dict[str, Any]] = None):
    cards = [
        ("Investment", metrics.get("investment_total", 0), "₹"),
        ("Total Benefit", metrics.get("benefit_total", 0), "₹"),
        ("Net Profit", metrics.get("net_profit_total", 0), "₹"),
        ("ROI", metrics.get("roi", 0), "X"),
        ("Benefit / Bird", metrics.get("benefit_per_bird", 0), "₹"),
        ("Cost / Bird", metrics.get("cost_per_bird", 0), "₹"),
    ]
    cols = st.columns(6, gap="small")
    for idx, (label, value, unit) in enumerate(cards):
        with cols[idx]:
            if unit == "₹":
                display = compact_money(value)
                sub = money(value)
            elif unit == "X":
                display = roi_text(value)
                sub = ""
            else:
                display = number(value)
                sub = ""

            prev_val = None
            if previous_metrics:
                key_map = {
                    "Investment": "investment_total",
                    "Total Benefit": "benefit_total",
                    "Net Profit": "net_profit_total",
                    "ROI": "roi",
                    "Benefit / Bird": "benefit_per_bird",
                    "Cost / Bird": "cost_per_bird",
                }
                prev_val = previous_metrics.get(key_map[label])

            badge = delta_badge(value, prev_val)
            icon = _ICON_MAP.get(label, "")
            accent = _ACCENT_MAP.get(label, _BRAND_BLUE)

            # For net profit: colour the value
            value_colour = "#071B3B"
            if label == "Net Profit":
                value_colour = _POSITIVE if float(value) >= 0 else _NEGATIVE
            elif label == "ROI":
                value_colour = _POSITIVE if float(value) >= 1.5 else (_WARNING if float(value) >= 1 else _NEGATIVE)

            st.markdown(
                f"""
                <div style='{_KPI_CARD_STYLE.format(bg=_CARD_BG, border=_CARD_BORDER)}'>
                  <div style='position:absolute;top:0;left:0;width:4px;height:100%;
                              background:{accent};border-radius:16px 0 0 16px;'></div>
                  <div style='font-size:11px;font-weight:600;color:#6B7A99;
                              text-transform:uppercase;letter-spacing:.08em;
                              display:flex;align-items:center;gap:5px;'>
                    <span>{icon}</span>{label}
                  </div>
                  <div style='font-size:1.65rem;font-weight:800;color:{value_colour};
                              margin-top:8px;line-height:1.1;letter-spacing:-0.01em;'>
                    {display}
                  </div>
                  <div style='display:flex;align-items:center;margin-top:4px;'>
                    <span style='font-size:11px;color:#9BA8C0;'>{sub}</span>
                    {badge}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    # Breathing room after cards
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)


# ── Summary Banner ────────────────────────────────────────────────────────────

def render_summary_banner(metrics: Dict[str, Any]):
    roi = float(metrics.get("roi", 0))
    net = float(metrics.get("net_profit_total", 0))

    if roi >= 2:
        bg, icon, msg, text = "#DCFCE7", "✅", "Strong positive ROI", f"Every ₹1 invested returns {roi:.2f}X"
        border = _POSITIVE
    elif roi >= 1:
        bg, icon, msg, text = "#FEF9C3", "⚠️", "Investment recovered — moderate ROI", f"Net profit of {compact_money(net)}"
        border = _WARNING
    else:
        bg, icon, msg, text = "#FEE2E2", "❌", "Investment not recovered", f"Net loss of {compact_money(abs(net))}"
        border = _NEGATIVE

    st.markdown(
        f"""
        <div style='background:{bg};border-left:4px solid {border};
                    border-radius:0 10px 10px 0;padding:14px 20px;
                    display:flex;align-items:center;gap:12px;margin:4px 0 18px;'>
          <span style='font-size:1.4rem'>{icon}</span>
          <div>
            <div style='font-weight:700;color:#1E293B;font-size:14px;'>{msg}</div>
            <div style='color:#475569;font-size:12px;margin-top:2px;'>{text}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Waterfall / Bar Breakdown ─────────────────────────────────────────────────

def render_breakdown(result) -> None:
    if not result.breakdown:
        return

    df = pd.DataFrame(result.breakdown)
    colours = []
    for row in result.breakdown:
        amt = row.get("amount", 0)
        if row.get("name", "").lower().startswith("invest"):
            colours.append(_NEGATIVE)
        elif amt >= 0:
            colours.append(_POSITIVE)
        else:
            colours.append(_WARNING)

    fig = go.Figure(
        go.Bar(
            x=df["name"],
            y=df["amount"],
            marker_color=colours,
            text=[compact_money(v) for v in df["amount"]],
            textposition="outside",
            textfont=dict(size=12, family="Inter, sans-serif"),
            hovertemplate="%{x}: %{y:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text="Economic Benefit Breakdown", font=dict(size=15, family="Inter, sans-serif"), x=0),
        template="plotly_white",
        height=320,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#1E293B"),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=True,
                   zerolinecolor="#CBD5E1", tickformat="₹,.0f"),
        xaxis=dict(showgrid=False),
        showlegend=False,
        bargap=0.35,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── Formulas Expander ─────────────────────────────────────────────────────────

def render_formulas(result) -> None:
    for formula in result.formulas:
        with st.expander(f"🔢 {formula['title']}", expanded=False):
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.markdown(
                    f"<span style='font-family:monospace;font-size:13px;"
                    f"background:#F8FAFC;padding:4px 8px;border-radius:6px;"
                    f"border:1px solid #E2E8F0;display:inline-block;'>"
                    f"{formula['formula']}</span>",
                    unsafe_allow_html=True,
                )
                st.caption(f"Inputs: {formula['inputs']}")
            with col_b:
                st.metric("Result", f"{formula['result']:.4f} {formula['unit']}")


# ── Metrics Detail Table ──────────────────────────────────────────────────────

def render_metrics_table(metrics: Dict[str, Any]) -> None:
    rows = []
    friendly = {
        "investment_total": ("Total Investment", "₹"),
        "benefit_total": ("Total Benefit", "₹"),
        "net_profit_total": ("Net Profit", "₹"),
        "roi": ("ROI", "X"),
        "cost_per_bird": ("Cost / Bird", "₹"),
        "benefit_per_bird": ("Benefit / Bird", "₹"),
        "net_profit_per_bird": ("Net Profit / Bird", "₹"),
        "birds_saved": ("Birds Saved", ""),
        "weight_gain_benefit": ("Weight Gain Benefit", "₹"),
        "mortality_benefit": ("Mortality Benefit", "₹"),
        "additional_weight_kg": ("Additional Weight", "kg"),
    }
    for k, v in metrics.items():
        fname, unit = friendly.get(k, (k.replace("_", " ").title(), ""))
        try:
            fv = float(v)
            if unit == "₹":
                display = money(fv)
            elif unit == "X":
                display = roi_text(fv)
            elif unit == "kg":
                display = f"{fv:,.2f} kg"
            elif unit == "%":
                display = f"{fv:.2f} %"
            else:
                display = number(fv)
        except (TypeError, ValueError):
            display = str(v)
        rows.append({"Metric": fname, "Value": display})

    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Metric": st.column_config.TextColumn("Metric", width="medium"),
            "Value": st.column_config.TextColumn("Value", width="medium"),
        },
    )
