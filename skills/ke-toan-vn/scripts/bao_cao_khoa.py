#!/usr/bin/env python3
"""Dựng báo cáo doanh thu và bảng chia tiền công của một khoa cho kỳ mới.

    # dựng tháng mới từ mẫu tháng trước
    bao_cao_khoa.py dung \\
        --mau-bcct "NT-07 MOI.xlsx" \\
        --mau-ctc  "A01-KHOA NOI TIET - T7.2026.xlsx" \\
        --nguon    "NOI TIET -08.xlsx" \\
        --thang    T8.2026 \\
        --ra       "NOI-TIET-08-MOI.xlsx"

    # kiểm chứng: dựng lại chính kỳ của mẫu rồi so từng ô với mẫu
    bao_cao_khoa.py dung --mau-bcct ... --mau-ctc ... --kiem-chung --ra /tmp/thu.xlsx
    # (chạy recalc.py của skill xlsx trên /tmp/thu.xlsx trước bước sau)
    bao_cao_khoa.py doi-chieu --mau-bcct ... --mau-ctc ... --tep /tmp/thu-da-recalc.xlsx

Đổi khoa = đổi ba file đầu vào. Bố cục sheet của các khoa trong cùng bệnh viện giống nhau,
nên các mốc dòng để mặc định; khoa nào lệch thì truyền cờ --dong-*.

Cách làm: **nhân bản nguyên sheet của kỳ trước** (giữ cả công thức lẫn định dạng) rồi đặt
DLBC kỳ mới vào cùng workbook. Không tính sẵn bằng Python rồi dán giá trị — kế toán phải bấm
được vào ô để xem nó cộng từ đâu (xem references/bao-cao.md).

Vì công thức nhân bản trỏ cột theo CHỮ CÁI ($AE, $AP, $BD...), script **chặn** nếu thứ tự cột
DLBC kỳ mới khác mẫu. Không chặn thì công thức vẫn chạy, chỉ là cộng sai cột — sai âm thầm,
kiểu sai tệ nhất.

Sheet CK-DV được sinh lại từ DLBC (các dòng công khám thuộc luồng dịch vụ). Đã đối chiếu: bản
sinh trùng khít bản kế toán tự lọc, cả số dòng lẫn từng cặp (tên dịch vụ, đơn giá).
"""

from __future__ import annotations

import argparse
import sys
from copy import copy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _chung import can_thu_vien, canh_bao, in_json  # noqa: E402

# Bố cục mặc định — theo mẫu đang dùng của bệnh viện. Khoa nào khác thì truyền cờ.
SHEET_BCCT = "BÁO CÁO CHI TIẾT"
SHEET_CTC = "Chi tiền công THEO REPORT"
SHEET_NGUON = "DLBC"
DONG_CUOI_BCCT = 24   # dòng TỔNG CỘNG; các dòng sau là đối chiếu liên kết ngoài, xem dưới
COT_CUOI_BCCT = 10
DONG_CUOI_CTC = 53
COT_CUOI_CTC = 16
O_THANG = "A1"        # ô tiêu đề tháng trên sheet Chi tiền công
O_CK_CG = "H40"       # khối "Công khám chuyên gia", lấy từ sheet CK-CG nhập tay
DONG_DVKT = (13, 16)      # nhóm 5: các TENLOAIVP của Dịch vụ kĩ thuật thông thường
DONG_XET_NGHIEM = (18, 23)  # nhóm 6: các TENCHIDINH của Xét nghiệm
DONG_GIUONG = (45, 52)    # khối giường trên sheet Chi tiền công

# MADOITUONG gộp thành luồng DỊCH VỤ. Luồng BHYT là 1, THU PHÍ là 2.
MA_DICH_VU = (8, 11, 12)

NHOM_BCCT = {
    "Công khám", "Tiền giường", "Thuốc", "Vật tư tiêu hao",
    "Dịch vụ kĩ thuật thông thường", "Xét nghiệm",
}

# Cột của sheet CK-DV <- cột tương ứng trên DLBC
CK_DV_COT = [
    ("TENKPCT", "TENKP"), ("NGAYTHU", "NGAYTHU"), ("QUYENSO", "QUYENSO"),
    ("SOBIENLAI", "SOBIENLAI"), ("TEN", "TENCHIDINH"), ("DVT", "DVT"),
    ("DONGIA", "DONGIA"), ("SOLUONG", "SOLUONG"), ("SOTIENCT", "SOTIENCT"),
    ("MABN", "MABN"), ("HOTEN", "HOTEN"), ("NAMSINH", "NAMSINH"),
]
CK_DV_RONG = (30, 17, 10, 11, 30, 8, 11, 9, 12, 11, 24, 10, 12)


def doc_dlbc(duong_dan: Path, sheet: str):
    """Đọc sheet dữ liệu thành (tiêu đề, chỉ mục cột theo tên, các dòng). Bỏ dòng rỗng."""
    import openpyxl

    wb = openpyxl.load_workbook(duong_dan, read_only=True, data_only=True)
    if sheet not in wb.sheetnames:
        raise SystemExit(f"Không có sheet {sheet!r} trong {duong_dan.name}")
    it = wb[sheet].iter_rows(values_only=True)
    tieu_de = list(next(it))
    # DLBC có ba cột cùng tên "BHYT" (công thức dò cũ). Giữ cột ĐẦU tiên cho mỗi tên.
    chi_muc: dict[str, int] = {}
    for i, h in enumerate(tieu_de):
        if h and h not in chi_muc:
            chi_muc[h] = i
    dong = [r for r in it if not all(v is None for v in r)]
    wb.close()
    return tieu_de, chi_muc, dong


def kiem_cot(tieu_de_mau: list, tieu_de_moi: list, den_cot: int) -> None:
    """Chặn nếu thứ tự cột DLBC kỳ mới khác mẫu.

    Công thức nhân bản từ mẫu trỏ cột theo chữ cái, nên lệch một cột là cộng sai cột mà
    vẫn ra số trông hợp lý. Thà dừng còn hơn giao một báo cáo sai không ai nhận ra.
    """
    a = [("" if h is None else str(h)) for h in tieu_de_mau]
    b = [("" if h is None else str(h)) for h in tieu_de_moi]
    # Chỉ soát tới cột cuối cùng mà công thức thật sự trỏ tới. Các cột sau đó là cột nháp
    # kế toán tự thêm ("dò tính thuế", "CHỐT ĐT", đôi khi chỉ là một cột tên "a") — khác
    # nhau giữa các file là chuyện bình thường, chặn ở đó chỉ tạo báo động giả.
    n = min(len(a), len(b), den_cot)
    lech = [(i, a[i], b[i]) for i in range(n) if a[i] != b[i]]
    thieu = den_cot - min(len(a), len(b))
    if lech or thieu > 0:
        from openpyxl.utils import get_column_letter

        chi_tiet = [f"cột {get_column_letter(i + 1)}: mẫu={x!r} nguồn={y!r}" for i, x, y in lech[:10]]
        if thieu > 0:
            chi_tiet.append(
                f"nguồn chỉ có {len(b)} cột, công thức cần tới cột "
                f"{get_column_letter(den_cot)}"
            )
        raise SystemExit(
            "Thứ tự cột DLBC của file nguồn KHÁC file mẫu, dừng để tránh cộng sai cột:\n  "
            + "\n  ".join(chi_tiet)
            + "\nCách xử lý: xuất lại DLBC theo đúng thứ tự cột của file mẫu."
        )


def cot_cuoi_cong_thuc(*ws_list) -> int:
    """Cột DLBC xa nhất mà công thức trong các sheet mẫu trỏ tới.

    Dùng làm biên cho kiem_cot: lệch ở cột nằm ngoài biên này thì không ảnh hưởng số liệu.
    """
    import re

    from openpyxl.utils import column_index_from_string

    xa = 0
    for ws in ws_list:
        if ws is None:
            continue
        for hang in ws.iter_rows():
            for o in hang:
                v = o.value
                if not (isinstance(v, str) and v.startswith("=")):
                    continue
                for cot in re.findall(r"\$([A-Z]{1,3})\$?\d*:\$([A-Z]{1,3})", v):
                    for c in cot:
                        xa = max(xa, column_index_from_string(c))
    return xa


def sao_chep_o(nguon, dich) -> None:
    """Chép giá trị/công thức + toàn bộ định dạng của một ô sang workbook khác.

    Chép định dạng vô điều kiện: font mặc định của hai workbook khác nhau (mẫu là Times New
    Roman 12, workbook mới là Calibri 11), nên ô không có style riêng vẫn phải gán tường minh.
    """
    dich.value = nguon.value
    dich.font = copy(nguon.font)
    dich.fill = copy(nguon.fill)
    dich.border = copy(nguon.border)
    dich.alignment = copy(nguon.alignment)
    dich.protection = copy(nguon.protection)
    dich.number_format = nguon.number_format


def nhan_ban_sheet(ws_mau, ws_moi, dong_cuoi: int, cot_cuoi: int) -> None:
    """Nhân bản nguyên vẹn một vùng sheet của file mẫu: giá trị, công thức, định dạng, khung."""
    for r in range(1, dong_cuoi + 1):
        for c in range(1, cot_cuoi + 1):
            sao_chep_o(ws_mau.cell(r, c), ws_moi.cell(r, c))
    for k, v in ws_mau.column_dimensions.items():
        d = ws_moi.column_dimensions[k]
        d.width, d.hidden, d.bestFit = v.width, v.hidden, v.bestFit
    for k, v in ws_mau.row_dimensions.items():
        if v.height and k <= dong_cuoi:
            ws_moi.row_dimensions[k].height = v.height
    for m in ws_mau.merged_cells.ranges:
        if m.max_row <= dong_cuoi and m.max_col <= cot_cuoi:
            ws_moi.merge_cells(str(m))
    ws_moi.sheet_view.showGridLines = ws_mau.sheet_view.showGridLines
    if ws_mau.sheet_format.defaultRowHeight:
        ws_moi.sheet_format.defaultRowHeight = ws_mau.sheet_format.defaultRowHeight


# Sáu nhóm của BÁO CÁO CHI TIẾT: (nhãn nhóm, giá trị TENNHOMBHYT, cột gom dòng chi tiết).
# Nhóm 1/3/4 gom theo chính TENNHOMBHYT nên chỉ có một dòng chi tiết; nhóm 2/5/6 liệt kê
# từng hạng mục nên số dòng thay đổi theo khoa — đó là lý do phải dựng lại thay vì nhân bản.
NHOM_DUNG_LAI = [
    ("Công khám", "Công khám", "TENNHOMBHYT"),
    ("Giường bệnh", "Tiền giường", "TENNHOM"),
    ("Thuốc", "Thuốc", "TENNHOMBHYT"),
    ("Vật tư tiêu hao", "Vật tư tiêu hao", "TENNHOMBHYT"),
    ("Dịch vụ kĩ thuật thông thường", "Dịch vụ kĩ thuật thông thường", "TENLOAIVP"),
    ("Xét nghiệm", "Xét nghiệm", "TENCHIDINH"),
]


def dung_lai_bcct(ws_mau, ws, chi_muc, dong, sheet_nguon: str) -> dict:
    """Dựng BÁO CÁO CHI TIẾT với danh mục lấy từ chính dữ liệu của khoa.

    Dùng khi khoa chưa có báo cáo kỳ trước của riêng mình: mượn bố cục, công thức và định
    dạng của khoa khác, nhưng các dòng liệt kê hạng mục (giường, dịch vụ kĩ thuật, xét
    nghiệm) phải sinh từ dữ liệu — khoa khác thì danh mục khác, chép nguyên sang là tiền
    của hạng mục không có dòng sẽ rơi ra ngoài TỔNG CỘNG.

    Mẫu cho mượn ba kiểu dòng: dòng 4 (tiêu đề nhóm), dòng 5 (chi tiết), dòng 24 (tổng cộng).
    """
    from openpyxl.utils import get_column_letter

    def cot(ten):
        return get_column_letter(chi_muc[ten] + 1)

    sl, tien, bnct = cot("SOLUONG"), cot("SOTIENCT"), cot("BNTRACT")
    dt = cot("MADOITUONG")
    dv = "+".join(str(m) for m in MA_DICH_VU)

    def sumifs(cot_do, cot_khoa, o_nhan, ma):
        return (f"SUMIFS('{sheet_nguon}'!${cot_do}:${cot_do},"
                f"'{sheet_nguon}'!${cot_khoa}:${cot_khoa},${o_nhan},"
                f"'{sheet_nguon}'!${dt}:${dt},{ma})")

    for r in range(1, 4):          # ba dòng tiêu đề
        for c in range(1, COT_CUOI_BCCT + 1):
            sao_chep_o(ws_mau.cell(r, c), ws.cell(r, c))

    r = 4
    moc_nhom = []
    for stt, (nhan, nhom_bhyt, khoa) in enumerate(NHOM_DUNG_LAI, 1):
        trong_nhom = [d for d in dong
                      if str(d[chi_muc["TENNHOMBHYT"]]).strip() == nhom_bhyt]
        tong_muc: dict = {}
        for d in trong_nhom:
            k = d[chi_muc[khoa]]
            tong_muc[k] = tong_muc.get(k, 0) + (d[chi_muc["SOTIENCT"]] or 0)
        muc = [k for k, v in sorted(tong_muc.items(), key=lambda x: -x[1]) if v]
        if not muc:                 # nhóm không phát sinh: vẫn giữ một dòng 0 cho đủ khuôn
            muc = [nhom_bhyt]

        r_nhom = r
        for c in range(1, COT_CUOI_BCCT + 1):
            sao_chep_o(ws_mau.cell(4, c), ws.cell(r_nhom, c))
        ws.cell(r_nhom, 1).value = stt
        ws.cell(r_nhom, 2).value = f"{nhan} ({khoa})"
        moc_nhom.append(r_nhom)

        r += 1
        dau_ct = r
        for ten_muc in muc:
            for c in range(1, COT_CUOI_BCCT + 1):
                sao_chep_o(ws_mau.cell(5, c), ws.cell(r, c))
            ws.cell(r, 1).value = None
            ws.cell(r, 2).value = ten_muc
            kc = cot(khoa)
            ws.cell(r, 3).value = f"={sumifs(sl, kc, f'B{r}', 1)}"
            ws.cell(r, 4).value = f"={sumifs(tien, kc, f'B{r}', 1)}"
            ws.cell(r, 5).value = f"={sumifs(bnct, kc, f'B{r}', 1)}"
            ws.cell(r, 6).value = f"={sumifs(sl, kc, f'B{r}', 2)}"
            ws.cell(r, 7).value = f"={sumifs(tien, kc, f'B{r}', 2)}"
            ws.cell(r, 8).value = "=" + "+".join(
                sumifs(sl, kc, f"B{r}", m) for m in MA_DICH_VU)
            ws.cell(r, 9).value = "=" + "+".join(
                sumifs(tien, kc, f"B{r}", m) for m in MA_DICH_VU)
            ws.cell(r, 10).value = None
            r += 1
        cuoi_ct = r - 1

        for c in range(3, 10):
            cl = get_column_letter(c)
            ws.cell(r_nhom, c).value = f"=SUM({cl}{dau_ct}:{cl}{cuoi_ct})"
        ws.cell(r_nhom, 10).value = f"=D{r_nhom}+G{r_nhom}+I{r_nhom}"

    r_tong = r
    for c in range(1, COT_CUOI_BCCT + 1):
        sao_chep_o(ws_mau.cell(24, c), ws.cell(r_tong, c))
    ws.cell(r_tong, 1).value = None
    ws.cell(r_tong, 2).value = "TỔNG CỘNG"
    for c in range(3, 10):
        cl = get_column_letter(c)
        ws.cell(r_tong, c).value = "=" + "+".join(f"{cl}{m}" for m in moc_nhom)
    ws.cell(r_tong, 10).value = f"=D{r_tong}+G{r_tong}+I{r_tong}"

    for k, v in ws_mau.column_dimensions.items():
        d = ws.column_dimensions[k]
        d.width, d.hidden, d.bestFit = v.width, v.hidden, v.bestFit
    for m in ws_mau.merged_cells.ranges:
        if m.max_row <= 3 and m.max_col <= COT_CUOI_BCCT:
            ws.merge_cells(str(m))
    ws.sheet_view.showGridLines = ws_mau.sheet_view.showGridLines
    return {"dong_tong": r_tong, "so_dong_chi_tiet": r_tong - 4 - len(moc_nhom)}


def nhan_o(ws, dau: int, cuoi: int, cot: int = 2) -> set:
    return {ws.cell(r, cot).value for r in range(dau, cuoi + 1)}


def soat_danh_muc(chi_muc, dong, ws_bcct, ws_ctc, moc, chi_bcct: bool = False) -> list[str]:
    """Tìm hạng mục có tiền trong kỳ mới nhưng KHÔNG có dòng tương ứng trong mẫu.

    Thiếu một dòng nghĩa là tiền của hạng mục đó rơi ra ngoài TỔNG CỘNG mà không ai thấy.
    Đây là phép kiểm bắt buộc, không phải cho vui: mẫu tháng 7/2026 của khoa Nội Tiết thiếu
    đúng một giường như vậy và nó lặng lẽ không được chia tiền công.
    """
    canh = []

    def co_tien(r):
        return r[chi_muc["SOTIENCT"]] or 0

    def nhom(r):
        return str(r[chi_muc["TENNHOMBHYT"]]).strip()

    co = {r[chi_muc["TENLOAIVP"]] for r in dong
          if nhom(r) == "Dịch vụ kĩ thuật thông thường" and co_tien(r)}
    thieu = co - nhan_o(ws_bcct, *moc["dvkt"])
    if thieu:
        canh.append(f"BÁO CÁO CHI TIẾT nhóm 5 (DVKT) thiếu dòng TENLOAIVP: {sorted(thieu)}")

    co = {r[chi_muc["TENCHIDINH"]] for r in dong
          if nhom(r) == "Xét nghiệm" and co_tien(r)}
    thieu = co - nhan_o(ws_bcct, *moc["xet_nghiem"])
    if thieu:
        canh.append(f"BÁO CÁO CHI TIẾT nhóm 6 (Xét nghiệm) thiếu dòng TENCHIDINH: {sorted(thieu)}")

    co = {nhom(r) for r in dong if co_tien(r)}
    if co - NHOM_BCCT:
        canh.append(f"TENNHOMBHYT lạ ngoài khuôn báo cáo: {sorted(co - NHOM_BCCT)}")

    if not chi_bcct:
        co = {r[chi_muc["TENCHIDINH"]] for r in dong
              if nhom(r) == "Tiền giường" and r[chi_muc["MADOITUONG"]] in MA_DICH_VU
              and co_tien(r)}
        thieu = co - nhan_o(ws_ctc, *moc["giuong"])
        if thieu:
            canh.append(f"Chi tiền công khối giường thiếu dòng: {sorted(thieu)}")
    return canh


def sinh_ck_dv(ws, chi_muc, dong) -> int:
    """Sinh sheet CK-DV: các dòng Công khám thuộc luồng DỊCH VỤ (MADOITUONG 8/11/12)."""
    ws.append([a for a, _ in CK_DV_COT] + ["GHI CHÚ"])
    n = 0
    for r in dong:
        if str(r[chi_muc["TENNHOMBHYT"]]).strip() != "Công khám":
            continue
        if r[chi_muc["MADOITUONG"]] not in MA_DICH_VU:
            continue
        ws.append([r[chi_muc[b]] for _, b in CK_DV_COT] + [None])
        n += 1
    from openpyxl.utils import get_column_letter

    for i, w in enumerate(CK_DV_RONG, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    return n


def sua_vung_ck_dv(ws_ctc, so_dong: int, dau: int, cuoi: int) -> None:
    """Chỉnh vùng SUMIF của khối công khám cho khớp số dòng CK-DV kỳ mới."""
    import re

    het = so_dong + 1
    for r in range(dau, cuoi + 1):
        for c in range(1, COT_CUOI_CTC + 1):
            v = ws_ctc.cell(r, c).value
            if isinstance(v, str) and v.startswith("=") and "CK-DV" in v:
                ws_ctc.cell(r, c).value = re.sub(
                    r"(\$[EH]\$)2:(\$[EH]\$)\d+", rf"\g<1>2:\g<2>{het}", v
                )


def dung(a) -> int:
    can_thu_vien("openpyxl")
    import openpyxl

    from openpyxl.utils import get_column_letter

    mau_bcct = Path(a.mau_bcct)
    chi_bcct = a.chi_bcct or not a.mau_ctc
    mau_ctc = None if chi_bcct else Path(a.mau_ctc)
    nguon = mau_bcct if a.kiem_chung else Path(a.nguon)
    thang = a.thang or ""

    tieu_de_mau, _, _ = doc_dlbc(mau_bcct, a.sheet_nguon)
    tieu_de, chi_muc, dong = doc_dlbc(nguon, a.sheet_nguon)
    for can in ("SOTIENCT", "SOLUONG", "BNTRACT", "TENNHOM", "TENNHOMBHYT",
                "TENCHIDINH", "MADOITUONG", "TENLOAIVP"):
        if can not in chi_muc:
            raise SystemExit(f"Sheet {a.sheet_nguon} thiếu cột bắt buộc {can!r}")

    wb_b = openpyxl.load_workbook(mau_bcct, data_only=False)
    ws_b_mau = wb_b[a.sheet_bcct]
    wb_c = None if chi_bcct else openpyxl.load_workbook(mau_ctc, data_only=False)
    ws_c_mau = None if chi_bcct else wb_c[a.sheet_ctc]

    # Chế độ dựng lại sinh công thức mới theo tên cột nên không phụ thuộc thứ tự cột;
    # chỉ chế độ nhân bản mới cần chặn.
    if nguon != mau_bcct and not a.dung_lai_danh_muc:
        kiem_cot(tieu_de_mau, tieu_de, cot_cuoi_cong_thuc(ws_b_mau, ws_c_mau))

    moc = {"dvkt": a.dong_dvkt, "xet_nghiem": a.dong_xet_nghiem, "giuong": a.dong_giuong}
    canh = [] if a.dung_lai_danh_muc else soat_danh_muc(
        chi_muc, dong, ws_b_mau, ws_c_mau, moc, chi_bcct)
    for c in canh:
        canh_bao(c)

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    ws_dl = wb.create_sheet(a.sheet_nguon)
    ws_dl.append(tieu_de)
    for r in dong:
        ws_dl.append(list(r))
    ws_dl.freeze_panes = "A2"

    n_ckdv = None if chi_bcct else sinh_ck_dv(wb.create_sheet("CK-DV"), chi_muc, dong)

    # BÁO CÁO CHI TIẾT: chỉ tới dòng TỔNG CỘNG. Các dòng sau trong mẫu là đối chiếu với
    # workbook NGOÀI (liên kết ngoài cache = 0 nên báo lệch bằng đúng cả doanh thu) và
    # GETPIVOTDATA vào một pivot không mang sang. Thay bằng đối chiếu tự thân.
    ws_b = wb.create_sheet(a.sheet_bcct)
    if a.dung_lai_danh_muc:
        kq = dung_lai_bcct(ws_b_mau, ws_b, chi_muc, dong, a.sheet_nguon)
        dong_tong = kq["dong_tong"]
    else:
        nhan_ban_sheet(ws_b_mau, ws_b, a.dong_cuoi_bcct, a.cot_cuoi_bcct)
        dong_tong = a.dong_cuoi_bcct

    ct = get_column_letter(a.cot_cuoi_bcct)
    # Cột SOTIENCT tra theo TÊN, không hardcode chữ cái: bố cục đổi thì ô đối chiếu
    # phải đi theo, nếu không nó lặng lẽ cộng nhầm cột và luôn báo "khớp".
    c_tien = get_column_letter(chi_muc["SOTIENCT"] + 1)
    r1, r2 = dong_tong + 2, dong_tong + 3
    ws_b.cell(r1, 2).value = "KIỂM TRA: tổng SOTIENCT trực tiếp trên " + a.sheet_nguon
    ws_b[f"{ct}{r1}"] = f"=SUM('{a.sheet_nguon}'!${c_tien}:${c_tien})"
    ws_b.cell(r2, 2).value = "CHÊNH LỆCH (phải bằng 0)"
    ws_b[f"{ct}{r2}"] = f"={ct}{dong_tong}-{ct}{r1}"
    for r in (r1, r2):
        ws_b.cell(r, a.cot_cuoi_bcct).number_format = "#,##0"

    if not chi_bcct:
        ws_c = wb.create_sheet(a.sheet_ctc)
        nhan_ban_sheet(ws_c_mau, ws_c, a.dong_cuoi_ctc, a.cot_cuoi_ctc)
        if thang:
            ws_c[a.o_thang] = f"BẢNG CHIA TIỀN CÔNG {thang}"
        sua_vung_ck_dv(ws_c, n_ckdv, 1, a.dong_cuoi_ctc)
        if not a.ck_cg:
            # Khối khám chuyên gia lấy từ sheet CK-CG — danh sách nhập tay, đơn giá của nó
            # không tồn tại dòng nào trong DLBC nên KHÔNG suy ra được. Để 0 kèm ghi chú
            # nhìn thấy được, không im lặng bỏ qua. Cũng tránh để lại tham chiếu treo
            # sang sheet CK-CG không mang theo (Excel sẽ hiện #REF!).
            o = ws_c[a.o_ck_cg]
            o.value = 0
            ws_c.cell(o.row, 10).value = "CHƯA CÓ DỮ LIỆU CK-CG KỲ NÀY — cần điền tay"

    wb.calculation.fullCalcOnLoad = True
    ra = Path(a.ra)
    wb.save(ra)
    in_json({
        "tep_ket_qua": str(ra),
        "nguon": str(nguon),
        "so_dong_dlbc": len(dong),
        "so_dong_ck_dv": n_ckdv,
        "dong_tong_cong": dong_tong,
        "dung_lai_danh_muc": bool(a.dung_lai_danh_muc),
        "chi_bcct": chi_bcct,
        "thang": thang or None,
        "canh_bao": canh,
        "buoc_tiep": "Chạy recalc.py của skill xlsx để Excel/LibreOffice tính công thức, "
                     "rồi bao_cao_khoa.py doi-chieu nếu đang kiểm chứng.",
    })
    return 0


def o_can_so(dong_cuoi_bcct: int, dong_cuoi_ctc: int, moc) -> tuple[list[str], list[str]]:
    """Danh sách ô số cần đối chiếu trên hai sheet."""
    o_b = [f"{c}{r}" for r in range(4, dong_cuoi_bcct + 1) for c in "CDEFGHIJ"]
    o_c = (
        [f"{c}{r}" for r in range(4, 7) for c in "CEFGHI"]
        + [f"{c}{r}" for r in range(13, 18) for c in "CEFGHIJKL"]
        + [f"{c}{r}" for r in range(26, 35) for c in "CEFGHI"]
        + [f"{c}{r}" for r in range(moc["giuong"][0], dong_cuoi_ctc + 1) for c in "CDEGHIJK"]
        + ["K1"]
    )
    return o_b, o_c


def doi_chieu(a) -> int:
    """So từng ô số của file đã recalc với hai file mẫu.

    Khối khám chuyên gia (CK-CG) không nằm trong danh sách ô: script không tái tạo được nó,
    nên so ở đó chỉ tạo báo động giả.
    """
    can_thu_vien("openpyxl")
    import openpyxl

    moc = {"giuong": a.dong_giuong}
    o_b, o_c = o_can_so(a.dong_cuoi_bcct, a.dong_cuoi_ctc, moc)

    def lay(p, sheet, o):
        wb = openpyxl.load_workbook(p, data_only=True)
        ws = wb[sheet]
        r = {k: ws[k].value for k in o}
        wb.close()
        return r

    lech = []
    for ten, goc_tep, sheet, o in (
        ("BCCT", Path(a.mau_bcct), a.sheet_bcct, o_b),
        ("CTC", Path(a.mau_ctc), a.sheet_ctc, o_c),
    ):
        goc, moi = lay(goc_tep, sheet, o), lay(Path(a.tep), sheet, o)
        for k, v in goc.items():
            x = v if isinstance(v, (int, float)) else None
            y = moi.get(k) if isinstance(moi.get(k), (int, float)) else None
            if x is None and y is None:
                continue
            if x is None or y is None or abs(x - y) > 0.5:
                lech.append({"sheet": ten, "o": k, "goc": v, "moi": moi.get(k)})

    tong = len(o_b) + len(o_c)
    in_json({"so_o_da_so": tong, "khop": tong - len(lech), "lech": lech})
    if lech:
        canh_bao(f"{len(lech)}/{tong} ô lệch — KHÔNG dùng file này cho kỳ mới")
        return 1
    return 0


def khoang(s: str) -> tuple[int, int]:
    dau, _, cuoi = s.partition(":")
    return int(dau), int(cuoi or dau)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="lenh", required=True)

    def chung(s):
        s.add_argument("--mau-bcct", required=True, help="File mẫu chứa sheet BÁO CÁO CHI TIẾT")
        s.add_argument("--mau-ctc", help="File mẫu chứa sheet Chi tiền công; bỏ qua nếu chỉ cần BCCT")
        s.add_argument("--sheet-bcct", default=SHEET_BCCT)
        s.add_argument("--sheet-ctc", default=SHEET_CTC)
        s.add_argument("--sheet-nguon", default=SHEET_NGUON)
        s.add_argument("--dong-cuoi-bcct", type=int, default=DONG_CUOI_BCCT)
        s.add_argument("--cot-cuoi-bcct", type=int, default=COT_CUOI_BCCT)
        s.add_argument("--dong-cuoi-ctc", type=int, default=DONG_CUOI_CTC)
        s.add_argument("--dong-giuong", type=khoang, default=DONG_GIUONG)

    s = sub.add_parser("dung", help="Dựng file kỳ mới từ mẫu kỳ trước")
    chung(s)
    s.add_argument("--nguon", help="File chứa sheet dữ liệu của kỳ mới")
    s.add_argument("--thang", help='Nhãn kỳ, ví dụ "T8.2026"')
    s.add_argument("--ra", required=True)
    s.add_argument("--cot-cuoi-ctc", type=int, default=COT_CUOI_CTC)
    s.add_argument("--o-thang", default=O_THANG)
    s.add_argument("--o-ck-cg", default=O_CK_CG)
    s.add_argument("--dong-dvkt", type=khoang, default=DONG_DVKT)
    s.add_argument("--dong-xet-nghiem", type=khoang, default=DONG_XET_NGHIEM)
    s.add_argument("--ck-cg", action="store_true",
                   help="Đã có dữ liệu CK-DV/CK-CG kỳ này, đừng ghi đè khối khám chuyên gia")
    s.add_argument("--chi-bcct", action="store_true",
                   help="Chỉ dựng sheet BÁO CÁO CHI TIẾT, bỏ Chi tiền công và CK-DV")
    s.add_argument("--dung-lai-danh-muc", action="store_true",
                   help="Sinh lại các dòng liệt kê hạng mục từ dữ liệu thay vì nhân bản. "
                        "Dùng khi khoa chưa có báo cáo kỳ trước của riêng mình — khoa khác "
                        "thì danh mục giường/dịch vụ kĩ thuật/xét nghiệm khác nhau.")
    s.add_argument("--kiem-chung", action="store_true",
                   help="Dựng lại chính kỳ của mẫu để đối chiếu, thay vì dựng kỳ mới")
    s.set_defaults(ham=dung)

    s = sub.add_parser("doi-chieu", help="So file đã recalc với hai file mẫu")
    chung(s)
    s.add_argument("--tep", required=True, help="File đã được recalc")
    s.set_defaults(ham=doi_chieu)

    a = p.parse_args()
    if a.lenh == "dung" and not a.kiem_chung and not a.nguon:
        p.error("cần --nguon (hoặc --kiem-chung)")
    if a.lenh == "doi-chieu" and not a.mau_ctc:
        p.error("doi-chieu cần cả --mau-ctc")
    return a.ham(a)


if __name__ == "__main__":
    sys.exit(main())
