from __future__ import annotations

from typing import Any, Optional


def money(value: Any) -> str:
    try:
        return f"₹ {float(value):,.2f}"
    except (TypeError, ValueError):
        return "₹ 0.00"


def compact_money(value: Any) -> str:
    """Short-format rupee value: ₹ 1.2 L / ₹ 45 K / ₹ 950."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "₹ 0"
    abs_v = abs(v)
    sign = "-" if v < 0 else ""
    if abs_v >= 1_00_00_000:
        return f"{sign}₹ {abs_v / 1_00_00_000:.2f} Cr"
    if abs_v >= 1_00_000:
        return f"{sign}₹ {abs_v / 1_00_000:.2f} L"
    if abs_v >= 1_000:
        return f"{sign}₹ {abs_v / 1_000:.1f} K"
    return f"{sign}₹ {abs_v:.0f}"


def number(value: Any, decimals: int = 2) -> str:
    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return "0.00"


def percent(value: Any, decimals: int = 2) -> str:
    try:
        return f"{float(value):,.{decimals}%}"
    except (TypeError, ValueError):
        return "0.00%"


def roi_text(value: Any) -> str:
    try:
        return f"{float(value):.2f}X"
    except (TypeError, ValueError):
        return "0.00X"


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def format_unit(value: Any, unit: str = "") -> str:
    if value is None:
        return "0"
    if unit:
        return f"{value} {unit}"
    return str(value)


def delta_badge(current: Any, previous: Optional[Any]) -> str:
    """Return an HTML span chip showing the delta vs previous value."""
    if previous is None:
        return ""
    try:
        cur = float(current)
        prev = float(previous)
    except (TypeError, ValueError):
        return ""
    diff = cur - prev
    if abs(diff) < 1e-9:
        return "<span style='font-size:11px;color:#6B7A99;margin-left:6px;'>—</span>"
    arrow = "▲" if diff > 0 else "▼"
    colour = "#22C55E" if diff > 0 else "#EF4444"
    display = compact_money(abs(diff)) if abs(diff) >= 10 else f"{abs(diff):.2f}"
    return (
        f"<span style='font-size:11px;font-weight:600;color:{colour};"
        f"background:{colour}18;padding:2px 6px;border-radius:20px;"
        f"margin-left:6px;'>{arrow} {display}</span>"
    )
