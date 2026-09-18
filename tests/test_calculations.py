from __future__ import annotations

from calculators.gutsol_liquid import GutsolLiquidCalculator
from calculators.gutsol_powder import GutsolPowderCalculator
from calculators.immon_layer import ImmonLayerCalculator
from calculators.immon_broiler import ImmonBroilerCalculator
from calculators.colikil_r import ColikilRCalculator
from calculators.colikil_liquid import ColikilLiquidCalculator
from calculators.crdx_ir import CRDXIRCalculator


def test_gutsol_liquid():
    result = GutsolLiquidCalculator().calculate({
        "flock_size": 10000,
        "gutsol_cost_per_bird_day": 0.03,
        "duration_days": 7,
        "live_bird_price": 100,
        "extra_weight_gain_g": 30,
        "mortality_reduction_pct": 0.25,
        "average_bird_weight_kg": 2.2,
    })
    assert result.metrics["investment_total"] > 0
    assert result.metrics["roi"] > 0


def test_gutsol_powder():
    result = GutsolPowderCalculator().calculate({
        "flock_size": 10000,
        "body_weight_kg": 2.3,
        "fcr": 1.45,
        "dose_g_per_ton": 250,
        "product_price_per_kg": 600,
        "live_bird_price": 100,
        "extra_weight_gain_g": 50,
        "mortality_reduction_pct": 0.25,
        "average_bird_weight_kg": 2.3,
    })
    assert result.metrics["investment_total"] > 0
    assert result.metrics["benefit_total"] >= result.metrics["investment_total"]


def test_immon_layer():
    result = ImmonLayerCalculator().calculate({
        "flock_size": 10000,
        "trial_duration_days": 266,
        "egg_production_control_pct": 89.19,
        "egg_production_treatment_pct": 91.66,
        "egg_selling_price": 5.6,
        "product_cost_per_bird_day": 0.0152,
        "mortality_saved_pct": 0.75,
        "value_per_layer": 350,
    })
    assert result.metrics["investment_total"] > 0
    assert "benefit_total" in result.metrics


def test_immon_broiler():
    result = ImmonBroilerCalculator().calculate({
        "flock_size": 10000,
        "immon_cost_per_bird_day": 1.52,
        "trial_duration_days": 35,
        "control_body_weight_kg": 2.05,
        "treatment_body_weight_kg": 2.15,
        "live_bird_price": 100,
        "control_mortality_pct": 5,
        "treatment_mortality_pct": 4,
    })
    assert result.metrics["roi"] >= 0


def test_colikil_r():
    result = ColikilRCalculator().calculate({
        "flock_size": 10000,
        "live_bird_price": 100,
        "feed_price_per_kg": 40,
        "product_price_per_kg": 750,
        "control_body_weight_kg": 1.911,
        "treatment_body_weight_kg": 1.975,
        "control_fcr": 1.626,
        "treatment_fcr": 1.564,
        "dose_g_per_ton": 150,
    })
    assert result.metrics["benefit_per_bird"] > 0


def test_colikil_liquid():
    result = ColikilLiquidCalculator().calculate({
        "flock_size": 10000,
        "live_bird_price": 100,
        "product_price_per_liter": 1800,
        "medication_hours_day": 12,
        "treatment_days": 20,
        "water_intake_l_per_day": 0.2,
        "dose_l_per_ml": 2,
        "control_body_weight_kg": 2.181,
        "treatment_body_weight_kg": 2.247,
    })
    assert result.metrics["roi"] > 0


def test_crdx_ir():
    result = CRDXIRCalculator().calculate({
        "flock_size": 10000,
        "live_bird_price": 100,
        "product_price_per_liter": 4400,
        "dose_ml_per_1000_birds_day": 10,
        "treatment_days": 42,
        "control_body_weight_kg": 2.738,
        "treatment_body_weight_kg": 2.806,
        "control_mortality_pct": 4,
        "treatment_mortality_pct": 1.67,
    })
    assert result.metrics["benefit_total"] > 0
