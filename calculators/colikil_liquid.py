from __future__ import annotations

from typing import Any, Dict, List

from calculators.base_calculator import BaseCalculator, CalculationResult


class ColikilLiquidCalculator(BaseCalculator):
    product_id = "colikil_liquid"
    product_name = "Colikil Liquid"

    def calculate(self, values: Dict[str, Any]) -> CalculationResult:
        flock_size = self.safe_float(values.get("flock_size"), 0)
        live_bird_price = self.safe_float(values.get("live_bird_price"), 0)
        product_price_per_liter = self.safe_float(values.get("product_price_per_liter"), 0)
        medication_hours_day = self.safe_float(values.get("medication_hours_day"), 0)
        treatment_days = self.safe_float(values.get("treatment_days"), 0)
        water_intake_l_per_day = self.safe_float(values.get("water_intake_l_per_day"), 0)
        dose_l_per_ml = self.safe_float(values.get("dose_l_per_ml"), 0)
        control_bw = self.safe_float(values.get("control_body_weight_kg"), 0)
        treatment_bw = self.safe_float(values.get("treatment_body_weight_kg"), 0)

        extra_bw = treatment_bw - control_bw
        additional_income_per_bird = extra_bw * live_bird_price
        water_consumed_during_medication = water_intake_l_per_day * medication_hours_day * treatment_days / 24
        product_used_per_bird_ml = water_consumed_during_medication / dose_l_per_ml if dose_l_per_ml else 0
        product_cost_per_bird = (product_used_per_bird_ml / 1000) * product_price_per_liter
        total_product_cost = product_cost_per_bird * flock_size
        total_benefit = additional_income_per_bird * flock_size
        net_profit_per_bird = additional_income_per_bird - product_cost_per_bird
        total_net_profit = total_benefit - total_product_cost
        roi = self.safe_divide(additional_income_per_bird, product_cost_per_bird, 0.0)

        metrics = {
            "flock_size": flock_size,
            "investment_total": total_product_cost,
            "benefit_total": total_benefit,
            "net_profit_total": total_net_profit,
            "roi": roi,
            "cost_per_bird": product_cost_per_bird,
            "benefit_per_bird": additional_income_per_bird,
            "net_profit_per_bird": net_profit_per_bird,
            "water_consumed_l_per_bird": water_consumed_during_medication,
            "product_used_ml_per_bird": product_used_per_bird_ml,
            "extra_bw_kg": extra_bw,
        }

        formulas: List[Dict[str, Any]] = [
            {"title": "Extra BW", "formula": "Treatment BW - Control BW", "inputs": [treatment_bw, control_bw], "result": extra_bw, "unit": "kg/bird"},
            {"title": "Additional Income/Bird", "formula": "Extra BW × Live Bird Price", "inputs": [extra_bw, live_bird_price], "result": additional_income_per_bird, "unit": "₹/bird"},
            {"title": "Water During Medication", "formula": "Average Water Intake × Medication Hours/Day × Treatment Days ÷ 24", "inputs": [water_intake_l_per_day, medication_hours_day, treatment_days], "result": water_consumed_during_medication, "unit": "L/bird"},
            {"title": "Product Used/Bird", "formula": "Water Consumed ÷ Dose (L water per 1 mL product)", "inputs": [water_consumed_during_medication, dose_l_per_ml], "result": product_used_per_bird_ml, "unit": "mL/bird"},
            {"title": "Product Cost/Bird", "formula": "Product Used (mL) ÷ 1000 × Product Price/L", "inputs": [product_used_per_bird_ml, product_price_per_liter], "result": product_cost_per_bird, "unit": "₹/bird"},
            {"title": "Total Product Cost", "formula": "Product Cost/Bird × Flock Size", "inputs": [product_cost_per_bird, flock_size], "result": total_product_cost, "unit": "₹"},
            {"title": "Net Profit/Bird", "formula": "Additional Income/Bird - Product Cost/Bird", "inputs": [additional_income_per_bird, product_cost_per_bird], "result": net_profit_per_bird, "unit": "₹/bird"},
            {"title": "ROI", "formula": "Benefit ÷ Cost", "inputs": [additional_income_per_bird, product_cost_per_bird], "result": roi, "unit": "X"},
        ]

        return CalculationResult(
            product_id=self.product_id,
            product_name=self.product_name,
            metrics=metrics,
            breakdown=[
                {"name": "Weight Gain", "amount": total_benefit},
                {"name": "Investment", "amount": -total_product_cost},
            ],
            formulas=formulas,
            comparison=[],
            notes=["Dose is explicitly treated as water-to-product ratio. The product used in mL/bird is separated from total flock cost."],
        )
