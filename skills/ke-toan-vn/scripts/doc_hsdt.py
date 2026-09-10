#!/usr/bin/env python3
"""Bóc tách hồ sơ dự thầu (HSDT) thành dữ liệu chuẩn hoá, có truy vết tới số trang.

    doc_hsdt.py <thư mục HSDT> --ra hsdt.json

Bố cục thư mục mong đợi: mỗi nhà thầu một thư mục con.

    goi-thau/hsdt/
      ├── Nha thau A/  *.pdf
      ├── Nha thau B/  *.pdf
      └── Nha thau C/  *.pdf

NGUYÊN TẮC: script này KHÔNG kết luận đạt/không đạt. Nó trích dữ liệu và ghi rõ tìm thấy ở
trang nào, để tổ chuyên gia tự đối chiếu với HSMT. Trường nào không tìm thấy trả về null kèm
lý do — TUYỆT ĐỐI không điền 0 hay đoán.

Lý do: chấm thầu là hành vi pháp lý. Một dòng 'không đạt' sai dẫn tới kiến nghị, hủy thầu, và
quy trách nhiệm cá nhân cho người ký biên bản. Người ký chịu trách nhiệm đó, không phải công cụ.
Nên công cụ đưa dữ liệu kèm đường dẫn tới bằng chứng, không đưa kết luận.

BẢO MẬT: không gửi bất kỳ nội dung nào của HSDT ra ngoài. Script chạy hoàn toàn cục bộ.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _chung import can_thu_vien, canh_bao, in_json  # noqa: E402
from chuan_hoa import chuan_mst, lam_sach_text, ngay_vn, so_vn  # noqa: E402

_SO = r"([\d][\d.,]*)"

NHAN = {
    "gia_du_thau": [
        r"giá\s*dự\s*thầu(?:\s*(?:là|:))?",
        r"tổng\s*giá\s*dự\s*thầu",
        r"giá\s*chào\s*thầu",
    ],
    "gia_giam": [
        r"giá\s*trị\s*giảm\s*giá",        # cụ thể nhất, ưu tiên trước
        r"thư\s*giảm\s*giá",
        r"giảm\s*giá",
    ],
    "bao_lanh_tien": [
        r"(?:giá\s*trị\s*)?bảo\s*(?:đảm|lãnh)\s*dự\s*thầu",
    ],
    "doanh_thu_bq": [
        r"doanh\s*thu\s*(?:bình\s*quân|trung\s*bình)",
    ],
}


def _trang_co(van_ban_trang: list[str], mau: str):
    """Trả về số trang đầu tiên khớp mẫu (đánh số từ 1)."""
    for i, t in enumerate(van_ban_trang, 1):
        if re.search(mau, t, re.IGNORECASE):
            return i
    return None


# Số đứng ngay trước các từ này là số đếm, không phải số tiền: "bình quân 3 NĂM gần nhất",
# "giảm 3 %", "03 HỢP ĐỒNG tương tự", "switch 24 CỔNG". Bỏ qua chúng, nếu không sẽ trích ra
# doanh thu bằng 3 đồng — sai thầm lặng và rất khó phát hiện khi nhìn bảng tổng hợp.
_DON_VI_DEM = re.compile(
    r"^\s*(%|năm|ngày|tháng|quý|hợp\s*đồng|cổng|inch|bộ|chiếc|cái|gói|người|lần|"
    r"tuần|giờ|vnd|đồng\s*/)", re.IGNORECASE)


def _la_so_tien(trang: str, m: re.Match) -> bool:
    """Số này có phải số tiền không, hay chỉ là số đếm?"""
    sau = trang[m.end():m.end() + 14]
    if _DON_VI_DEM.match(sau):
        return False
    thuan = re.sub(r"[.,]", "", m.group(0))
    # Số tiền VND thực tế luôn từ hàng nghìn trở lên, hoặc có dấu phân cách nghìn
    return len(thuan) >= 4 or ("." in m.group(0) or "," in m.group(0))


def _tim(van_ban_trang: list[str], mau_list, so=True):
    """Tìm giá trị theo nhãn, trả (giá trị, số trang, đoạn văn bản gốc).

    Với số tiền, quét NHIỀU ứng viên trong cửa sổ sau nhãn và bỏ những số đếm
    (xem _la_so_tien) — nhãn tiếng Việt hay có số đếm chen vào giữa.
    """
    for i, trang in enumerate(van_ban_trang, 1):
        for mau in mau_list:
            for m_nhan in re.finditer(mau, trang, re.IGNORECASE):
                cua_so = trang[m_nhan.end():m_nhan.end() + 120]
                if not so:
                    m = re.search(r"[:\s]+([^\n]{1,60})", cua_so)
                    if m:
                        return m.group(1).strip(), i, _boi_canh(trang, m_nhan.start())
                    continue
                for m_so in re.finditer(r"[\d][\d.,]*", cua_so):
                    if "\n" in cua_so[:m_so.start()]:
                        break            # đã sang dòng khác, không còn thuộc nhãn này
                    if _la_so_tien(cua_so, m_so):
                        return m_so.group(0), i, _boi_canh(trang, m_nhan.start())
    return None, None, None


def _boi_canh(trang: str, vi_tri: int) -> str:
    doan = trang[max(0, vi_tri - 30):vi_tri + 120].replace("\n", " ")
    return re.sub(r"\s+", " ", doan).strip()


def _doc_bang_co_ke(bang, nguon: str) -> list[dict]:
    """Đọc bảng đã được pdfplumber nhận diện qua đường kẻ."""
    if not bang or len(bang) < 2:
        return []
    tieu_de = " ".join(str(o or "") for o in bang[0]).lower()
    if not re.search(r"(tên|hàng\s*hóa|mô\s*tả|nội\s*dung)", tieu_de):
        return []

    ket_qua = []
    for hang in bang[1:]:
        o = [lam_sach_text(x, "") or "" for x in hang if x is not None]
        if not any(o):
            continue
        ten = next((x for x in o if x and len(x) > 3
                    and not re.fullmatch(r"[\d.,\s]*", x)), None)
        if not ten or re.match(r"^(tổng|cộng|stt)\b", ten, re.IGNORECASE):
            continue
        so = [so_vn(x) for x in o
              if x != ten and re.fullmatch(r"[\d.,]+", x.strip()) and so_vn(x) is not None]
        if len(so) < 3:
            continue
        ket_qua.append({
            "ten": ten, "so_luong": so[-3], "don_gia": so[-2], "thanh_tien": so[-1],
            "nguon_trang": nguon,
        })
    return ket_qua


_DVT = re.compile(r"^(bộ|chiếc|cái|gói|hệ|m|m2|m3|kg|tấn|lít|hộp|thùng|ram|cuộn|"
                  r"tờ|quyển|đôi|bao|can|chuyến|lần|người|tháng|năm)$", re.IGNORECASE)
_LA_SO = re.compile(r"^[\d][\d.,]*$")


def _doc_bang_theo_dong(van_ban: str, nguon: str) -> list[dict]:
    """Đọc bảng giá dự thầu từ văn bản thuần, theo từng dòng.

    Rất nhiều HSDT xuất từ Word không có đường kẻ bảng, mà extract_tables() của pdfplumber
    dựa vào đường kẻ; chiến lược 'text' thì cắt vụn chữ thành cột vô nghĩa. Với hình dạng
    bảng giá dự thầu (STT | tên hàng | ĐVT | số lượng | đơn giá | thành tiền), đọc theo dòng
    là công cụ đúng hơn nhiều.

    Quy ước nhận dạng: một dòng hàng hóa kết thúc bằng ÍT NHẤT 3 số. Ba số cuối cùng luôn là
    (số lượng, đơn giá, thành tiền) theo đúng thứ tự đó — thành tiền là số cuối. Lấy ba số
    CUỐI thay vì ba số đầu để tên hàng có chứa số (vd 'OptiPlex 7010') không làm lệch cột.
    """
    ket_qua = []
    for dong in van_ban.splitlines():
        tu = dong.split()
        if len(tu) < 4:
            continue

        duoi = []
        while tu and _LA_SO.match(tu[-1]):
            duoi.insert(0, tu.pop())
        if len(duoi) < 3:
            continue

        while tu and _DVT.match(tu[-1]):
            tu.pop()
        if tu and re.fullmatch(r"\d{1,3}", tu[0]):
            tu.pop(0)                       # số thứ tự

        ten = lam_sach_text(" ".join(tu), "")
        if not ten or len(ten) < 4 or re.match(r"^(tổng|cộng)\b", ten, re.IGNORECASE):
            continue

        so = [so_vn(x) for x in duoi[-3:]]
        if any(v is None for v in so):
            continue

        ket_qua.append({
            "ten": ten,
            "so_luong": so[0],
            "don_gia": so[1],
            "thanh_tien": so[2],
            "nguon_trang": nguon,
        })
    return ket_qua


def _truong(gia_tri, trang, boi_canh, ly_do_neu_thieu):
    """Chuẩn hoá một trường trích được, luôn kèm truy vết."""
    if gia_tri is None:
        return {"gia_tri": None, "nguon_trang": None, "trich_dan": None,
                "ghi_chu": ly_do_neu_thieu}
    return {"gia_tri": gia_tri, "nguon_trang": trang, "trich_dan": boi_canh, "ghi_chu": None}


def doc_mot_nha_thau(thu_muc: Path) -> dict:
    import pdfplumber

    kq = {
        "nha_thau": thu_muc.name,
        "thu_muc": str(thu_muc),
        "tep": [],
        "canh_bao": [],
    }

    tep_pdf = sorted(thu_muc.rglob("*.pdf"))
    if not tep_pdf:
        kq["canh_bao"].append("Không có file PDF nào trong thư mục này")
        return kq

    trang_all, ban_do_trang = [], []
    for t in tep_pdf:
        kq["tep"].append(t.name)
        try:
            with pdfplumber.open(t) as pdf:
                for i, tr in enumerate(pdf.pages, 1):
                    trang_all.append(tr.extract_text() or "")
                    ban_do_trang.append(f"{t.name} tr.{i}")
        except Exception as e:
            kq["canh_bao"].append(f"Không mở được {t.name}: {e}")

    if not any(t.strip() for t in trang_all):
        kq["canh_bao"].append(
            "Toàn bộ PDF không có chữ — có thể là bản scan, cần OCR (tesseract -l vie). "
            "Chưa trích được gì.")
        return kq

    def dinh_vi(so_trang):
        return ban_do_trang[so_trang - 1] if so_trang and so_trang <= len(ban_do_trang) else None

    # --- Giá dự thầu ---------------------------------------------------------
    gt, tr, bc = _tim(trang_all, NHAN["gia_du_thau"])
    kq["gia_du_thau"] = _truong(
        so_vn(gt), dinh_vi(tr), bc,
        "Không tìm thấy nhãn 'giá dự thầu' — kiểm tra đơn dự thầu bằng mắt")

    # --- Thư giảm giá --------------------------------------------------------
    gt, tr, bc = _tim(trang_all, NHAN["gia_giam"])
    kq["gia_giam"] = _truong(
        so_vn(gt), dinh_vi(tr), bc,
        "Không tìm thấy thư giảm giá. Lưu ý: thư giảm giá KHÔNG công khai trong biên bản "
        "mở thầu thì không được xem xét")

    # --- Bảo đảm dự thầu -----------------------------------------------------
    gt, tr, bc = _tim(trang_all, NHAN["bao_lanh_tien"])
    kq["bao_lanh_du_thau"] = _truong(
        so_vn(gt), dinh_vi(tr), bc,
        "Không tìm thấy giá trị bảo đảm dự thầu")

    tr_bl = _trang_co(trang_all, r"bảo\s*(?:đảm|lãnh)\s*dự\s*thầu")
    hieu_luc = None
    if tr_bl:
        vung = " ".join(trang_all[max(0, tr_bl - 1): tr_bl + 1])
        m = re.search(r"(?:có\s*)?hiệu\s*lực[^\n]{0,80}?"
                      r"(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{4})", vung, re.IGNORECASE)
        if m:
            hieu_luc = ngay_vn(m.group(1))
    kq["bao_lanh_hieu_luc_den"] = _truong(
        hieu_luc, dinh_vi(tr_bl), None,
        "Không đọc được ngày hết hiệu lực của bảo đảm dự thầu — kiểm tra bằng mắt")

    # --- Năng lực tài chính --------------------------------------------------
    gt, tr, bc = _tim(trang_all, NHAN["doanh_thu_bq"])
    kq["doanh_thu_binh_quan"] = _truong(
        so_vn(gt), dinh_vi(tr), bc,
        "Không tìm thấy doanh thu bình quân")

    # --- MST -----------------------------------------------------------------
    mst = None
    tr_mst = None
    for i, trang in enumerate(trang_all, 1):
        m = re.search(r"(?:MST|Mã\s*số\s*thuế|Mã\s*số\s*doanh\s*nghiệp)\s*[:\s]*([\d\s\-]{9,20})",
                      trang, re.IGNORECASE)
        if m:
            mst, tr_mst = chuan_mst(m.group(1)), i
            break
    kq["mst"] = _truong(mst, dinh_vi(tr_mst), None, "Không tìm thấy mã số thuế nhà thầu")

    # --- Bảng giá dự thầu (danh mục hàng hóa) --------------------------------
    danh_muc = []
    for t in tep_pdf:
        try:
            with pdfplumber.open(t) as pdf:
                for i, tr_pdf in enumerate(pdf.pages, 1):
                    nguon = f"{t.name} tr.{i}"
                    truoc = len(danh_muc)
                    for bang in (tr_pdf.extract_tables() or []):
                        danh_muc += _doc_bang_co_ke(bang, nguon)
                    if len(danh_muc) == truoc:
                        # Không có đường kẻ bảng — đọc theo dòng văn bản
                        danh_muc += _doc_bang_theo_dong(tr_pdf.extract_text() or "", nguon)
        except Exception as e:
            kq["canh_bao"].append(f"Đọc bảng trong {t.name} lỗi: {e}")

    # Loại trùng: cùng tên + cùng thành tiền có thể bị bắt hai lần bởi hai cách đọc
    thay, loc = set(), []
    for d in danh_muc:
        khoa = (d["ten"], str(d["thanh_tien"]))
        if khoa not in thay:
            thay.add(khoa)
            loc.append(d)
    danh_muc = loc

    kq["danh_muc"] = danh_muc
    if not danh_muc:
        kq["canh_bao"].append(
            "Không đọc được bảng giá dự thầu — có thể bảng nằm trong file Excel riêng, "
            "hoặc PDF không có cấu trúc bảng. Cần nhập tay hoặc kiểm bằng mắt.")

    # --- Kiểm số học từng dòng ----------------------------------------------
    # Đây là 'sửa lỗi' theo NĐ 214/2025: lỗi số học TRONG hồ sơ dự thầu.
    for d in danh_muc:
        sl, dg, tt = d.get("so_luong"), d.get("don_gia"), d.get("thanh_tien")
        if sl is not None and dg is not None and tt is not None:
            mong_doi = sl * dg
            if abs(mong_doi - tt) > 1:
                d["loi_so_hoc"] = {
                    "tinh_ra": mong_doi, "ghi_trong_hsdt": tt,
                    "chenh_lech": tt - mong_doi,
                    "ghi_chu": "Lỗi số học — thuộc diện SỬA LỖI, không phải hiệu chỉnh sai lệch",
                }
                kq["canh_bao"].append(
                    f"Dòng '{d['ten'][:40]}' ({d['nguon_trang']}): {sl} × {dg:,.0f} = "
                    f"{mong_doi:,.0f} nhưng ghi {tt:,.0f}")

    # gia_giam là trường TÙY CHỌN — phần lớn nhà thầu không có thư giảm giá, nên vắng mặt
    # là bình thường chứ không phải vấn đề. Cảnh báo nó chỉ tạo nhiễu, và nhiễu làm người
    # chấm bỏ qua luôn cả cảnh báo thật.
    TUY_CHON = {"gia_giam"}
    thieu = [k for k, v in kq.items()
             if isinstance(v, dict) and k not in TUY_CHON
             and v.get("gia_tri") is None and "ghi_chu" in v]
    if thieu:
        kq["canh_bao"].append(f"Không trích được: {', '.join(thieu)} — cần kiểm tra bằng mắt")

    return kq


def main() -> int:
    p = argparse.ArgumentParser(
        description="Bóc tách HSDT thành dữ liệu chuẩn hoá, có truy vết số trang.",
        epilog="Script KHÔNG kết luận đạt/không đạt — đó là việc của tổ chuyên gia.")
    p.add_argument("thu_muc", help="Thư mục chứa HSDT (mỗi nhà thầu một thư mục con)")
    p.add_argument("--ra", help="File JSON kết quả")
    args = p.parse_args()

    can_thu_vien("pdfplumber")

    goc = Path(args.thu_muc).expanduser()
    if not goc.is_dir():
        print(f"Không phải thư mục: {goc}", file=sys.stderr)
        return 1

    con = sorted(d for d in goc.iterdir() if d.is_dir())
    if not con:
        con = [goc]   # thư mục phẳng: coi cả thư mục là một nhà thầu

    ket_qua = [doc_mot_nha_thau(d) for d in con]

    tom_tat = {
        "so_nha_thau": len(ket_qua),
        "nha_thau": [r["nha_thau"] for r in ket_qua],
        "so_canh_bao": sum(len(r["canh_bao"]) for r in ket_qua),
        "nhac": ("Đây là dữ liệu trích tự động, KHÔNG phải kết quả đánh giá. "
                 "Tổ chuyên gia phải đối chiếu với HSMT và HSDT gốc."),
    }

    if args.ra:
        ra = Path(args.ra).expanduser()
        ra.parent.mkdir(parents=True, exist_ok=True)
        ra.write_text(
            json.dumps({"tom_tat": tom_tat, "nha_thau": ket_qua},
                       ensure_ascii=False, indent=2, default=str),
            encoding="utf-8")
        tom_tat["tep_ket_qua"] = str(ra)

    for r in ket_qua:
        for c in r["canh_bao"]:
            canh_bao(f"[{r['nha_thau']}] {c}")

    in_json({"tom_tat": tom_tat, "nha_thau": ket_qua})
    return 0


if __name__ == "__main__":
    sys.exit(main())
