from __future__ import annotations

import os
from typing import Any, Dict, Iterable, List, Tuple

from openpyxl import load_workbook


def find_workbook_candidates() -> List[str]:
    search_roots = [
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/OneDrive/Documents"),
        "C:/Users/admin/Downloads",
        "C:/ROI Calculator",
    ]
    candidates: List[str] = []
    for root in search_roots:
        if not os.path.isdir(root):
            continue
        for name in os.listdir(root):
            if name.lower().endswith((".xlsx", ".xlsm")) and "roi" in name.lower():
                candidates.append(os.path.join(root, name))
    return sorted(set(candidates))


def load_excel_model(path: str | None = None) -> Dict[str, Any]:
    if path is None:
        candidates = find_workbook_candidates()
        path = candidates[0] if candidates else None
    if path is None or not os.path.exists(path):
        return {"available": False, "message": "No Excel workbook was found. Place ROI_Liquid & Powder.xlsx in Downloads or the workspace root."}

    workbook = load_workbook(path, data_only=False)
    sheets = workbook.sheetnames
    summary = {"available": True, "path": path, "sheets": sheets, "products": {}}
    for sheet in sheets:
        ws = workbook[sheet]
        values: List[Tuple[Any, ...]] = []
        for row in ws.iter_rows(values_only=True):
            values.append(row)
        summary["products"][sheet] = {
            "row_count": ws.max_row,
            "column_count": ws.max_column,
            "values": values[:25],
        }
    return summary
