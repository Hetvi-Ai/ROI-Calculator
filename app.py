from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
import streamlit as st

from config.products import PRODUCT_DEFINITIONS, PRODUCT_ORDER
from calculators.gutsol_liquid import GutsolLiquidCalculator
from calculators.gutsol_powder import GutsolPowderCalculator
from calculators.immon_layer import ImmonLayerCalculator
from calculators.immon_broiler import ImmonBroilerCalculator
from calculators.colikil_r import ColikilRCalculator
from calculators.colikil_liquid import ColikilLiquidCalculator
from calculators.crdx_ir import CRDXIRCalculator
from calculators.thermogard import ThermogardCalculator
from utils.excel_loader import load_excel_model
from utils.formatting import compact_money, money, number, roi_text
from utils.validation import validate_inputs
from components.results import (
    render_kpis,
    render_summary_banner,
    render_breakdown,
    render_formulas,
    render_metrics_table,
)
from components.comparison import (
    render_control_treatment_cards,
    render_delta_table,
)


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Poultry ROI Dashboard",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Global CSS theme ──────────────────────────────────────────────────────────
THEME_CSS = """
<style>
/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ── App background ── */
.stApp {
    background: linear-gradient(135deg, #F0F4FF 0%, #F8FAFF 60%, #EEF6FF 100%);
    min-height: 100vh;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A1628 0%, #0D1F3C 100%) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * {
    color: #CBD5E1 !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #F1F5F9 !important;
    font-weight: 700;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #94A3B8 !important;
    font-size: 12px;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 8px !important;
    color: #F1F5F9 !important;
}
[data-testid="stSidebar"] .stSelectbox svg { color: #94A3B8 !important; }

/* ── Main headings ── */
h1 { font-size: 1.6rem !important; font-weight: 800 !important; color: #0A1628 !important; letter-spacing: -0.02em; }
h2 { font-size: 1.1rem !important; font-weight: 700 !important; color: #1E293B !important; }
h3 { font-size: 0.9rem !important; font-weight: 600 !important; color: #334155 !important; }

/* ── Block container ── */
.block-container { padding-top: 2rem !important; padding-bottom: 3rem !important; max-width: 1280px; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(255,255,255,0.6);
    backdrop-filter: blur(8px);
    border-radius: 12px;
    padding: 4px;
    border: 1px solid rgba(99,120,160,0.12);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 8px 18px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    color: #475569 !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.15s ease;
}
.stTabs [aria-selected="true"] {
    background: #1A56DB !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(26,86,219,0.35) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #1A56DB, #0EA5E9) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 24px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: 0.01em;
    box-shadow: 0 4px 14px rgba(26,86,219,0.3) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(26,86,219,0.4) !important;
}

/* ── Form submit button ── */
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #1A56DB, #0EA5E9) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 32px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    width: 100%;
    box-shadow: 0 4px 14px rgba(26,86,219,0.3) !important;
    margin-top: 8px;
}

/* ── Inputs ── */
.stNumberInput > div > div > input,
.stTextInput > div > div > input {
    border-radius: 8px !important;
    border: 1px solid #E2E8F0 !important;
    background: white !important;
    font-size: 14px !important;
    padding: 8px 12px !important;
    transition: border-color 0.15s;
}
.stNumberInput > div > div > input:focus,
.stTextInput > div > div > input:focus {
    border-color: #1A56DB !important;
    box-shadow: 0 0 0 3px rgba(26,86,219,0.12) !important;
}
.stNumberInput label, .stTextInput label {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #475569 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden;
    border: 1px solid #E2E8F0 !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.5) !important;
    border-radius: 10px !important;
    padding: 12px !important;
    border: 1px solid rgba(99,120,160,0.12) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.5) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border: 1px solid #E2E8F0 !important;
}

/* ── Download buttons ── */
.stDownloadButton > button {
    background: rgba(255,255,255,0.8) !important;
    color: #1A56DB !important;
    border: 1.5px solid #1A56DB !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    backdrop-filter: blur(8px);
}
.stDownloadButton > button:hover {
    background: #1A56DB !important;
    color: white !important;
}

/* ── Alerts / info ── */
.stAlert { border-radius: 10px !important; }

/* ── Dividers ── */
hr { border-color: rgba(99,120,160,0.15) !important; margin: 1.5rem 0 !important; }

/* ── Section heading pill ── */
.section-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: linear-gradient(135deg, rgba(26,86,219,0.08), rgba(14,165,233,0.08));
    border: 1px solid rgba(26,86,219,0.2);
    border-radius: 20px; padding: 4px 14px;
    font-size: 11px; font-weight: 700; color: #1A56DB;
    text-transform: uppercase; letter-spacing: 0.08em;
    margin-bottom: 12px; margin-top: 4px;
}

/* ── Field group card ── */
.field-group {
    background: rgba(255,255,255,0.65);
    border: 1px solid rgba(99,120,160,0.12);
    border-radius: 14px;
    padding: 18px 18px 10px;
    margin-bottom: 14px;
    backdrop-filter: blur(6px);
}
</style>
"""


# ── Calculator map ─────────────────────────────────────────────────────────────
CALCULATOR_MAP = {
    "gutsol_liquid": GutsolLiquidCalculator,
    "gutsol_powder": GutsolPowderCalculator,
    "immon_layer": ImmonLayerCalculator,
    "immon_broiler": ImmonBroilerCalculator,
    "colikil_r": ColikilRCalculator,
    "colikil_liquid": ColikilLiquidCalculator,
    "crdx_ir": CRDXIRCalculator,
    "thermogard_prevention": ThermogardCalculator,
    "thermogard_treatment": ThermogardCalculator,
}

# Sensitivity sweep params per product
SWEEP_PARAMS: Dict[str, List[Tuple[str, str]]] = {
    "gutsol_liquid": [
        ("flock_size", "Flock Size"),
        ("live_bird_price", "Live Bird Price"),
        ("mortality_reduction_pct", "Mortality Reduction %"),
        ("extra_weight_gain_g", "Extra Weight/Bird (g)"),
    ],
    "gutsol_powder": [
        ("flock_size", "Flock Size"),
        ("live_bird_price", "Live Bird Price"),
        ("mortality_reduction_pct", "Mortality Reduction %"),
        ("extra_weight_gain_g", "Extra Weight/Bird (g)"),
    ],
    "immon_layer": [
        ("flock_size", "Flock Size"),
        ("egg_selling_price", "Egg Selling Price"),
        ("egg_production_treatment_pct", "Treatment HDP %"),
        ("mortality_saved_pct", "Mortality Saved %"),
    ],
    "immon_broiler": [
        ("flock_size", "Flock Size"),
        ("live_bird_price", "Live Bird Price"),
        ("treatment_mortality_pct", "Treatment Mortality %"),
        ("treatment_body_weight_kg", "Treatment BW"),
    ],
    "colikil_r": [
        ("flock_size", "Flock Size"),
        ("live_bird_price", "Live Bird Price"),
        ("treatment_fcr", "Treatment FCR"),
        ("treatment_body_weight_kg", "Treatment BW"),
    ],
    "colikil_liquid": [
        ("flock_size", "Flock Size"),
        ("live_bird_price", "Live Bird Price"),
        ("treatment_body_weight_kg", "Treatment BW"),
        ("treatment_days", "Treatment Days"),
    ],
    "crdx_ir": [
        ("flock_size", "Flock Size"),
        ("live_bird_price", "Live Bird Price"),
        ("treatment_mortality_pct", "Treatment Mortality %"),
        ("treatment_body_weight_kg", "Treatment BW"),
    ],
    "thermogard_prevention": [
        ("flock_size", "Flock Size"),
        ("average_mortality_pct", "Average Mortality %"),
        ("weight_gain_kg", "Weight Gain (kg)"),
        ("product_price_per_liter", "Product Price/L"),
    ],
    "thermogard_treatment": [
        ("flock_size", "Flock Size"),
        ("average_mortality_pct", "Average Mortality %"),
        ("weight_gain_kg", "Weight Gain (kg)"),
        ("product_price_per_liter", "Product Price/L"),
    ],
}


# ── Helpers ────────────────────────────────────────────────────────────────────

@st.cache_data
def get_excel_summary():
    return load_excel_model(Path("C:/Users/admin/Downloads/ROI_Liquid & Powder.xlsx"))


def get_product_id_from_label(label: str) -> str:
    for product_id, config in PRODUCT_DEFINITIONS.items():
        if config["product_name"] == label:
            return product_id
    return "gutsol_liquid"


def section_heading(icon: str, title: str, subtitle: str = "") -> None:
    sub = f"<div style='font-size:12px;color:#64748B;margin-top:2px;'>{subtitle}</div>" if subtitle else ""
    st.markdown(
        f"""
        <div style='margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid rgba(99,120,160,0.12);'>
          <div style='display:flex;align-items:center;gap:8px;'>
            <span style='font-size:1.1rem;'>{icon}</span>
            <span style='font-size:1rem;font-weight:800;color:#0A1628;letter-spacing:-0.01em;'>{title}</span>
          </div>
          {sub}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Sidebar ────────────────────────────────────────────────────────────────────

def render_sidebar() -> Tuple[str, Dict[str, Any]]:
    with st.sidebar:
        # Brand header
        st.markdown(
            """
            <div style='padding:16px 0 24px;border-bottom:1px solid rgba(255,255,255,0.08);margin-bottom:20px;'>
              <div style='font-size:1.3rem;font-weight:800;color:#F1F5F9;letter-spacing:-0.02em;'>
                🐔 ROI Dashboard
              </div>
              <div style='font-size:11px;color:#64748B;margin-top:3px;'>
                Poultry Product Economic Impact
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='font-size:11px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;'>Product</div>", unsafe_allow_html=True)

        product_options = {cfg["product_name"]: pid for pid, cfg in PRODUCT_DEFINITIONS.items()}
        selected_label = st.selectbox("", list(product_options.keys()), label_visibility="collapsed")
        product_id = get_product_id_from_label(selected_label)

        mode_override = None
        if product_id.startswith("thermogard"):
            st.markdown("<div style='font-size:11px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:.08em;margin-top:14px;margin-bottom:8px;'>Mode</div>", unsafe_allow_html=True)
            mode_override = st.radio("", ["Prevention", "Treatment"], label_visibility="collapsed")
            if mode_override == "Treatment":
                product_id = "thermogard_treatment"
            else:
                product_id = "thermogard_prevention"

        # Product metadata chip
        cfg = PRODUCT_DEFINITIONS[product_id]
        st.markdown(
            f"""
            <div style='margin-top:16px;padding:12px 14px;background:rgba(255,255,255,0.06);
                        border:1px solid rgba(255,255,255,0.1);border-radius:10px;'>
              <div style='font-size:10px;color:#94A3B8;font-weight:600;text-transform:uppercase;
                          letter-spacing:.08em;margin-bottom:8px;'>Product Details</div>
              <div style='font-size:12px;color:#CBD5E1;'>
                <div>📦 {cfg.get('form','—')}</div>
                <div style='margin-top:4px;'>🏷️ {cfg.get('category','—')}</div>
                <div style='margin-top:4px;'>🔬 {cfg.get('application','—')}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Excel model status
        st.markdown("<div style='margin-top:24px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
        wb = get_excel_summary()
        if wb.get("available"):
            st.markdown(
                f"<div style='font-size:11px;color:#4ADE80;'>✅ Workbook loaded</div>"
                f"<div style='font-size:10px;color:#64748B;margin-top:2px;'>{Path(wb['path']).name}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div style='font-size:11px;color:#F87171;'>⚠️ Workbook not found</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    return product_id, cfg


# ── Input Form ─────────────────────────────────────────────────────────────────

def render_input_form(product_id: str, values: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
    config = PRODUCT_DEFINITIONS[product_id]
    inputs = config["inputs"]

    # Group fields: first 3 → flock params, rest → economic params
    mid = min(3, len(inputs))
    groups = [
        ("🐔 Flock Parameters", inputs[:mid]),
        ("💵 Economic Parameters", inputs[mid:]),
    ]

    with st.form("roi_form", clear_on_submit=False):
        for group_label, fields in groups:
            if not fields:
                continue
            st.markdown(f"<div class='field-group'>", unsafe_allow_html=True)
            st.markdown(
                f"<div style='font-size:11px;font-weight:700;color:#1A56DB;"
                f"text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px;'>"
                f"{group_label}</div>",
                unsafe_allow_html=True,
            )
            ncols = 2 if len(fields) > 2 else len(fields)
            cols = st.columns(ncols)
            for i, field in enumerate(fields):
                fid = field["id"]
                val = float(values.get(fid, field["default"]))
                label = field["label"]
                unit = field.get("unit", "")
                full_label = f"{label} ({unit})" if unit else label
                is_pct = any(t in fid for t in ["pct", "mortality", "fcr", "production"])
                kw = dict(value=val, min_value=0.0, step=0.01, format="%.4f", label_visibility="visible")
                if is_pct:
                    kw.update(max_value=100.0, format="%.2f")
                with cols[i % ncols]:
                    form_data_entry = st.number_input(full_label, **kw)
                    # Store inline — we rebuild form_data after loop
            st.markdown("</div>", unsafe_allow_html=True)

        submitted = st.form_submit_button("⚡ Calculate Economic Impact", use_container_width=True)

    # Re-read session values (form doesn't return per-field easily in groups)
    # Fall back to collecting from a flat pass
    form_data: Dict[str, Any] = {}
    return form_data, submitted


def render_input_form_flat(product_id: str, values: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
    """Flat form that correctly captures all values."""
    config = PRODUCT_DEFINITIONS[product_id]
    inputs = config["inputs"]

    with st.form("roi_form", clear_on_submit=False):
        section_heading("📋", "Input Parameters", f"Configure your {config['product_name']} scenario")

        # Split into two column groups
        mid = (len(inputs) + 1) // 2
        left_fields = inputs[:mid]
        right_fields = inputs[mid:]

        col_l, col_r = st.columns(2, gap="large")
        form_data: Dict[str, Any] = {}

        def add_field(col, field):
            fid = field["id"]
            val = float(values.get(fid, field["default"]))
            unit = field.get("unit", "")
            full_label = f"{field['label']} ({unit})" if unit else field["label"]
            is_pct = any(t in fid for t in ["pct", "mortality_reduction", "egg_production", "mortality_saved"])
            kw = dict(value=val, min_value=0.0, step=0.01, format="%.4f")
            if is_pct:
                kw.update(max_value=100.0, format="%.2f")
            with col:
                return st.number_input(full_label, **kw, key=f"inp_{fid}")

        for field in left_fields:
            form_data[field["id"]] = add_field(col_l, field)
        for field in right_fields:
            form_data[field["id"]] = add_field(col_r, field)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("⚡  Calculate Economic Impact", use_container_width=True)

    return form_data, submitted


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    st.markdown(THEME_CSS, unsafe_allow_html=True)

    product_id, cfg = render_sidebar()

    # Page header
    st.markdown(
        f"""
        <div style='margin-bottom:24px;'>
          <div style='font-size:0.75rem;font-weight:700;color:#1A56DB;text-transform:uppercase;
                      letter-spacing:.1em;margin-bottom:4px;'>
            Poultry Product ROI & Profit Impact
          </div>
          <h1 style='margin:0 0 4px;'>Economic Impact Dashboard</h1>
          <div style='font-size:13px;color:#64748B;'>
            Measure the economic return of <strong>{cfg['product_name']}</strong> using validated field data
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Session state init
    prev_product = st.session_state.get("current_product")
    if prev_product != product_id:
        # Product changed — reset to defaults
        defaults = {f["id"]: f["default"] for f in cfg["inputs"]}
        st.session_state.selected_values = defaults
        st.session_state.current_product = product_id
        st.session_state.pop("last_result", None)
        st.session_state.pop("prev_metrics", None)

    if "selected_values" not in st.session_state:
        st.session_state.selected_values = {f["id"]: f["default"] for f in cfg["inputs"]}

    # Two-column layout: form left, results right
    form_col, result_col = st.columns([1, 1.85], gap="large")

    with form_col:
        input_values, submitted = render_input_form_flat(product_id, st.session_state.selected_values)
        if submitted:
            st.session_state.selected_values = input_values

    # Run calculation (auto-run if not yet calculated)
    if submitted or "last_result" not in st.session_state:
        errors = validate_inputs(product_id, input_values)
        if errors:
            with result_col:
                for err in errors:
                    st.error(err)
            return

        calc_class = CALCULATOR_MAP[product_id]
        result = calc_class().calculate(input_values)
        prev_metrics = st.session_state.get("last_metrics")
        st.session_state.prev_metrics = prev_metrics
        st.session_state.last_metrics = result.metrics
        st.session_state.last_result = result
        st.session_state.last_inputs = input_values
    else:
        result = st.session_state.last_result
        input_values = st.session_state.get("last_inputs", st.session_state.selected_values)

    metrics = result.metrics
    prev_metrics = st.session_state.get("prev_metrics")

    with result_col:
        # ── KPI Cards ──────────────────────────────────────────
        render_kpis(metrics, prev_metrics)
        render_summary_banner(metrics)

        # ── Streamlined Tabs ────────────────────────────────────
        tab_roi, tab_details, tab_export = st.tabs([
            "📊 ROI Breakdown",
            "🔍 Metric Details & Formulas",
            "📥 Export Summary",
        ])

        with tab_roi:
            render_breakdown(result)

        with tab_details:
            section_heading("🔍", "Full Metrics", "Key calculated values for this scenario")
            render_metrics_table(metrics)
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            section_heading("🧮", "Formula Steps", "Underlying formula steps")
            render_formulas(result)

            if result.notes:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                with st.expander("📝 Calculation Notes"):
                    for note in result.notes:
                        st.markdown(f"• {note}")

        with tab_export:
            section_heading("📥", "Export Report", "Download results in your preferred format")
            col_a, col_b = st.columns(2, gap="medium")
            with col_a:
                st.download_button(
                    "📊 Download JSON Report",
                    data=json.dumps(result.as_dict(), indent=2),
                    file_name=f"roi_{product_id}.json",
                    mime="application/json",
                    use_container_width=True,
                )
            with col_b:
                st.download_button(
                    "📑 Download CSV Metrics",
                    data=pd.DataFrame([metrics]).to_csv(index=False),
                    file_name=f"roi_{product_id}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.markdown(
                f"<div style='background:rgba(255,255,255,0.5);border:1px solid #E2E8F0;"
                f"border-radius:12px;padding:16px;'>"
                f"<div style='font-size:11px;color:#64748B;font-weight:600;"
                f"text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px;'>Summary</div>"
                f"<div style='font-size:13px;color:#1E293B;'>Product: <b>{result.product_name}</b></div>"
                f"<div style='font-size:13px;color:#1E293B;margin-top:4px;'>ROI: <b>{roi_text(metrics.get('roi',0))}</b></div>"
                f"<div style='font-size:13px;color:#1E293B;margin-top:4px;'>Net Profit: <b>{money(metrics.get('net_profit_total',0))}</b></div>"
                f"</div>",
                unsafe_allow_html=True,
            )



if __name__ == "__main__":
    main()
