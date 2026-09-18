from __future__ import annotations

from typing import Any, Dict, List

from calculators.base_calculator import BaseCalculator, CalculationResult


class GutsolPowderCalculator(BaseCalculator):
    product_id = "gutsol_powder"
    product_name = "Gutsol Powder"

    def calculate(self, values: Dict[str, Any]) -> CalculationResult:
        flock_size = self.safe_float(values.get("flock_size"), 0)
        body_weight_kg = self.safe_float(values.get("body_weight_kg"), 0)
        fcr = self.safe_float(values.get("fcr"), 0)
        dose_g_per_ton = self.safe_float(values.get("dose_g_per_ton"), 0)
        product_price = self.safe_float(values.get("product_price_per_kg"), 0)
        live_bird_price = self.safe_float(values.get("live_bird_price"), 0)
        extra_weight_gain_g = self.safe_float(values.get("extra_weight_gain_g"), 0)
        mortality_reduction_pct = self.safe_float(values.get("mortality_reduction_pct"), 0)
        avg_weight_saved_kg = self.safe_float(values.get("average_bird_weight_kg"), 0)

        total_feed_consumption = flock_size * body_weight_kg * fcr
        gutsol_required_kg = total_feed_consumption * dose_g_per_ton / 1_000_000
        investment = gutsol_required_kg * product_price
        additional_weight_kg = flock_size * extra_weight_gain_g / 1000
        weight_gain_value = additional_weight_kg * live_bird_price
        birds_saved = flock_size * (mortality_reduction_pct / 100)
        mortality_saving = birds_saved * avg_weight_saved_kg * live_bird_price
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
            "product_required_kg": gutsol_required_kg,
            "total_feed_consumption_kg": total_feed_consumption,
        }

        formulas: List[Dict[str, Any]] = [
            {"title": "Total Feed Consumption", "formula": "Flock Size × Body Weight × FCR", "inputs": [flock_size, body_weight_kg, fcr], "result": total_feed_consumption, "unit": "kg"},
            {"title": "Gutsol Required", "formula": "Total Feed Consumption × Dose ÷ 1,000,000", "inputs": [total_feed_consumption, dose_g_per_ton], "result": gutsol_required_kg, "unit": "kg"},
            {"title": "Investment", "formula": "Gutsol Required × Product Price/kg", "inputs": [gutsol_required_kg, product_price], "result": investment, "unit": "₹"},
            {"title": "Additional Weight", "formula": "Flock Size × Extra Weight Gain ÷ 1000", "inputs": [flock_size, extra_weight_gain_g], "result": additional_weight_kg, "unit": "kg"},
            {"title": "Weight Gain Value", "formula": "Additional Weight × Live Bird Price", "inputs": [additional_weight_kg, live_bird_price], "result": weight_gain_value, "unit": "₹"},
            {"title": "Birds Saved", "formula": "Flock Size × Mortality Reduction %", "inputs": [flock_size, mortality_reduction_pct], "result": birds_saved, "unit": "birds"},
            {"title": "Mortality Saving", "formula": "Birds Saved × Avg bird weight saved × Live Bird Price", "inputs": [birds_saved, avg_weight_saved_kg, live_bird_price], "result": mortality_saving, "unit": "₹"},
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
            notes=["Follows the Excel workbook logic for powder dose, feed consumption, and mortality savings."],
        )
