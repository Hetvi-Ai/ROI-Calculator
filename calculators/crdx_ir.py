from __future__ import annotations

from typing import Any, Dict, List

from calculators.base_calculator import BaseCalculator, CalculationResult


class CRDXIRCalculator(BaseCalculator):
    product_id = "crdx_ir"
    product_name = "CRDX-IR Liquid"

    def calculate(self, values: Dict[str, Any]) -> CalculationResult:
        flock_size = self.safe_float(values.get("flock_size"), 0)
        live_bird_price = self.safe_float(values.get("live_bird_price"), 0)
        product_price_per_liter = self.safe_float(values.get("product_price_per_liter"), 0)
        dose_ml_per_1000_birds_day = self.safe_float(values.get("dose_ml_per_1000_birds_day"), 0)
        treatment_days = self.safe_float(values.get("treatment_days"), 0)
        control_bw = self.safe_float(values.get("control_body_weight_kg"), 0)
        treatment_bw = self.safe_float(values.get("treatment_body_weight_kg"), 0)
        control_mortality_pct = self.safe_float(values.get("control_mortality_pct"), 0)
        treatment_mortality_pct = self.safe_float(values.get("treatment_mortality_pct"), 0)

        extra_bw = treatment_bw - control_bw
        additional_income_per_bird = extra_bw * live_bird_price
        mortality_reduction_pct = control_mortality_pct - treatment_mortality_pct
        mortality_benefit_per_bird = (mortality_reduction_pct / 100) * treatment_bw * live_bird_price
        total_benefit_per_bird = additional_income_per_bird + mortality_benefit_per_bird
        product_used_ml_per_bird = (dose_ml_per_1000_birds_day / 1000) * treatment_days
        product_cost_per_bird = product_used_ml_per_bird * (product_price_per_liter / 1000)
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
            "mortality_reduction_pct": mortality_reduction_pct,
            "product_used_ml_per_bird": product_used_ml_per_bird,
        }

        formulas: List[Dict[str, Any]] = [
            {"title": "Extra BW", "formula": "Treatment BW - Control BW", "inputs": [treatment_bw, control_bw], "result": extra_bw, "unit": "kg/bird"},
            {"title": "Additional Income/Bird", "formula": "Extra BW × Live Bird Price", "inputs": [extra_bw, live_bird_price], "result": additional_income_per_bird, "unit": "₹/bird"},
            {"title": "Mortality Reduction", "formula": "Control Mortality - Treatment Mortality", "inputs": [control_mortality_pct, treatment_mortality_pct], "result": mortality_reduction_pct, "unit": "%"},
            {"title": "Mortality Benefit", "formula": "Mortality Reduction % ÷ 100 × Treatment BW × Live Bird Price", "inputs": [mortality_reduction_pct, treatment_bw, live_bird_price], "result": mortality_benefit_per_bird, "unit": "₹/bird"},
            {"title": "Total Benefit/Bird", "formula": "Additional Income + Mortality Benefit", "inputs": [additional_income_per_bird, mortality_benefit_per_bird], "result": total_benefit_per_bird, "unit": "₹/bird"},
            {"title": "Product Used", "formula": "Dose/1000 × Treatment Days", "inputs": [dose_ml_per_1000_birds_day, treatment_days], "result": product_used_ml_per_bird, "unit": "mL/bird"},
            {"title": "Product Cost/Bird", "formula": "Product Used × Product Price/L ÷ 1000", "inputs": [product_used_ml_per_bird, product_price_per_liter], "result": product_cost_per_bird, "unit": "₹/bird"},
            {"title": "Net Profit/Bird", "formula": "Total Benefit - Product Cost", "inputs": [total_benefit_per_bird, product_cost_per_bird], "result": net_profit_per_bird, "unit": "₹/bird"},
            {"title": "ROI", "formula": "Total Benefit ÷ Product Cost", "inputs": [total_benefit_per_bird, product_cost_per_bird], "result": roi, "unit": "X"},
        ]

        return CalculationResult(
            product_id=self.product_id,
            product_name=self.product_name,
            metrics=metrics,
            breakdown=[
                {"name": "Weight Gain", "amount": additional_income_per_bird * flock_size},
                {"name": "Mortality", "amount": mortality_benefit_per_bird * flock_size},
                {"name": "Investment", "amount": -total_product_cost},
            ],
            formulas=formulas,
            comparison=[],
            notes=["The dose is tracked in mL per 1000 birds/day and converted to per-bird cost before ROI is calculated."],
        )
