from __future__ import annotations

from typing import Any, Dict, List

from calculators.base_calculator import BaseCalculator, CalculationResult


class GutsolPowderCalculator(BaseCalculator):
    product_id = "gutsol_powder"
    product_name = "Gutsol Powder"

    def calculate(self, values: Dict[str, Any]) -> CalculationResult:
        flock_size = self.safe_float(values.get("flock_size"), 10000)
        live_bird_price = self.safe_float(values.get("live_bird_price"), 100)
        product_price = self.safe_float(values.get("product_price_per_kg"), 600)
        dose_g_per_ton = self.safe_float(values.get("dose_g_per_ton"), 250)

        bw = self.safe_float(values.get("body_weight_kg"), 2.3)
        fcr = self.safe_float(values.get("fcr"), 1.45)
        extra_weight_gain_g = self.safe_float(values.get("extra_weight_gain_g"), 50)
        mortality_reduction_pct = self.safe_float(values.get("mortality_reduction_pct"), 0.25)
        average_bird_weight_kg = self.safe_float(values.get("average_bird_weight_kg"), 2.3)

        # Excel formulas:
        # Total Feed Consumption (kg) = Body Weight * FCR * Birds
        total_feed_consumption = bw * fcr * flock_size
        # Gutsol Required (kg) = Total Feed Consumption * Dose / 1,000,000
        gutsol_required_kg = total_feed_consumption * dose_g_per_ton / 1_000_000
        # Investment = Gutsol Required * Product Price
        investment = gutsol_required_kg * product_price

        # Additional Weight (kg) = Birds * Extra Weight / 1000
        additional_weight_kg = flock_size * extra_weight_gain_g / 1000
        # Weight Gain Value = Additional Weight * Live Bird Price
        weight_gain_value = additional_weight_kg * live_bird_price

        # Birds Saved = Birds * (Mortality Reduction % / 100)
        birds_saved = flock_size * (mortality_reduction_pct / 100)
        # Mortality Saving Value = Birds Saved * Avg Bird Weight Saved * Live Bird Price
        mortality_saving = birds_saved * average_bird_weight_kg * live_bird_price

        # Total Value Generation = Weight Gain Value + Mortality Saving Value
        total_benefit = weight_gain_value + mortality_saving
        # Net Gain = Total Value - Investment
        net_profit = total_benefit - investment
        # ROI = Total Value / Investment
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
            "extra_bw_kg": extra_weight_gain_g / 1000,
            "mortality_reduction_pct": mortality_reduction_pct,
        }

        formulas: List[Dict[str, Any]] = [
            {"title": "Total Feed Consumption", "formula": "Body Weight × FCR × Birds", "inputs": [bw, fcr, flock_size], "result": total_feed_consumption, "unit": "kg"},
            {"title": "Gutsol Required", "formula": "Total Feed Consumption × Dose ÷ 1,000,000", "inputs": [total_feed_consumption, dose_g_per_ton], "result": gutsol_required_kg, "unit": "kg"},
            {"title": "Investment", "formula": "Gutsol Required × Product Price/kg", "inputs": [gutsol_required_kg, product_price], "result": investment, "unit": "₹"},
            {"title": "Additional Weight", "formula": "Flock Size × Extra Weight Gain/Bird ÷ 1000", "inputs": [flock_size, extra_weight_gain_g], "result": additional_weight_kg, "unit": "kg"},
            {"title": "Weight Gain Value", "formula": "Additional Weight × Live Bird Price", "inputs": [additional_weight_kg, live_bird_price], "result": weight_gain_value, "unit": "₹"},
            {"title": "Birds Saved", "formula": "Flock Size × (Mortality Reduction % ÷ 100)", "inputs": [flock_size, mortality_reduction_pct], "result": birds_saved, "unit": "birds"},
            {"title": "Mortality Saving", "formula": "Birds Saved × Avg Bird Weight Saved × Live Bird Price", "inputs": [birds_saved, average_bird_weight_kg, live_bird_price], "result": mortality_saving, "unit": "₹"},
            {"title": "Total Benefit", "formula": "Weight Gain Value + Mortality Saving Value", "inputs": [weight_gain_value, mortality_saving], "result": total_benefit, "unit": "₹"},
            {"title": "Net Gain", "formula": "Total Value - Investment", "inputs": [total_benefit, investment], "result": net_profit, "unit": "₹"},
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
            comparison=[
                {
                    "metric": "Extra Weight Gain / Bird",
                    "control": "Baseline",
                    "treatment": f"+{extra_weight_gain_g} g",
                },
                {
                    "metric": "Mortality Reduction",
                    "control": "Standard",
                    "treatment": f"-{mortality_reduction_pct}%",
                },
            ],
            notes=["Mathematical model directly calibrated from ROI_Liquid & Powder.xlsx (Gutsol Powder ROI sheet)."],
        )