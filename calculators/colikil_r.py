from __future__ import annotations

from typing import Any, Dict, List

from calculators.base_calculator import BaseCalculator, CalculationResult


class ColikilRCalculator(BaseCalculator):
    product_id = "colikil_r"
    product_name = "Colikil-R Powder"

    def calculate(self, values: Dict[str, Any]) -> CalculationResult:
        flock_size = self.safe_float(values.get("flock_size"), 0)
        live_bird_price = self.safe_float(values.get("live_bird_price"), 0)
        feed_price = self.safe_float(values.get("feed_price_per_kg"), 0)
        product_price = self.safe_float(values.get("product_price_per_kg"), 0)
        control_bw = self.safe_float(values.get("control_body_weight_kg"), 0)
        treatment_bw = self.safe_float(values.get("treatment_body_weight_kg"), 0)
        control_fcr = self.safe_float(values.get("control_fcr"), 0)
        treatment_fcr = self.safe_float(values.get("treatment_fcr"), 0)
        dose_g_per_ton = self.safe_float(values.get("dose_g_per_ton"), 0)

        extra_bw = treatment_bw - control_bw
        additional_income_per_bird = extra_bw * live_bird_price
        control_feed_per_bird = control_bw * control_fcr
        treatment_feed_per_bird = treatment_bw * treatment_fcr
        feed_saved_per_bird = control_feed_per_bird - treatment_feed_per_bird
        feed_saving_per_bird = feed_saved_per_bird * feed_price
        product_cost_per_ton = (dose_g_per_ton / 1000) * product_price
        product_cost_per_bird = (treatment_feed_per_bird / 1000) * product_cost_per_ton
        total_benefit_per_bird = additional_income_per_bird + feed_saving_per_bird
        net_profit_per_bird = total_benefit_per_bird - product_cost_per_bird
        roi = self.safe_divide(total_benefit_per_bird, product_cost_per_bird, 0.0)

        total_benefit = total_benefit_per_bird * flock_size
        total_product_cost = product_cost_per_bird * flock_size
        total_net_profit = total_benefit - total_product_cost

        metrics = {
            "flock_size": flock_size,
            "investment_total": total_product_cost,
            "benefit_total": total_benefit,
            "net_profit_total": total_net_profit,
            "roi": roi,
            "cost_per_bird": product_cost_per_bird,
            "benefit_per_bird": total_benefit_per_bird,
            "net_profit_per_bird": net_profit_per_bird,
            "extra_bw_kg": extra_bw,
            "feed_saved_kg_per_bird": feed_saved_per_bird,
        }

        formulas: List[Dict[str, Any]] = [
            {"title": "Extra BW", "formula": "Treatment BW - Control BW", "inputs": [treatment_bw, control_bw], "result": extra_bw, "unit": "kg/bird"},
            {"title": "Additional Income/Bird", "formula": "Extra BW × Live Bird Price", "inputs": [extra_bw, live_bird_price], "result": additional_income_per_bird, "unit": "₹/bird"},
            {"title": "Control Feed/Bird", "formula": "Control BW × Control FCR", "inputs": [control_bw, control_fcr], "result": control_feed_per_bird, "unit": "kg/bird"},
            {"title": "Treatment Feed/Bird", "formula": "Treatment BW × Treatment FCR", "inputs": [treatment_bw, treatment_fcr], "result": treatment_feed_per_bird, "unit": "kg/bird"},
            {"title": "Feed Saved/Bird", "formula": "Control Feed - Treatment Feed", "inputs": [control_feed_per_bird, treatment_feed_per_bird], "result": feed_saved_per_bird, "unit": "kg/bird"},
            {"title": "Feed Saving/Bird", "formula": "Feed Saved × Feed Price", "inputs": [feed_saved_per_bird, feed_price], "result": feed_saving_per_bird, "unit": "₹/bird"},
            {"title": "Product Cost/Ton", "formula": "Dose/1000 × Product Price", "inputs": [dose_g_per_ton, product_price], "result": product_cost_per_ton, "unit": "₹/ton"},
            {"title": "Product Cost/Bird", "formula": "Treatment Feed/1000 × Product Cost/Ton", "inputs": [treatment_feed_per_bird, product_cost_per_ton], "result": product_cost_per_bird, "unit": "₹/bird"},
            {"title": "Total Benefit/Bird", "formula": "Additional Income + Feed Saving", "inputs": [additional_income_per_bird, feed_saving_per_bird], "result": total_benefit_per_bird, "unit": "₹/bird"},
            {"title": "Net Profit/Bird", "formula": "Total Benefit - Product Cost", "inputs": [total_benefit_per_bird, product_cost_per_bird], "result": net_profit_per_bird, "unit": "₹/bird"},
            {"title": "ROI", "formula": "Total Benefit ÷ Product Cost", "inputs": [total_benefit_per_bird, product_cost_per_bird], "result": roi, "unit": "X"},
        ]

        return CalculationResult(
            product_id=self.product_id,
            product_name=self.product_name,
            metrics=metrics,
            breakdown=[
                {"name": "Weight Gain", "amount": additional_income_per_bird * flock_size},
                {"name": "Feed Saving", "amount": feed_saving_per_bird * flock_size},
                {"name": "Investment", "amount": -total_product_cost},
            ],
            formulas=formulas,
            comparison=[],
            notes=["ROI uses fishbone logic from the workbook: weight gain + feed saving is compared against product cost per bird."],
        )
