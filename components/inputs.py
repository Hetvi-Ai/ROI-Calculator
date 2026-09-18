from __future__ import annotations

from typing import Any, Dict

import streamlit as st


def render_input_form(product_id: str, values: Dict[str, Any], config: Dict[str, Any]):
    with st.form("roi_form"):
        st.subheader(f"{config['product_name']} inputs")
        form_data: Dict[str, Any] = {}
        for field in config["inputs"]:
            field_id = field["id"]
            value = values.get(field_id, field["default"])
            label = field["label"]
            if any(token in field_id for token in ["pct", "mortality", "fcr", "egg_production"]):
                form_data[field_id] = st.number_input(label, value=float(value), min_value=0.0, max_value=100.0, step=0.01)
            else:
                form_data[field_id] = st.number_input(label, value=float(value), min_value=0.0, step=0.01)
        submitted = st.form_submit_button("Calculate Economic Impact")
        return form_data, submitted
