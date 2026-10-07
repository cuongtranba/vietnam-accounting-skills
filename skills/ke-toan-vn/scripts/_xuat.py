"""Ghi workbook kết quả theo một khuôn chung: tiêu đề đậm, cố định dòng đầu, có bộ lọc."""

from __future__ import annotations

from pathlib import Path


def sheet_du_lieu(wb, ten: str, tieu_de: list, dong: list):
    from openpyxl.styles import Font
    from openpyxl.utils import get_column_letter

    ws = wb.create_sheet(ten)
    ws.append(tieu_de)
    for c in ws[1]:
        c.font = Font(bold=True)
    for r in dong:
        ws.append(r)
    ws.freeze_panes = "A2"
    if tieu_de:
        ws.auto_filter.ref = f"A1:{get_column_letter(len(tieu_de))}{len(dong) + 1}"
    return ws


def dam_dong(ws, *so_dong: int) -> None:
    from openpyxl.styles import Font

    for r in so_dong:
        for c in ws[r]:
            c.font = Font(bold=True)


def luu(wb, ra: Path) -> None:
    """Đặt tính lại khi mở: kế toán mở bằng Excel là thấy số, không cần recalc trước."""
    wb.calculation.fullCalcOnLoad = True
    ra.parent.mkdir(parents=True, exist_ok=True)
    wb.save(ra)
