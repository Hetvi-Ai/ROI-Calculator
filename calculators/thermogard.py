from __future__ import annotations

from typing import Any, Dict, List

from calculators.base_calculator import BaseCalculator, CalculationResult

      
class ThermogardCalculator(BaseCalculator):
    product_id = "thermogard"
    product_name = "Thermogard"

    def calculate(self, values: Dict[str, Any]) -> CalculationResult:
        mode = values.get("mode", "prevention")
        flock_size = self.safe_float(values.get("flock_size"), 0)
        medication_start_day = self.safe_float(values.get("medication_start_day"), 0)
        medication_end_day = self.safe_float(values.get("medication_end_day"), 0)
        morning_water_l = self.safe_float(values.get("morning_water_l"), 0)
        afternoon_water_l = self.safe_float(values.get("afternoon_water_l"), 0)
        product_price_per_liter = self.safe_float(values.get("product_price_per_liter"), 0)
        preventive_dose_ml = self.safe_float(values.get("preventive_dose_ml"), 0)
        treatment_dose_ml = self.safe_float(values.get("treatment_dose_ml"), 0)
        average_mortality_pct = self.safe_float(values.get("average_mortality_pct"), 0)
        weight_gain_kg = self.safe_float(values.get("weight_gain_kg"), 0)
        mortality_saving_value = self.safe_float(values.get("mortality_saving_value"), 0)

        dose_ml = preventive_dose_ml if mode == "prevention" else treatment_dose_ml
        medication_duration = max(medication_end_day - medication_start_day + 1, 0)
        total_water_l = (morning_water_l + afternoon_water_l) * medication_duration
        total_product_dose_ml = dose_ml * medication_duration
        product_consumption_l = total_product_dose_ml / 1000
        cost_per_day = (dose_ml * product_price_per_liter) / 1000
        total_medication_cost = product_consumption_l * product_price_per_liter
        weight_gain_benefit = weight_gain_kg * 1000 * 0.0
        total_benefit = weight_gain_benefit + mortality_saving_value
        net_profit = total_benefit - total_medication_cost
        roi = self.safe_divide(total_benefit, total_medication_cost, 0.0)

        metrics = {
            "flock_size": flock_size,
            "investment_total": total_medication_cost,
            "weight_gain_benefit": weight_gain_benefit,
            "mortality_benefit": mortality_saving_value,
            "benefit_total": total_benefit,
            "net_profit_total": net_profit,
            "roi": roi,
            "cost_per_bird": total_medication_cost / flock_size if flock_size else 0,
            "benefit_per_bird": total_benefit / flock_size if flock_size else 0,
            "net_profit_per_bird": net_profit / flock_size if flock_size else 0,`   `
            "medication_duration_days": medication_duration,
            "total_water_l": total_water_l,
            "total_product_dose_ml": total_product_dose_ml,
            "product_consumption_l": product_consumption_l,
        }

        formulas: List[Dict[str, Any]] = [
            {"title": "Medication Duration", "formula": "Medication End Day - Medication Start Day + 1", "inputs": [medication_end_day, medication_start_day], "result": medication_duration, "unit": "days"},
            {"title": "Total Water", "formula": "(Morning Water + Afternoon Water) × Medication Duration", "inputs": [morning_water_l, afternoon_water_l, medication_duration], "result": total_water_l, "unit": "L"},
            {"title": "Total Product Dose", "formula": "Dose × Medication Duration", "inputs": [dose_ml, medication_duration], "result": total_product_dose_ml, "unit": "mL"},
            {"title": "Product Consumption", "formula": "Total Dose ÷ 1000", "inputs": [total_product_dose_ml], "result": product_consumption_l, "unit": "L"},
            {"title": "Cost/Day", "formula": "Dose × Product Price/L ÷ 1000", "inputs": [dose_ml, product_price_per_liter], "result": cost_per_day, "unit": "₹/day"},
            {"title": "Total Medication Cost", "formula": "Product Consumption × Product Price/L", "inputs": [product_consumption_l, product_price_per_liter], "result": total_medication_cost, "unit": "₹"},
            {"title": "Total Benefit", "formula": "Weight Gain Benefit + Mortality Saving", "inputs": [weight_gain_benefit, mortality_saving_value], "result": total_benefit, "unit": "₹"},
            {"title": "Net Profit", "formula": "Total Benefit - Investment", "inputs": [total_benefit, total_medication_cost], "result": net_profit, "unit": "₹"},
            {"title": "ROI", "formula": "Total Benefit ÷ Investment", "inputs": [total_benefit, total_medication_cost], "result": roi, "unit": "X"},
        ]

        return CalculationResult( 
            product_id=self.product_id,
            product_name=self.product_name if mode == "prevention" else "Thermogard Treatment",
            metrics=metrics,
            breakdown=[
                {"name": "Weight Gain", "amount": weight_gain_benefit},
                {"name": "Mortality", "amount": mortality_saving_value},
                {"name": "Investment", "amount": -total_medication_cost},
            ],
            formulas=formulas,
            comparison=[],
            notes=["Thermogard uses either preventive or treatment dose depending on selected mode."],
        )
