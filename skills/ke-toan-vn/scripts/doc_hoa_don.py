#!/usr/bin/env python3
"""Bóc tách hóa đơn điện tử (XML theo QĐ 1450/QĐ-TCT, và PDF) thành một bảng chuẩn hoá.

    doc_hoa_don.py <thư mục|file> --ra bang_ke.csv
    doc_hoa_don.py <thư mục> --ra bang_ke.json --dinh-dang json
    doc_hoa_don.py <thư mục> --ca-tin-cay ca.pem --yeu-cau-day-du   # cho bên gọi chặn lại

XML THẮNG PDF. Hóa đơn điện tử là thông điệp dữ liệu (bản XML); PDF chỉ là bản thể hiện, bản
chuyển sang giấy không có hiệu lực giao dịch (Điều 7 NĐ 123/2020 với hóa đơn lập trước 01/7/2026;
khoản 2 và điểm b.2 khoản 4 Điều 5 NĐ 254/2026 từ 01/7/2026). Khi một hóa đơn có cả hai, script
đọc XML; PDF cùng tên chỉ dùng để so tổng tiền.

ĐỌC ≠ XÁC THỰC. Mỗi dòng có `xac_thuc` gồm ba trạng thái riêng (xem xac_thuc_hoa_don.py):
xml_schema, chu_ky, trang_thai_cqt. Tình trạng trên hệ thống cơ quan thuế luôn `not_checked` —
script không có kênh tra cứu được cấp phép và không bịa ra một kết quả.

CỔNG ĐẦY ĐỦ. `tom_tat.tong_tien_hang` (và các tổng khác) là TỔNG QUAN SÁT: chỉ cộng các số đọc
được, hóa đơn trùng chỉ cộng một lần. `tom_tat.tong_da_kiem` chỉ có khi MỌI hóa đơn đều đủ dữ
liệu và không có vấn đề cần xem; ngược lại nó để trống. `tom_tat.trang_thai`:
  draft         đủ điều kiện để kế toán xem và duyệt — CHƯA phải đã duyệt
  needs_review  có hóa đơn thiếu số, lỗi đọc, trùng, lệch, chữ ký hỏng/thiếu... (xem ly_do)
Script không bao giờ tự cho ra "đã duyệt" — việc đó thuộc người có trách nhiệm
(ho_so_kiem_toan.py duyet).

Mã thoát: 0 (kể cả needs_review, để giữ cách dùng cũ); 2 khi có --yeu-cau-day-du mà lô
needs_review; 1 khi lỗi đầu vào.

Phần XML chạy được bằng python hệ thống. PDF cần pdfplumber; kiểm chữ ký cần signxml.
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
import _ho_so as H  # noqa: E402
from _chung import canh_bao, home_don_vi, in_json, o_an_toan, tim_home  # noqa: E402
from che_do_ke_toan import che_do_hoa_don  # noqa: E402
from chuan_hoa import chuan_mst, lam_sach_text, ngay_vn, so_vn  # noqa: E402
from kiem_tra_mst import kiem_tra as kiem_mst  # noqa: E402
import xac_thuc_hoa_don as xt  # noqa: E402

PHIEN_BAN_BO_DOC = "2.0"

COT = ["nguon", "tep", "ky_hieu", "so_hd", "ngay", "mst_ban", "ten_ban",
       "mst_mua", "ten_mua", "tien_hang", "thue_suat", "tien_thue", "tong_cong", "canh_bao",
       "che_do_hoa_don", "xml_schema", "chu_ky", "trang_thai_cqt", "trang_thai_dong"]

# Thuế suất không phải lúc nào cũng là số. Kế toán phân biệt rõ 'thuế suất 0%' (hàng xuất khẩu,
# ĐƯỢC khấu trừ đầu vào) với 'không chịu thuế' (KHÔNG được khấu trừ) — ép về 0 là làm hỏng tờ khai.
TS_DAC_BIET = {"KCT": "KCT", "KKKNT": "KKKNT", "KHAC": "KHAC", "\\": "KHAC", "": None}

GIOI_HAN_XML = 20 * 1024 * 1024
GIOI_HAN_PDF = 50 * 1024 * 1024

# Vấn đề làm lô phải để người xem (needs_review). Cảnh báo khác (vd nhiều mức thuế suất) chỉ
# là lưu ý khi lên bảng kê.
CHAN = {"loi_doc", "thieu", "can_doi", "nhieu_gia_tri", "thue_suat", "mst", "chu_ky_hong",
        "chu_ky_thieu", "lech_pdf", "trung"}


def _ten(phan_tu) -> str:
    """Tên thẻ bỏ namespace."""
    return phan_tu.tag.rsplit("}", 1)[-1] if isinstance(phan_tu.tag, str) else ""


def _tim(goc, *ten_the, hang: dict | None = None):
    """Tìm thẻ theo tên ở bất kỳ độ sâu nào TRONG phạm vi `goc` (một hóa đơn).

    Nhà cung cấp lệch nhau về cấu trúc, đi theo đường dẫn tuyệt đối là vỡ. Nhưng tìm theo tên
    thì phải chịu được thẻ lặp: nếu cùng tên mà khác giá trị thì KHÔNG chọn bừa cái đầu tiên —
    trả None và ghi cảnh báo, để kế toán xem file gốc.
    """
    muon = set(ten_the)
    gt = []
    for pt in goc.iter():
        if _ten(pt) in muon and pt.text and pt.text.strip() and pt.text.strip() not in gt:
            gt.append(pt.text.strip())
    if len(gt) > 1:
        if hang is not None:
            _van_de(hang, "nhieu_gia_tri",
                    f"Thẻ {'/'.join(ten_the)} có nhiều giá trị khác nhau ({', '.join(gt[:4])}) — "
                    "không tự chọn, cần kiểm file gốc")
        return None
    return gt[0] if gt else None


def _van_de(hang: dict, ma: str, thong_diep: str) -> None:
    hang["canh_bao"].append(thong_diep)
    hang["_van_de"].add(ma)


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


def _hang_trong(nguon: str, tep: str) -> dict:
    hang = {c: None for c in COT}
    hang.update({"nguon": nguon, "tep": tep, "canh_bao": [], "_van_de": set()})
    return hang


def _kiem_an_toan_xml(du_lieu: bytes) -> str | None:
    """Hóa đơn điện tử không dùng DTD. File có DOCTYPE/ENTITY là bất thường — từ chối luôn, để
    không phải tin vào giới hạn mở rộng thực thể của trình đọc XML (tấn công 'billion laughs')."""
    if len(du_lieu) > GIOI_HAN_XML:
        return f"File XML {len(du_lieu) / 1048576:.1f} MB vượt giới hạn {GIOI_HAN_XML >> 20} MB"
    if re.search(rb"<!(DOCTYPE|ENTITY)", du_lieu, re.IGNORECASE):
        return "XML có khai báo DOCTYPE/ENTITY — hóa đơn điện tử không dùng; từ chối đọc"
    return None


def _doc_mot_hoa_don(hd, hang: dict) -> None:
    hang["ky_hieu"] = _tim(hd, "KHHDon", "KHHD", hang=hang)
    hang["so_hd"] = _tim(hd, "SHDon", "SHD", hang=hang)
    hang["ngay"] = ngay_vn(_tim(hd, "NLap", "NgayLap", hang=hang))

    # Người bán / người mua: cần lấy trong đúng nhánh, vì cả hai đều có thẻ <Ten>, <MST>
    ban = mua = None
    for pt in hd.iter():
        t = _ten(pt)
        # DSCKS/NBan (vùng chữ ký) cũng tên NBan nhưng không có thông tin người bán — bỏ qua
        co_tt = any(_ten(c) in ("MST", "Ten", "CCCDan") for c in pt.iter())
        if t in ("NBan", "NBanHang") and ban is None and co_tt:
            ban = pt
        elif t in ("NMua", "NMuaHang") and mua is None and co_tt:
            mua = pt
    if ban is not None:
        hang["ten_ban"] = lam_sach_text(_tim(ban, "Ten", hang=hang))
        hang["mst_ban"] = chuan_mst(_tim(ban, "MST", hang=hang))
    if mua is not None:
        hang["ten_mua"] = lam_sach_text(_tim(mua, "Ten", hang=hang))
        hang["mst_mua"] = chuan_mst(_tim(mua, "MST", "CCCDan", hang=hang))

    hang["tien_hang"] = so_vn(_tim(hd, "TgTCThue", "TgTienChuaThue", hang=hang))
    hang["tien_thue"] = so_vn(_tim(hd, "TgTThue", "TgTienThue", hang=hang))
    hang["tong_cong"] = so_vn(_tim(hd, "TgTTTBSo", "TgTienTTBSo", hang=hang))

    # Thuế suất: gom từ phần tổng hợp theo từng loại thuế suất (hoặc từng dòng hàng). Một hóa
    # đơn có thể có nhiều mức — giữ tất cả thay vì chọn bừa một cái.
    muc = []
    nhom = [pt for pt in hd.iter() if _ten(pt) == "LTSuat"] or \
        [pt for pt in hd.iter() if _ten(pt) == "HHDVu"] or [hd]
    for pt in nhom:
        for con in pt.iter():
            if _ten(con) == "TSuat" and con.text and con.text.strip():
                ts = _chuan_thue_suat(con.text)
                if ts is not None and ts not in muc:
                    muc.append(ts)
    if len(muc) == 1:
        hang["thue_suat"] = muc[0]
    elif len(muc) > 1:
        hang["thue_suat"] = "; ".join(str(m) for m in muc)
        hang["canh_bao"].append(
            f"Hóa đơn có nhiều mức thuế suất ({hang['thue_suat']}) — khi lên bảng kê "
            "phải tách theo từng mức, không gộp chung")
    if not any(hang[k] is not None for k in ("so_hd", "ky_hieu", "tien_hang", "tong_cong")):
        _van_de(hang, "loi_doc", "Không nhận ra cấu trúc hóa đơn (QĐ 1450) trong file này")


def doc_xml(duong_dan: Path, ca: str | None = None, xsd: str | None = None) -> list[dict]:
    """Mỗi hóa đơn trong file một dòng. Một thông điệp (<TDiep>) có thể chứa nhiều <HDon>."""
    if duong_dan.stat().st_size > GIOI_HAN_XML:
        hang = _hang_trong("XML", duong_dan.name)
        _van_de(hang, "loi_doc", f"File XML vượt giới hạn {GIOI_HAN_XML >> 20} MB — không đọc")
        hang["xac_thuc"] = {"xml_schema": "fail", "chu_ky": "not_checked",
                            "trang_thai_cqt": "not_checked"}
        return [hang]
    du_lieu = duong_dan.read_bytes()
    loi = _kiem_an_toan_xml(du_lieu)
    goc = None
    if loi is None:
        try:
            goc = ET.fromstring(du_lieu)
        except ET.ParseError as e:
            loi = f"Không đọc được XML: {e}"
    if goc is None:
        hang = _hang_trong("XML", duong_dan.name)
        _van_de(hang, "loi_doc", loi)
        hang["xac_thuc"] = {"xml_schema": "fail", "chu_ky": "not_checked",
                            "trang_thai_cqt": "not_checked"}
        return [hang]

    luoc_do = xt.kiem_xsd(du_lieu, xsd)
    cac_hd = [pt for pt in goc.iter() if _ten(pt) == "HDon"] or [goc]
    ra = []
    for i, hd in enumerate(cac_hd):
        hang = _hang_trong("XML", duong_dan.name if len(cac_hd) == 1
                           else f"{duong_dan.name}#{i + 1}")
        _doc_mot_hoa_don(hd, hang)
        ck = xt.kiem_chu_ky(du_lieu, i, ca)
        hang["xac_thuc"] = {"xml_schema": luoc_do, **ck, "trang_thai_cqt": "not_checked"}
        if luoc_do == "fail":
            _van_de(hang, "loi_doc", "XML không khớp lược đồ XSD đã cung cấp")
        if ck["chu_ky"] == "invalid":
            _van_de(hang, "chu_ky_hong", f"Chữ ký số người bán KHÔNG hợp lệ: {ck['ly_do']}")
        elif ck["chu_ky"] == "absent":
            _van_de(hang, "chu_ky_thieu",
                    "Không có chữ ký số người bán — chỉ chấp nhận với loại hóa đơn được miễn "
                    "(vd khởi tạo từ máy tính tiền); cần kiểm")
        ra.append(hang)
    return ra


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
    hang = _hang_trong("PDF", duong_dan.name)
    hang["xac_thuc"] = {"xml_schema": "unsupported", "chu_ky": "not_checked",
                        "trang_thai_cqt": "not_checked",
                        "ly_do": "PDF là bản thể hiện; không có XML gốc để kiểm, chữ ký PDF "
                                 "(nếu có) không được kiểm"}
    if duong_dan.stat().st_size > GIOI_HAN_PDF:
        _van_de(hang, "loi_doc", f"File PDF vượt giới hạn {GIOI_HAN_PDF >> 20} MB — không đọc")
        return hang
    try:
        import pdfplumber
    except ImportError:
        _van_de(hang, "loi_doc", "Chưa cài pdfplumber — chạy bootstrap.sh")
        return hang

    try:
        with pdfplumber.open(duong_dan) as pdf:
            van_ban = "\n".join((tr.extract_text() or "") for tr in pdf.pages)
    except Exception as e:
        _van_de(hang, "loi_doc", f"Không mở được PDF: {e}")
        return hang

    if len(van_ban.strip()) < 40:
        _van_de(hang, "loi_doc",
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
    """Các phép kiểm rẻ bắt được hầu hết lỗi bóc tách."""
    if "loi_doc" in hang["_van_de"]:
        return
    th, tt, tc = hang.get("tien_hang"), hang.get("tien_thue"), hang.get("tong_cong")

    if th is not None and tt is not None and tc is not None:
        lech = abs((th + tt) - tc)
        if lech > 1:
            _van_de(hang, "can_doi",
                    f"Không cân đối: tiền hàng {th:,.0f} + thuế {tt:,.0f} = {th + tt:,.0f} "
                    f"nhưng tổng cộng ghi {tc:,.0f} (lệch {lech:,.0f})")

    ts = hang.get("thue_suat")
    if isinstance(ts, (int, float)) and th is not None and tt is not None and th > 0:
        mong_doi = th * Decimal(str(ts)) / Decimal(100)
        if abs(mong_doi - tt) > max(Decimal(1), th * Decimal("0.005")):
            _van_de(hang, "thue_suat",
                    f"Thuế suất {ts}% × tiền hàng {th:,.0f} ra {mong_doi:,.0f} "
                    f"nhưng tiền thuế ghi {tt:,.0f} — đọc sai một trong hai?")
    # Tiền thuế chỉ được vắng khi thuế suất không phải số dương (KCT, KKKNT, 0%).
    if isinstance(ts, (int, float)) and ts > 0 and tt is None:
        _van_de(hang, "thieu", "Thiếu tien_thue dù thuế suất > 0 — KHÔNG tự điền")

    for truong, nhan in (("mst_ban", "bên bán"), ("mst_mua", "bên mua")):
        gt = hang.get(truong)
        if gt:
            kq = kiem_mst(gt)
            if kq["tinh_trang"] not in ("hop_le", "ma_dinh_danh", "khong_ket_luan"):
                _van_de(hang, "mst", f"MST {nhan} {gt}: {kq['ghi_chu']}")

    for truong in ("so_hd", "ngay", "mst_ban", "tien_hang", "tong_cong"):
        if hang.get(truong) in (None, ""):
            _van_de(hang, "thieu", f"Thiếu {truong} — KHÔNG tự điền, cần kiểm file gốc")


def quet(goc: Path) -> list[Path]:
    if goc.is_file():
        return [goc]
    tep = sorted(p for p in goc.rglob("*") if p.suffix.lower() in (".xml", ".pdf"))
    return tep


def _so_pdf_cung_ten(hang_xml: list[dict], pdf: Path) -> None:
    """PDF cùng tên với XML: không đọc làm hóa đơn riêng, nhưng so tổng tiền — bộ hồ sơ mà bản
    thể hiện ghi số khác bản gốc là dấu hiệu nhầm file hoặc sửa tay."""
    if len(hang_xml) != 1 or hang_xml[0]["tong_cong"] is None:
        return
    try:
        import pdfplumber  # noqa: F401
    except ImportError:
        return
    p = doc_pdf(pdf)
    if p["tong_cong"] is not None and abs(p["tong_cong"] - hang_xml[0]["tong_cong"]) > 1:
        _van_de(hang_xml[0], "lech_pdf",
                f"Bản PDF cùng tên ({pdf.name}) ghi tổng thanh toán {p['tong_cong']:,.0f}, khác "
                f"XML {hang_xml[0]['tong_cong']:,.0f} — kiểm lại bộ hồ sơ")


def _tong(ds: list[dict], truong: str):
    return sum((h[truong] for h in ds if h[truong] is not None), Decimal(0))


def tong_hop(hang_list: list[dict], bo_qua: list[Path]) -> dict:
    # Trùng số hóa đơn của cùng một người bán — lỗi rất hay gặp, và không tự lộ ra ở đâu khác.
    # Bản trùng thứ hai trở đi KHÔNG cộng vào tổng (cộng là đếm hai lần một khoản thuế).
    thay, trung = {}, []
    for h in hang_list:
        khoa = (h.get("mst_ban"), h.get("ky_hieu"), h.get("so_hd"))
        if all(khoa) and khoa in thay:
            trung.append({"so_hd": h["so_hd"], "mst_ban": h["mst_ban"],
                          "tep": [thay[khoa], h["tep"]]})
            _van_de(h, "trung", f"Trùng hóa đơn với {thay[khoa]} — không cộng vào tổng")
            h["_trung"] = True
        elif all(khoa):
            thay[khoa] = h["tep"]
    cong = [h for h in hang_list if not h.get("_trung")]

    for h in hang_list:
        chan = sorted(h["_van_de"] & CHAN)
        h["trang_thai_dong"] = ("trung" if h.get("_trung") else "loi_doc" if "loi_doc" in chan
                                else "thieu_du_lieu" if "thieu" in chan
                                else "can_xem" if chan else "ok")
    thieu_tien = sum(1 for h in cong if "loi_doc" not in h["_van_de"]
                     and (h["tien_hang"] is None or h["tong_cong"] is None))
    day_du = all(h["trang_thai_dong"] == "ok" for h in hang_list) and bool(hang_list)
    ly_do = sorted({f"{h['tep']}: {h['trang_thai_dong']}" for h in hang_list
                    if h["trang_thai_dong"] != "ok"})
    tong = {"tien_hang": _tong(cong, "tien_hang"), "tien_thue": _tong(cong, "tien_thue"),
            "tong_thanh_toan": _tong(cong, "tong_cong")}
    return {
        "so_hoa_don": len(hang_list),
        "tu_xml": sum(1 for h in hang_list if h["nguon"] == "XML"),
        "tu_pdf": sum(1 for h in hang_list if h["nguon"] == "PDF"),
        "pdf_bo_qua_vi_da_co_xml": [t.name for t in bo_qua],
        "tong_tien_hang": tong["tien_hang"],
        "tong_tien_thue": tong["tien_thue"],
        "tong_thanh_toan": tong["tong_thanh_toan"],
        "tong_la": "quan_sat",
        "tong_da_kiem": tong if day_du else None,
        "so_dong_co_canh_bao": sum(1 for h in hang_list if h["canh_bao"]),
        "hoa_don_trung": trung,
        "kiem_soat": {
            "so_hoa_don": len(hang_list),
            "so_dong_loi_doc": sum(1 for h in hang_list if h["trang_thai_dong"] == "loi_doc"),
            "so_dong_thieu_tien": thieu_tien,
            "so_dong_trung_khong_cong": len(trung),
            "so_dong_can_xem": sum(1 for h in hang_list
                                   if h["trang_thai_dong"] in ("can_xem", "thieu_du_lieu")),
            "du_lieu_day_du": day_du,
        },
        "trang_thai": "draft" if day_du else "needs_review",
        "ly_do_trang_thai": ly_do,
        "luu_y": "draft = đủ điều kiện để người có trách nhiệm xem và duyệt, KHÔNG phải đã duyệt. "
                 "Tình trạng hóa đơn trên hệ thống cơ quan thuế chưa được kiểm (not_checked).",
        "phien_ban_bo_doc": PHIEN_BAN_BO_DOC,
    }


def _dong_xuat(h: dict) -> dict:
    x = h.get("xac_thuc") or {}
    return {**{c: o_an_toan(h.get(c)) for c in COT},
            "xml_schema": x.get("xml_schema"), "chu_ky": x.get("chu_ky"),
            "trang_thai_cqt": x.get("trang_thai_cqt")}


def ghi_ho_so(args, goc: Path, tep: list[Path], tom_tat: dict) -> str:
    home_dv, don_vi = home_don_vi(tim_home(), args.don_vi)
    run_id = H.tao_run_id()
    ma_nguon = Path(__file__).resolve()
    goc_nhan = goc if goc.is_dir() else goc.parent
    phat_lai = [str(goc.resolve())]
    for co, gt in (("--ca-tin-cay", args.ca_tin_cay), ("--xsd", args.xsd)):
        if gt:
            phat_lai += [co, str(Path(gt).resolve())]
    dau_ra = []
    if args.ra:
        ra = Path(args.ra).expanduser().resolve()
        dau_ra = [{"nhan": ra.name, "sha256": H.bam_tep(ra), "_duong_dan": str(ra)}]
    H.ghi_ho_so(home_dv, {
        "schema_version": H.SCHEMA, "run_id": run_id, "loai_ban_ghi": "hoa_don",
        "cong_cu": "doc_hoa_don.py", "quy_trinh": None, "loai": "hoa_don", "don_vi": don_vi,
        "phap_nhan": None, "ky": None, "skill": H.phien_ban_skill(),
        # "Quy tắc" của lần đọc là chính bộ đọc: đổi bộ đọc là đổi cách ra số.
        "quy_tac": {"nhan": f"{ma_nguon.name} v{PHIEN_BAN_BO_DOC}", "sha256": H.bam_tep(ma_nguon),
                    "_duong_dan": str(ma_nguon)},
        "danh_muc": None,
        "tham_so": {"ca_tin_cay": bool(args.ca_tin_cay), "xsd": bool(args.xsd)},
        "dau_vao": [{"nhan": str(t.resolve().relative_to(goc_nhan.resolve())), "vai": "hoa_don",
                     "sha256": H.bam_tep(t), "_duong_dan": str(t.resolve())} for t in tep],
        "dau_ra": dau_ra,
        "ket_qua_tom_tat": H.bo_duong_dan(tom_tat), "ket_qua_sha256": H.bam_ket_qua(tom_tat),
        "canh_bao": [], "ngoai_le": [],
        "trang_thai_ket_qua": tom_tat["trang_thai"], "ly_do_trang_thai": tom_tat["ly_do_trang_thai"],
        "nguoi_lap": H.nguoi(args.nguoi_lap), "sua_doi_cho": None, "thoi_gian": H.bay_gio(),
        "_phat_lai": {"script": "doc_hoa_don.py", "truong": "tom_tat", "args": phat_lai},
    })
    return run_id


def main() -> int:
    p = argparse.ArgumentParser(
        description="Bóc tách hóa đơn điện tử XML/PDF thành bảng chuẩn hoá.")
    p.add_argument("nguon", help="Thư mục hoặc file hóa đơn")
    p.add_argument("--ra", help="File kết quả (.csv, .xlsx hoặc .json)")
    p.add_argument("--dinh-dang", choices=["csv", "json", "xlsx"], help="Ép định dạng kết quả")
    p.add_argument("--ca-tin-cay", help="File PEM các chứng thư CA tin cậy để kiểm chữ ký số")
    p.add_argument("--xsd", help="Lược đồ XSD để kiểm cấu trúc XML (cần lxml)")
    p.add_argument("--yeu-cau-day-du", action="store_true",
                   help="Mã thoát 2 nếu lô needs_review (cho bên gọi chặn bước sau)")
    p.add_argument("--ghi-ho-so", action="store_true",
                   help="Ghi hồ sơ lần đọc (mã băm từng file, kết quả, trạng thái) để duyệt/xuất "
                        "gói kiểm toán bằng ho_so_kiem_toan.py")
    p.add_argument("--don-vi", help="Mã đơn vị cho hồ sơ (mặc định KE_TOAN_VN_DON_VI)")
    p.add_argument("--nguoi-lap", help="Tên người chạy (tự khai)")
    args = p.parse_args()

    goc = Path(args.nguon).expanduser()
    if not goc.exists():
        print(f"Không tìm thấy: {goc}", file=sys.stderr)
        return 1

    tep = quet(goc)
    if not tep:
        print(f"Không có file .xml hoặc .pdf nào trong {goc}", file=sys.stderr)
        return 1

    # XML thắng PDF: PDF cùng tên với một XML không đọc thành hóa đơn riêng
    theo_ten_xml = {t.stem: t for t in tep if t.suffix.lower() == ".xml"}
    bo_qua = [t for t in tep if t.suffix.lower() == ".pdf" and t.stem in theo_ten_xml]
    tep = [t for t in tep if t not in bo_qua]

    hang_list = []
    for t in tep:
        if t.suffix.lower() == ".xml":
            cac = doc_xml(t, args.ca_tin_cay, args.xsd)
            pdf = next((b for b in bo_qua if b.stem == t.stem), None)
            for h in cac:
                tu_kiem(h)
            if pdf is not None:
                _so_pdf_cung_ten(cac, pdf)
        else:
            cac = [doc_pdf(t)]
            tu_kiem(cac[0])
        for h in cac:
            ngay = h.get("ngay")
            h["che_do_hoa_don"] = che_do_hoa_don(ngay)["id"] if ngay else None
        hang_list.extend(cac)

    tom_tat = tong_hop(hang_list, bo_qua)
    for h in hang_list:
        h["canh_bao"] = " | ".join(h["canh_bao"])
        h.pop("_van_de", None)
        h.pop("_trung", None)

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
            pd.DataFrame([_dong_xuat(h) for h in hang_list], columns=COT).to_excel(
                ra, index=False)
        else:
            import csv
            with ra.open("w", newline="", encoding="utf-8-sig") as f:
                w = csv.DictWriter(f, fieldnames=COT)
                w.writeheader()
                w.writerows(_dong_xuat(h) for h in hang_list)
        tom_tat["tep_ket_qua"] = str(ra)

    if tom_tat["so_dong_co_canh_bao"]:
        canh_bao(f"{tom_tat['so_dong_co_canh_bao']}/{len(hang_list)} hóa đơn có cảnh báo — "
                 "đọc cột canh_bao trước khi báo cáo kết quả")
    if tom_tat["hoa_don_trung"]:
        canh_bao(f"Có {len(tom_tat['hoa_don_trung'])} hóa đơn TRÙNG số — kiểm ngay")

    run_id = ghi_ho_so(args, goc, tep + bo_qua, tom_tat) if args.ghi_ho_so else None
    in_json({"tom_tat": tom_tat, "chi_tiet": hang_list, "run_id": run_id})
    if args.yeu_cau_day_du and tom_tat["trang_thai"] != "draft":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
