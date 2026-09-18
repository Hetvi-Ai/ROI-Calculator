from __future__ import annotations

from typing import Any, Dict, List

from calculators.base_calculator import BaseCalculator, CalculationResult


class GutsolLiquidCalculator(BaseCalculator):
    product_id = "gutsol_liquid"
    product_name = "Gutsol Liquid"

    def calculate(self, values: Dict[str, Any]) -> CalculationResult:
        flock_size = self.safe_float(values.get("flock_size"), 0)
        cost_per_bird_day = self.safe_float(values.get("gutsol_cost_per_bird_day"), 0)
        duration_days = self.safe_float(values.get("duration_days"), 0)
        live_bird_price = self.safe_float(values.get("live_bird_price"), 0)
        extra_weight_gain_g = self.safe_float(values.get("extra_weight_gain_g"), 0)
        mortality_reduction_pct = self.safe_float(values.get("mortality_reduction_pct"), 0)
        avg_weight_kg = self.safe_float(values.get("average_bird_weight_kg"), 0)

        investment = flock_size * cost_per_bird_day * duration_days
        additional_weight_kg = flock_size * extra_weight_gain_g / 1000
        weight_gain_value = additional_weight_kg * live_bird_price
        birds_saved = flock_size * (mortality_reduction_pct / 100)
        mortality_saving = birds_saved * avg_weight_kg * live_bird_price
        total_benefit = weight_gain_value + mortality_saving
        net_profit = total_benefit - investment
        roi = self.safe_divide(total_benefit, investment, 0.0)

        metrics = {
            "flock_size": flock_size,
            "investment_total": investment,
            "weight_gain_benefit": weight_gain_value,
            "mortality_benefit": mortality_saving,
            "benefit_total": total_benefit,
            "net_profit_total": net_profit,
            "roi": roi,
            "cost_per_bird": investment / flock_size if flock_size else 0,
            "benefit_per_bird": total_benefit / flock_size if flock_size else 0,
            "net_profit_per_bird": net_profit / flock_size if flock_size else 0,
            "additional_weight_kg": additional_weight_kg,
            "birds_saved": birds_saved,
            "investment_per_bird_day": cost_per_bird_day,
        }

        formulas: List[Dict[str, Any]] = [
            {"title": "Investment", "formula": "Flock Size × Cost/Bird/Day × Duration", "inputs": [flock_size, cost_per_bird_day, duration_days], "result": investment, "unit": "₹"},
            {"title": "Additional Weight", "formula": "Flock Size × Extra Weight/Bird ÷ 1000", "inputs": [flock_size, extra_weight_gain_g], "result": additional_weight_kg, "unit": "kg"},
            {"title": "Weight Gain Value", "formula": "Additional Weight × Live Bird Price", "inputs": [additional_weight_kg, live_bird_price], "result": weight_gain_value, "unit": "₹"},
            {"title": "Birds Saved", "formula": "Flock Size × Mortality Reduction %", "inputs": [flock_size, mortality_reduction_pct], "result": birds_saved, "unit": "birds"},
            {"title": "Mortality Saving", "formula": "Birds Saved × Avg Bird Weight × Live Bird Price", "inputs": [birds_saved, avg_weight_kg, live_bird_price], "result": mortality_saving, "unit": "₹"},
            {"title": "Total Benefit", "formula": "Weight Gain Value + Mortality Saving", "inputs": [weight_gain_value, mortality_saving], "result": total_benefit, "unit": "₹"},
            {"title": "Net Profit", "formula": "Total Benefit - Investment", "inputs": [total_benefit, investment], "result": net_profit, "unit": "₹"},
            {"title": "ROI", "formula": "Total Benefit ÷ Investment", "inputs": [total_benefit, investment], "result": roi, "unit": "X"},
        ]

        return CalculationResult(
            product_id=self.product_id,
            product_name=self.product_name,
            metrics=metrics,
            breakdown=[
                {"name": "Weight Gain", "amount": weight_gain_value},
                {"name": "Mortality", "amount": mortality_saving},
                {"name": "Investment", "amount": -investment},
            ],
            formulas=formulas,
            comparison=[],
            notes=["Uses the workbook logic for gutsol liquid with per-bird economic benefit separated from flock totals."],
        )
