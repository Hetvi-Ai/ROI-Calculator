from __future__ import annotations

from typing import Any, Dict, List


def is_percentage(value: Any) -> bool:
    try:
        v = float(value)
        return 0 <= v <= 100
    except (TypeError, ValueError):
        return False


def validate_inputs(product_id: str, values: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if not values:
        return ["No calculation inputs were supplied."]

    for key, value in values.items():
        if key.endswith("price") and key != "egg_selling_price":
            if float(value) < 0:
                errors.append(f"{key.replace('_', ' ').title()} must be greater than or equal to zero.")
        if key in {"flock_size", "duration_days", "trial_duration_days", "treatment_days", "medication_start_day", "medication_end_day"}:
            if float(value) <= 0:
                errors.append(f"{key.replace('_', ' ').title()} must be greater than zero.")
        if key in {"mortality_reduction_pct", "mortality_saved_pct", "control_mortality_pct", "treatment_mortality_pct", "average_mortality_pct",
                   "egg_production_control_pct", "egg_production_treatment_pct"} and not is_percentage(value):
            errors.append(f"{key.replace('_', ' ').title()} must be between 0 and 100.")
        if key in {"fcr", "control_fcr", "treatment_fcr", "body_weight_kg", "control_body_weight_kg", "treatment_body_weight_kg"} and float(value) <= 0:
            errors.append(f"{key.replace('_', ' ').title()} must be greater than zero.")
        if key in {"dose_g_per_ton", "dose_ml_per_1000_birds_day", "preventive_dose_ml", "treatment_dose_ml"} and float(value) < 0:
            errors.append(f"{key.replace('_', ' ').title()} must be greater than or equal to zero.")

    if values.get("control_mortality_pct", 0) < 0 or values.get("treatment_mortality_pct", 0) < 0:
        errors.append("Mortality values cannot be negative.")

    return errors


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0:
        return default
    return numerator / denominator
