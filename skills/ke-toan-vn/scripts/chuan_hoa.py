#!/usr/bin/env python3
"""Chuẩn hoá dữ liệu kiểu Việt Nam: số tiền, ngày tháng, MST, Unicode.

Dùng như thư viện:
    from chuan_hoa import so_vn, ngay_vn, chuan_mst, nfc

Dùng như lệnh:
    chuan_hoa.py file.xlsx --ra sach.csv
    chuan_hoa.py file.xlsx --cot-tien "tien_hang,tien_thue" --cot-ngay ngay --cot-mst mst_ban
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _chung import can_thu_vien, in_json  # noqa: E402

# Ký tự tiền tệ và rác hay dính vào số tiền trong file kế toán
_RAC_TIEN = re.compile(r"[₫đĐ\s '\"]|VND|VNĐ", re.IGNORECASE)
_CHI_SO = re.compile(r"^-?\d+(\.\d+)?$")


def nfc(gia_tri):
    """Chuẩn hoá Unicode về NFC.

    macOS lưu 'ế' thành 'e' + dấu rời (NFD), Windows lưu thành một ký tự (NFC).
    Hai chuỗi hiện lên màn hình giống hệt nhau nhưng so sánh bằng == trả về False.
    Đây là nguyên nhân số một của 'VLOOKUP không ra mà em nhìn rõ ràng là giống nhau'.
    """
    if not isinstance(gia_tri, str):
        return gia_tri
    return unicodedata.normalize("NFC", gia_tri).strip()


def so_vn(gia_tri, mac_dinh=None):
    """Đọc số tiền kiểu Việt Nam thành Decimal.

    '1.234.567'    -> 1234567      (dấu chấm phân cách nghìn)
    '1.234.567,89' -> 1234567.89   (dấu phẩy thập phân)
    '1,234,567.89' -> 1234567.89   (kiểu Mỹ, vẫn nhận)
    '(1.234.567)'  -> -1234567     (ngoặc = số âm, quy ước kế toán)
    '1.234.567 ₫'  -> 1234567

    Trả về Decimal chứ không phải float: tiền tệ cộng bằng float sinh sai số
    (0.1 + 0.2 != 0.3), và sai số đó tích luỹ qua hàng nghìn dòng hóa đơn.

    Trường hợp mập mờ: '1.234' có thể là 1234 (VN) hay 1.234 (Mỹ). Mặc định hiểu
    theo kiểu Việt Nam là 1234, vì số tiền VND trong sổ sách gần như không bao giờ
    có phần lẻ.
    """
    if gia_tri is None or gia_tri == "":
        return mac_dinh
    if isinstance(gia_tri, (int, Decimal)):
        return Decimal(gia_tri)
    if isinstance(gia_tri, float):
        return Decimal(str(gia_tri))

    s = _RAC_TIEN.sub("", str(gia_tri)).strip()
    if not s:
        return mac_dinh

    am = False
    if s.startswith("(") and s.endswith(")"):
        am, s = True, s[1:-1].strip()
    if s.startswith("-"):
        am, s = True, s[1:].strip()
    if s.startswith("+"):
        s = s[1:].strip()

    if not re.fullmatch(r"[\d.,]+", s):
        return mac_dinh

    co_cham, co_phay = "." in s, "," in s

    if co_cham and co_phay:
        # Dấu nào xuất hiện SAU cùng là dấu thập phân
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif co_phay:
        # Nhiều dấu phẩy = phân cách nghìn kiểu Mỹ; một dấu = thập phân kiểu VN
        s = s.replace(",", "") if s.count(",") > 1 else s.replace(",", ".")
    elif co_cham:
        # Nhiều dấu chấm = phân cách nghìn. Một dấu chấm với đúng 3 chữ số phía sau
        # cũng hiểu là phân cách nghìn (quy ước VN) — xem docstring.
        if s.count(".") > 1 or re.fullmatch(r"\d{1,3}\.\d{3}", s):
            s = s.replace(".", "")

    try:
        ket_qua = Decimal(s)
    except InvalidOperation:
        return mac_dinh
    return -ket_qua if am else ket_qua


def ngay_vn(gia_tri, mac_dinh=None):
    """Đọc ngày kiểu Việt Nam (dd/mm/yyyy) thành date.

    '15/07/2026' là 15 tháng 7, không phải tháng 15. Cũng nhận dd-mm-yyyy,
    dd.mm.yyyy và dạng ISO yyyy-mm-dd (hóa đơn XML dùng ISO).
    """
    if gia_tri is None or gia_tri == "":
        return mac_dinh
    if isinstance(gia_tri, datetime):
        return gia_tri.date()
    if isinstance(gia_tri, date):
        return gia_tri

    s = str(gia_tri).strip()
    # ISO trước: XML hóa đơn dùng dạng này, và không mập mờ
    for dinh_dang in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y",
                      "%d.%m.%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(s[:10] if len(s) > 10 else s, dinh_dang).date()
        except ValueError:
            continue

    # Dạng chữ: "ngày 15 tháng 07 năm 2026"
    m = re.search(r"ngày\s*(\d{1,2}).*?tháng\s*(\d{1,2}).*?năm\s*(\d{4})", s, re.IGNORECASE)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            pass
    return mac_dinh


def chuan_mst(gia_tri, mac_dinh=None):
    """Tách MST khỏi chuỗi lẫn lộn, giữ dạng CHUỖI.

    'MST: 0100109106 '   -> '0100109106'
    '0100109106-001'     -> '0100109106-001'
    100109106 (số)       -> '0100109106'  (bù số 0 đầu Excel đã ăn mất)

    Luôn trả chuỗi. Rất nhiều MST bắt đầu bằng 0; lưu dạng số là mất số 0 đầu
    và MST thành sai.
    """
    if gia_tri is None or gia_tri == "":
        return mac_dinh

    if isinstance(gia_tri, float) and gia_tri.is_integer():
        gia_tri = int(gia_tri)
    s = str(gia_tri).strip()
    if s.endswith(".0"):
        s = s[:-2]

    m = re.search(r"(\d{9,10})\s*[-–]\s*(\d{3})", s)
    if m:
        chinh = m.group(1).zfill(10)
        return f"{chinh}-{m.group(2)}"

    m = re.search(r"\d{9,13}", s)
    if not m:
        return mac_dinh
    so = m.group(0)
    if len(so) == 9:      # Excel ăn mất số 0 đầu
        so = so.zfill(10)
    elif len(so) == 12:   # 13 số bị mất số 0 đầu
        so = so.zfill(13)
    if len(so) == 13:
        return f"{so[:10]}-{so[10:]}"
    return so


def lam_sach_text(gia_tri, mac_dinh=None):
    """Chuẩn hoá NFC, gộp khoảng trắng thừa."""
    if gia_tri is None:
        return mac_dinh
    s = nfc(str(gia_tri))
    s = re.sub(r"\s+", " ", s).strip()
    return s or mac_dinh


def tim_dong_tieu_de(khung, so_dong_thu=20):
    """Đoán dòng tiêu đề thật trong file lộn xộn.

    File kế toán thật hay có logo, tên công ty, kỳ báo cáo ở vài dòng đầu, tiêu đề
    bảng nằm mãi dòng 5-6. Đọc với header=0 là hỏng toàn bộ.

    Cách đoán: dòng tiêu đề là dòng có nhiều ô chữ không rỗng nhất trong vùng đầu file.
    """
    diem_tot, dong_tot = -1, 0
    for i in range(min(so_dong_thu, len(khung))):
        hang = khung.iloc[i]
        diem = sum(
            1 for o in hang
            if o is not None and str(o).strip() not in ("", "nan", "None")
            and not _CHI_SO.fullmatch(str(o).strip())
        )
        if diem > diem_tot:
            diem_tot, dong_tot = diem, i
    return dong_tot


def _doc_bang(duong_dan: Path, sheet=None):
    import pandas as pd

    if duong_dan.suffix.lower() in (".csv", ".tsv", ".txt"):
        sep = "\t" if duong_dan.suffix.lower() == ".tsv" else None
        return pd.read_csv(duong_dan, dtype=str, sep=sep, engine="python")
    return pd.read_excel(duong_dan, sheet_name=sheet or 0, dtype=str)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Chuẩn hoá dữ liệu kiểu Việt Nam (số tiền, ngày, MST, Unicode).",
    )
    p.add_argument("tep", help="File Excel hoặc CSV cần chuẩn hoá")
    p.add_argument("--ra", help="File kết quả (.csv hoặc .xlsx)")
    p.add_argument("--sheet", help="Tên sheet cần đọc (mặc định sheet đầu)")
    p.add_argument("--cot-tien", default="", help="Các cột tiền, cách nhau bởi dấu phẩy")
    p.add_argument("--cot-ngay", default="", help="Các cột ngày, cách nhau bởi dấu phẩy")
    p.add_argument("--cot-mst", default="", help="Các cột MST, cách nhau bởi dấu phẩy")
    p.add_argument("--bo-dong-tong", action="store_true",
                   help="Bỏ các dòng tổng cộng (ô đầu chứa Tổng/Cộng)")
    args = p.parse_args()

    can_thu_vien("pandas", "openpyxl")
    import pandas as pd

    duong_dan = Path(args.tep).expanduser()
    if not duong_dan.exists():
        print(f"Không tìm thấy file: {duong_dan}", file=sys.stderr)
        return 1

    khung = _doc_bang(duong_dan, args.sheet)
    khung.columns = [lam_sach_text(c, "") for c in khung.columns]
    ban_dau = len(khung)

    if args.bo_dong_tong and len(khung.columns):
        cot_dau = khung.columns[0]
        mau_tong = re.compile(r"^\s*(tổng|cộng|tong|cong)\b", re.IGNORECASE)
        giu = ~khung[cot_dau].astype(str).apply(lambda v: bool(mau_tong.match(nfc(v) or "")))
        khung = khung[giu]

    def tach(chuoi):
        return [c.strip() for c in chuoi.split(",") if c.strip()]

    thong_ke = {"dong_ban_dau": ban_dau, "dong_con_lai": len(khung), "cot_da_xu_ly": {}}

    for cot in khung.columns:
        if khung[cot].dtype == object:
            khung[cot] = khung[cot].map(lambda v: lam_sach_text(v))

    for cot in tach(args.cot_tien):
        if cot in khung.columns:
            khung[cot] = khung[cot].map(lambda v: so_vn(v))
            thong_ke["cot_da_xu_ly"][cot] = "tiền"
    for cot in tach(args.cot_ngay):
        if cot in khung.columns:
            khung[cot] = khung[cot].map(lambda v: ngay_vn(v))
            thong_ke["cot_da_xu_ly"][cot] = "ngày"
    for cot in tach(args.cot_mst):
        if cot in khung.columns:
            khung[cot] = khung[cot].map(lambda v: chuan_mst(v))
            thong_ke["cot_da_xu_ly"][cot] = "MST"

    if args.ra:
        ra = Path(args.ra).expanduser()
        ra.parent.mkdir(parents=True, exist_ok=True)
        if ra.suffix.lower() == ".xlsx":
            khung.to_excel(ra, index=False)
        else:
            khung.to_csv(ra, index=False)
        thong_ke["tep_ket_qua"] = str(ra)
    else:
        print(khung.head(20).to_string(), file=sys.stderr)

    in_json(thong_ke)
    return 0


if __name__ == "__main__":
    sys.exit(main())
