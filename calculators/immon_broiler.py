from __future__ import annotations

from typing import Any, Dict, List

from calculators.base_calculator import BaseCalculator, CalculationResult


class ImmonBroilerCalculator(BaseCalculator):
    product_id = "immon_broiler"
    product_name = "Immon Powder – Broiler"

    def calculate(self, values: Dict[str, Any]) -> CalculationResult:
        flock_size = self.safe_float(values.get("flock_size"), 0)
        immon_cost_per_bird_day = self.safe_float(values.get("immon_cost_per_bird_day"), 0) / 100
        trial_duration = self.safe_float(values.get("trial_duration_days"), 0)
        control_bw_kg = self.safe_float(values.get("control_body_weight_kg"), 0)
        treatment_bw_kg = self.safe_float(values.get("treatment_body_weight_kg"), 0)
        live_bird_price = self.safe_float(values.get("live_bird_price"), 0)
        control_mortality_pct = self.safe_float(values.get("control_mortality_pct"), 0)
        treatment_mortality_pct = self.safe_float(values.get("treatment_mortality_pct"), 0)

        extra_bw_kg = treatment_bw_kg - control_bw_kg
        product_cost_per_bird = immon_cost_per_bird_day * trial_duration
        total_product_cost = product_cost_per_bird * flock_size
        additional_income = extra_bw_kg * live_bird_price
        mortality_reduction_pct = control_mortality_pct - treatment_mortality_pct
        mortality_saving = (mortality_reduction_pct / 100) * treatment_bw_kg * live_bird_price * flock_size
        total_benefit = additional_income + mortality_saving
        net_profit = total_benefit - total_product_cost
        roi = self.safe_divide(total_benefit, total_product_cost, 0.0)

        metrics = {
            "flock_size": flock_size,
            "investment_total": total_product_cost,
            "weight_gain_benefit": additional_income,
            "mortality_benefit": mortality_saving,
            "benefit_total": total_benefit,
            "net_profit_total": net_profit,
            "roi": roi,
            "cost_per_bird": total_product_cost / flock_size if flock_size else 0,
            "benefit_per_bird": total_benefit / flock_size if flock_size else 0,
            "net_profit_per_bird": net_profit / flock_size if flock_size else 0,
            "extra_bw_kg": extra_bw_kg,
            "mortality_reduction_pct": mortality_reduction_pct,
        }

        formulas: List[Dict[str, Any]] = [
            {"title": "Extra BW", "formula": "Treatment BW - Control BW", "inputs": [treatment_bw_kg, control_bw_kg], "result": extra_bw_kg, "unit": "kg/bird"},
            {"title": "Product Cost", "formula": "Cost per bird/day × Trial Duration", "inputs": [immon_cost_per_bird_day, trial_duration], "result": product_cost_per_bird, "unit": "₹/bird"},
            {"title": "Additional Income", "formula": "Extra BW × Live Bird Price", "inputs": [extra_bw_kg, live_bird_price], "result": additional_income, "unit": "₹/bird"},
            {"title": "Mortality Reduction", "formula": "Control Mortality - Treatment Mortality", "inputs": [control_mortality_pct, treatment_mortality_pct], "result": mortality_reduction_pct, "unit": "%"},
            {"title": "Mortality Saving", "formula": "Mortality Reduction % ÷ 100 × Treatment BW × Live Bird Price × Flock Size", "inputs": [mortality_reduction_pct, treatment_bw_kg, live_bird_price, flock_size], "result": mortality_saving, "unit": "₹"},
            {"title": "Total Benefit", "formula": "Additional Income + Mortality Saving", "inputs": [additional_income, mortality_saving], "result": total_benefit, "unit": "₹"},
            {"title": "Net Profit", "formula": "Total Benefit - Product Cost", "inputs": [total_benefit, total_product_cost], "result": net_profit, "unit": "₹"},
            {"title": "ROI", "formula": "Total Benefit ÷ Product Cost", "inputs": [total_benefit, total_product_cost], "result": roi, "unit": "X"},
        ]

        return CalculationResult(
            product_id=self.product_id,
            product_name=self.product_name,
            metrics=metrics,
            breakdown=[
                {"name": "Weight Gain", "amount": additional_income},
                {"name": "Mortality", "amount": mortality_saving},
                {"name": "Investment", "amount": -total_product_cost},
            ],
            formulas=formulas,
            comparison=[],
            notes=["Mortality benefit is calculated using a percentage reduction times treatment BW and flock size to avoid mixing percentage and flock-level terms."],
        )
