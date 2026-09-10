#!/usr/bin/env python3
"""Bóc tách hóa đơn điện tử (XML theo QĐ 1450/QĐ-TCT, và PDF) thành một bảng chuẩn hoá.

    doc_hoa_don.py <thư mục|file> --ra bang_ke.csv
    doc_hoa_don.py <thư mục> --ra bang_ke.json --dinh-dang json

XML THẮNG PDF. Theo Điều 7 NĐ 123/2020, bản XML là bản gốc có giá trị pháp lý; PDF chỉ là
'bản thể hiện'. Khi một hóa đơn có cả hai, script chỉ đọc XML và bỏ qua PDF trùng.

Cột `nguon` ghi XML hay PDF, vì độ tin cậy hai bên khác hẳn nhau: XML có nhãn rõ ràng, PDF phải
suy từ vị trí chữ. Kế toán cần biết dòng nào chắc chắn, dòng nào phải kiểm lại.

Cột `canh_bao` gom mọi thứ đáng ngờ — ĐỌC NÓ trước khi báo cáo kết quả cho người dùng.

Phần XML chạy được bằng python hệ thống (chỉ dùng thư viện chuẩn). Phần PDF cần pdfplumber.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _chung import canh_bao, in_json  # noqa: E402
from chuan_hoa import chuan_mst, lam_sach_text, ngay_vn, so_vn  # noqa: E402
from kiem_tra_mst import kiem_tra as kiem_mst  # noqa: E402

COT = ["nguon", "tep", "ky_hieu", "so_hd", "ngay", "mst_ban", "ten_ban",
       "mst_mua", "ten_mua", "tien_hang", "thue_suat", "tien_thue", "tong_cong", "canh_bao"]

# Thuế suất không phải lúc nào cũng là số. Kế toán phân biệt rõ 'thuế suất 0%' (hàng xuất khẩu,
# ĐƯỢC khấu trừ đầu vào) với 'không chịu thuế' (KHÔNG được khấu trừ) — ép về 0 là làm hỏng tờ khai.
TS_DAC_BIET = {"KCT": "KCT", "KKKNT": "KKKNT", "KHAC": "KHAC", "\\": "KHAC", "": None}


def _ten(phan_tu) -> str:
    """Tên thẻ bỏ namespace."""
    return phan_tu.tag.rsplit("}", 1)[-1]


def _tim(goc, *ten_the):
    """Tìm thẻ theo tên ở BẤT KỲ độ sâu nào.

    Nhà cung cấp hóa đơn khác nhau lệch chút ít về cấu trúc, và có bản bọc thêm lớp <TDiep>
    bên ngoài <HDon>. Đi theo đường dẫn tuyệt đối là vỡ; tìm theo tên thì bền hơn nhiều.
    """
    muon = set(ten_the)
    for pt in goc.iter():
        if _ten(pt) in muon and pt.text and pt.text.strip():
            return pt.text.strip()
    return None


def _chuan_thue_suat(gt):
    if gt is None:
        return None
    s = str(gt).strip().upper()
    if s in TS_DAC_BIET:
        return TS_DAC_BIET[s]
    m = re.search(r"(\d+(?:[.,]\d+)?)", s)
    if m:
        return float(m.group(1).replace(",", "."))
    return s or None


def doc_xml(duong_dan: Path) -> dict:
    hang = {c: None for c in COT}
    hang.update({"nguon": "XML", "tep": duong_dan.name, "canh_bao": []})

    try:
        goc = ET.parse(duong_dan).getroot()
    except ET.ParseError as e:
        hang["canh_bao"] = [f"Không đọc được XML: {e}"]
        return hang

    hang["ky_hieu"] = _tim(goc, "KHHDon", "KHHD")
    hang["so_hd"] = _tim(goc, "SHDon", "SHD")
    hang["ngay"] = ngay_vn(_tim(goc, "NLap", "NgayLap"))

    # Người bán / người mua: cần lấy trong đúng nhánh, vì cả hai đều có thẻ <Ten>, <MST>
    ban = mua = None
    for pt in goc.iter():
        t = _ten(pt)
        if t in ("NBan", "NBanHang") and ban is None:
            ban = pt
        elif t in ("NMua", "NMuaHang") and mua is None:
            mua = pt

    if ban is not None:
        hang["ten_ban"] = lam_sach_text(_tim(ban, "Ten"))
        hang["mst_ban"] = chuan_mst(_tim(ban, "MST"))
    if mua is not None:
        hang["ten_mua"] = lam_sach_text(_tim(mua, "Ten"))
        hang["mst_mua"] = chuan_mst(_tim(mua, "MST", "CCCDan"))

    hang["tien_hang"] = so_vn(_tim(goc, "TgTCThue", "TgTienChuaThue"))
    hang["tien_thue"] = so_vn(_tim(goc, "TgTThue", "TgTienThue"))
    hang["tong_cong"] = so_vn(_tim(goc, "TgTTTBSo", "TgTienTTBSo"))

    # Thuế suất: gom từ phần tổng hợp theo từng loại thuế suất. Một hóa đơn có thể có
    # nhiều mức — giữ tất cả thay vì chọn bừa một cái.
    muc = []
    for pt in goc.iter():
        if _ten(pt) == "LTSuat":
            ts = _chuan_thue_suat(_tim(pt, "TSuat"))
            if ts is not None and ts not in muc:
                muc.append(ts)
    if not muc:
        ts = _chuan_thue_suat(_tim(goc, "TSuat"))
        if ts is not None:
            muc = [ts]

    if len(muc) == 1:
        hang["thue_suat"] = muc[0]
    elif len(muc) > 1:
        hang["thue_suat"] = "; ".join(str(m) for m in muc)
        hang["canh_bao"].append(
            f"Hóa đơn có nhiều mức thuế suất ({hang['thue_suat']}) — khi lên bảng kê "
            "phải tách theo từng mức, không gộp chung")
    return hang


# --- PDF ---------------------------------------------------------------------

_NHAN = {
    "so_hd": [r"số\s*hóa\s*đơn", r"số\s*hđ\b", r"\binvoice\s*no"],
    "ky_hieu": [r"ký\s*hiệu"],
    "ngay": [r"ngày\s*(?:lập|hóa\s*đơn)?"],
    "tien_hang": [r"cộng\s*tiền\s*hàng", r"tổng\s*tiền\s*(?:hàng\s*)?chưa\s*(?:có\s*)?thuế",
                  r"cộng\s*thành\s*tiền"],
    "tien_thue": [r"tiền\s*thuế\s*gtgt", r"thuế\s*gtgt"],
    "tong_cong": [r"tổng\s*cộng\s*tiền\s*thanh\s*toán", r"tổng\s*tiền\s*thanh\s*toán",
                  r"tổng\s*cộng"],
}
_SO = r"([\d][\d.,]*)"


def _tim_nhan(van_ban: str, mau_list, so=True):
    for mau in mau_list:
        m = re.search(mau + r"[^\n:]*[:\s]+" + (_SO if so else r"(\S+)"),
                      van_ban, re.IGNORECASE)
        if m:
            return m.group(1)
    return None


def doc_pdf(duong_dan: Path) -> dict:
    hang = {c: None for c in COT}
    hang.update({"nguon": "PDF", "tep": duong_dan.name, "canh_bao": []})

    try:
        import pdfplumber
    except ImportError:
        hang["canh_bao"] = ["Chưa cài pdfplumber — chạy bootstrap.sh"]
        return hang

    try:
        with pdfplumber.open(duong_dan) as pdf:
            van_ban = "\n".join((tr.extract_text() or "") for tr in pdf.pages)
    except Exception as e:
        hang["canh_bao"] = [f"Không mở được PDF: {e}"]
        return hang

    if len(van_ban.strip()) < 40:
        hang["canh_bao"].append(
            "PDF gần như không có chữ — có thể là bản scan, cần OCR (tesseract -l vie). "
            "Chưa bóc tách được gì.")
        return hang

    hang["so_hd"] = _tim_nhan(van_ban, _NHAN["so_hd"], so=False)
    hang["ky_hieu"] = _tim_nhan(van_ban, _NHAN["ky_hieu"], so=False)
    hang["ngay"] = ngay_vn(_tim_nhan(van_ban, _NHAN["ngay"], so=False)) or ngay_vn(van_ban)
    hang["tien_hang"] = so_vn(_tim_nhan(van_ban, _NHAN["tien_hang"]))
    hang["tien_thue"] = so_vn(_tim_nhan(van_ban, _NHAN["tien_thue"]))
    hang["tong_cong"] = so_vn(_tim_nhan(van_ban, _NHAN["tong_cong"]))

    m = re.search(r"thuế\s*suất[^\d%]*(\d+)\s*%", van_ban, re.IGNORECASE)
    if m:
        hang["thue_suat"] = float(m.group(1))
    elif re.search(r"không\s*chịu\s*thuế|KCT", van_ban, re.IGNORECASE):
        hang["thue_suat"] = "KCT"

    # Hai MST đầu tiên trong hóa đơn theo thứ tự thường là bên bán rồi bên mua.
    # Đây là SUY LUẬN theo vị trí, không phải nhãn — nên phải cảnh báo.
    mst = re.findall(r"(?:MST|Mã\s*số\s*thuế)\s*[:\s]*([\d\s\-]{9,20})", van_ban, re.IGNORECASE)
    mst = [chuan_mst(x) for x in mst]
    mst = [x for x in mst if x]
    if mst:
        hang["mst_ban"] = mst[0]
        if len(mst) > 1:
            hang["mst_mua"] = mst[1]

    hang["canh_bao"].append(
        "Đọc từ PDF (bản thể hiện), không phải XML gốc — cần kiểm lại, nhất là thuế suất và MST")
    return hang


# --- Tự kiểm -----------------------------------------------------------------

def tu_kiem(hang: dict) -> None:
    """Ba phép kiểm rẻ bắt được hầu hết lỗi bóc tách."""
    th, tt, tc = hang.get("tien_hang"), hang.get("tien_thue"), hang.get("tong_cong")

    if th is not None and tt is not None and tc is not None:
        lech = abs((th + tt) - tc)
        if lech > 1:
            hang["canh_bao"].append(
                f"Không cân đối: tiền hàng {th:,.0f} + thuế {tt:,.0f} = {th + tt:,.0f} "
                f"nhưng tổng cộng ghi {tc:,.0f} (lệch {lech:,.0f})")

    ts = hang.get("thue_suat")
    if isinstance(ts, (int, float)) and th is not None and tt is not None and th > 0:
        mong_doi = th * Decimal(str(ts)) / Decimal(100)
        if abs(mong_doi - tt) > max(Decimal(1), th * Decimal("0.005")):
            hang["canh_bao"].append(
                f"Thuế suất {ts}% × tiền hàng {th:,.0f} ra {mong_doi:,.0f} "
                f"nhưng tiền thuế ghi {tt:,.0f} — đọc sai một trong hai?")

    for truong, nhan in (("mst_ban", "bên bán"), ("mst_mua", "bên mua")):
        gt = hang.get(truong)
        if gt:
            kq = kiem_mst(gt)
            if kq["tinh_trang"] not in ("hop_le", "ma_dinh_danh", "khong_ket_luan"):
                hang["canh_bao"].append(f"MST {nhan} {gt}: {kq['ghi_chu']}")

    for truong in ("so_hd", "ngay", "mst_ban", "tien_hang", "tong_cong"):
        if hang.get(truong) in (None, ""):
            hang["canh_bao"].append(f"Thiếu {truong} — KHÔNG tự điền, cần kiểm file gốc")


def quet(goc: Path) -> list[Path]:
    if goc.is_file():
        return [goc]
    tep = sorted(p for p in goc.rglob("*") if p.suffix.lower() in (".xml", ".pdf"))
    return tep


def main() -> int:
    p = argparse.ArgumentParser(
        description="Bóc tách hóa đơn điện tử XML/PDF thành bảng chuẩn hoá.")
    p.add_argument("nguon", help="Thư mục hoặc file hóa đơn")
    p.add_argument("--ra", help="File kết quả (.csv, .xlsx hoặc .json)")
    p.add_argument("--dinh-dang", choices=["csv", "json", "xlsx"], help="Ép định dạng kết quả")
    args = p.parse_args()

    goc = Path(args.nguon).expanduser()
    if not goc.exists():
        print(f"Không tìm thấy: {goc}", file=sys.stderr)
        return 1

    tep = quet(goc)
    if not tep:
        print(f"Không có file .xml hoặc .pdf nào trong {goc}", file=sys.stderr)
        return 1

    # XML thắng PDF: bỏ PDF nếu có XML cùng tên
    ten_xml = {t.stem for t in tep if t.suffix.lower() == ".xml"}
    bo_qua = [t for t in tep if t.suffix.lower() == ".pdf" and t.stem in ten_xml]
    tep = [t for t in tep if t not in bo_qua]

    hang_list = []
    for t in tep:
        hang = doc_xml(t) if t.suffix.lower() == ".xml" else doc_pdf(t)
        tu_kiem(hang)
        hang["canh_bao"] = " | ".join(hang["canh_bao"])
        hang_list.append(hang)

    tong_hang = sum(h["tien_hang"] for h in hang_list if h["tien_hang"] is not None)
    tong_thue = sum(h["tien_thue"] for h in hang_list if h["tien_thue"] is not None)
    tong_cong = sum(h["tong_cong"] for h in hang_list if h["tong_cong"] is not None)

    # Trùng số hóa đơn của cùng một người bán — lỗi rất hay gặp, và không tự lộ ra ở đâu khác
    thay = {}
    trung = []
    for h in hang_list:
        khoa = (h.get("mst_ban"), h.get("ky_hieu"), h.get("so_hd"))
        if all(khoa) and khoa in thay:
            trung.append({"so_hd": h["so_hd"], "mst_ban": h["mst_ban"],
                          "tep": [thay[khoa], h["tep"]]})
        elif all(khoa):
            thay[khoa] = h["tep"]

    tom_tat = {
        "so_hoa_don": len(hang_list),
        "tu_xml": sum(1 for h in hang_list if h["nguon"] == "XML"),
        "tu_pdf": sum(1 for h in hang_list if h["nguon"] == "PDF"),
        "pdf_bo_qua_vi_da_co_xml": [t.name for t in bo_qua],
        "tong_tien_hang": tong_hang,
        "tong_tien_thue": tong_thue,
        "tong_thanh_toan": tong_cong,
        "so_dong_co_canh_bao": sum(1 for h in hang_list if h["canh_bao"]),
        "hoa_don_trung": trung,
    }

    if args.ra:
        ra = Path(args.ra).expanduser()
        ra.parent.mkdir(parents=True, exist_ok=True)
        dd = args.dinh_dang or ra.suffix.lstrip(".").lower()
        if dd == "json":
            ra.write_text(json.dumps(hang_list, ensure_ascii=False, indent=2, default=str),
                          encoding="utf-8")
        elif dd == "xlsx":
            from _chung import can_thu_vien
            can_thu_vien("pandas", "openpyxl")
            import pandas as pd
            pd.DataFrame(hang_list, columns=COT).to_excel(ra, index=False)
        else:
            import csv
            with ra.open("w", newline="", encoding="utf-8-sig") as f:
                w = csv.DictWriter(f, fieldnames=COT)
                w.writeheader()
                w.writerows(hang_list)
        tom_tat["tep_ket_qua"] = str(ra)

    if tom_tat["so_dong_co_canh_bao"]:
        canh_bao(f"{tom_tat['so_dong_co_canh_bao']}/{len(hang_list)} hóa đơn có cảnh báo — "
                 "đọc cột canh_bao trước khi báo cáo kết quả")
    if trung:
        canh_bao(f"Có {len(trung)} hóa đơn TRÙNG số — kiểm ngay")

    in_json({"tom_tat": tom_tat, "chi_tiet": hang_list})
    return 0


if __name__ == "__main__":
    sys.exit(main())
