from __future__ import annotations

from typing import Any, Dict, List

from calculators.base_calculator import BaseCalculator, CalculationResult


class ImmonLayerCalculator(BaseCalculator):
    product_id = "immon_layer"
    product_name = "Immon Layer Powder"

    def calculate(self, values: Dict[str, Any]) -> CalculationResult:
        flock_size = self.safe_float(values.get("flock_size"), 0)
        trial_duration = self.safe_float(values.get("trial_duration_days"), 0)
        control_hdp = self.safe_float(values.get("egg_production_control_pct"), 0)
        treatment_hdp = self.safe_float(values.get("egg_production_treatment_pct"), 0)
        egg_price = self.safe_float(values.get("egg_selling_price"), 0)
        product_cost_per_day = self.safe_float(values.get("product_cost_per_bird_day"), 0)
        mortality_saved_pct = self.safe_float(values.get("mortality_saved_pct"), 0)
        value_per_layer = self.safe_float(values.get("value_per_layer"), 0)

        hdp_improvement = treatment_hdp - control_hdp
        extra_eggs_per_day = flock_size * (hdp_improvement / 100)
        extra_eggs_total = extra_eggs_per_day * trial_duration
        additional_egg_income = extra_eggs_total * egg_price
        product_cost_per_bird = product_cost_per_day * trial_duration
        total_product_cost = product_cost_per_bird * flock_size
        mortality_benefit = (mortality_saved_pct / 100) * flock_size * value_per_layer
        total_benefit = additional_egg_income + mortality_benefit
        net_profit = total_benefit - total_product_cost
        roi = self.safe_divide(total_benefit, total_product_cost, 0.0)

        metrics = {
            "flock_size": flock_size,
            "investment_total": total_product_cost,
            "egg_revenue_benefit": additional_egg_income,
            "mortality_benefit": mortality_benefit,
            "benefit_total": total_benefit,
            "net_profit_total": net_profit,
            "roi": roi,
            "cost_per_bird": total_product_cost / flock_size if flock_size else 0,
            "benefit_per_bird": total_benefit / flock_size if flock_size else 0,
            "net_profit_per_bird": net_profit / flock_size if flock_size else 0,
            "hpd_improvement_pct": hdp_improvement,
            "extra_eggs_total": extra_eggs_total,
        }

        formulas: List[Dict[str, Any]] = [
            {"title": "HDP Improvement", "formula": "Treatment HDP - Control HDP", "inputs": [treatment_hdp, control_hdp], "result": hdp_improvement, "unit": "%"},
            {"title": "Extra Eggs/Day", "formula": "Flock Size × HDP Improvement ÷ 100", "inputs": [flock_size, hdp_improvement], "result": extra_eggs_per_day, "unit": "eggs/day"},
            {"title": "Extra Eggs", "formula": "Extra Eggs/Day × Trial Duration", "inputs": [extra_eggs_per_day, trial_duration], "result": extra_eggs_total, "unit": "eggs"},
            {"title": "Additional Egg Income", "formula": "Extra Eggs × Egg Selling Price", "inputs": [extra_eggs_total, egg_price], "result": additional_egg_income, "unit": "₹"},
            {"title": "Product Cost/Bird", "formula": "Product Cost/Bird/Day × Trial Duration", "inputs": [product_cost_per_day, trial_duration], "result": product_cost_per_bird, "unit": "₹/bird"},
            {"title": "Total Product Cost", "formula": "Product Cost/Bird × Flock Size", "inputs": [product_cost_per_bird, flock_size], "result": total_product_cost, "unit": "₹"},
            {"title": "Mortality Benefit", "formula": "Mortality Saved % × Flock Size × Value per Layer", "inputs": [mortality_saved_pct, flock_size, value_per_layer], "result": mortality_benefit, "unit": "₹"},
            {"title": "Total Benefit", "formula": "Additional Egg Income + Mortality Benefit", "inputs": [additional_egg_income, mortality_benefit], "result": total_benefit, "unit": "₹"},
            {"title": "ROI", "formula": "Total Benefit ÷ Total Product Cost", "inputs": [total_benefit, total_product_cost], "result": roi, "unit": "X"},
        ]

        return CalculationResult(
            product_id=self.product_id,
            product_name=self.product_name,
            metrics=metrics,
            breakdown=[
                {"name": "Egg Revenue", "amount": additional_egg_income},
                {"name": "Mortality", "amount": mortality_benefit},
                {"name": "Investment", "amount": -total_product_cost},
            ],
            formulas=formulas,
            comparison=[],
            notes=["Uses percentage-based HDP improvement and layer value to calculate egg value and mortality benefit."],
        )
