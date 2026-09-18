from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CalculationResult:
    product_id: str
    product_name: str
    metrics: Dict[str, float] = field(default_factory=dict)
    breakdown: List[Dict[str, Any]] = field(default_factory=list)
    formulas: List[Dict[str, Any]] = field(default_factory=list)
    comparison: List[Dict[str, Any]] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def as_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "metrics": self.metrics,
            "breakdown": self.breakdown,
            "formulas": self.formulas,
            "comparison": self.comparison,
            "notes": self.notes,
        }


class BaseCalculator:
    product_id: str = "base"
    product_name: str = "Base Product"

    @staticmethod
    def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        if denominator == 0:
            return default
        return numerator / denominator

    @staticmethod
    def safe_float(value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def validate(self, values: Dict[str, Any]) -> Dict[str, float]:
        return {k: self.safe_float(v) for k, v in values.items()}

    def calculate(self, values: Dict[str, Any]) -> CalculationResult:
        raise NotImplementedError
