#!/usr/bin/env python3
"""Lập phiếu đối chiếu kỹ thuật giữa yêu cầu HSMT và thông số nhà thầu chào.

    cham_ky_thuat.py <thư mục HSDT> --yeu-cau yeu_cau_ky_thuat.csv --ra phieu_cham.xlsx
    cham_ky_thuat.py <thư mục HSDT> --hsmt hsmt.pdf --ra phieu_cham.xlsx

RANH GIỚI QUAN TRỌNG — script này KHÔNG chấm đạt/không đạt.

Đánh giá kỹ thuật là nơi tập trung nhiều nhận định chuyên môn nhất trong cả quy trình chấm thầu:
"tương đương", "đáp ứng về cơ bản", "xuất xứ chấp nhận được" đều là những phán đoán mà chỉ người
có chuyên môn và chịu trách nhiệm pháp lý mới được kết luận. Script chỉ làm ba việc:

  1. Xếp YÊU CẦU và CHÀO cạnh nhau, kèm số trang để tổ chuyên gia đối chiếu được ngay;
  2. Đối chiếu MÁY những gì đối chiếu khách quan được — thiếu dữ liệu, và số nhỏ hơn ngưỡng;
  3. Để TRỐNG cột kết luận cho tổ chuyên gia điền.

Cột `doi_chieu_may` chỉ nhận bốn giá trị:
    khop            số/chuỗi chào đáp ứng ngưỡng — vẫn cần người xác nhận
    thap_hon        chào NHỎ HƠN ngưỡng số học (vd RAM 8GB < 16GB) — khách quan
    thieu_du_lieu   không tìm thấy tiêu chí này trong HSDT
    can_nguoi_xem   khác loại, không so được bằng máy (xuất xứ, thương hiệu, mô tả)

Kết quả sau khi tổ chuyên gia điền cột "ket_luan" được nạp lại vào so_sanh_thau.py qua
--ket-qua-ky-thuat, để giới hạn nhóm "vượt bước kỹ thuật" khi lấy đơn giá cao nhất hiệu chỉnh
phần chào thiếu (điểm c khoản 2 Điều 31 NĐ 214/2025).

BẢO MẬT: chạy hoàn toàn cục bộ, không gửi nội dung HSDT ra ngoài.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _chung import can_thu_vien, canh_bao, in_json  # noqa: E402
from chuan_hoa import lam_sach_text  # noqa: E402

COT = ["nha_thau", "mat_hang", "tieu_chi", "yeu_cau_hsmt", "nha_thau_chao",
       "nguon_trang", "doi_chieu_may", "ghi_chu_may", "ket_luan", "y_kien_to_chuyen_gia"]

LUU_Y = ("PHIẾU ĐỐI CHIẾU KỸ THUẬT — chưa phải kết quả đánh giá. Cột 'ket_luan' do tổ chuyên gia "
         "điền Đạt / Không đạt sau khi đối chiếu HSMT và HSDT gốc. Cột 'doi_chieu_may' chỉ là "
         "gợi ý máy đối chiếu được, không thay cho nhận định chuyên môn.")

# Đơn vị đo hay gặp trong thông số thiết bị tin học, để so sánh số học có ý nghĩa
_DON_VI = r"(gb|tb|mb|ghz|mhz|inch|\"|thang|tháng|nam|năm|w|wh|mah|ppm|dpi|cm|mm|kg)"
_SO_DV = re.compile(r"(\d+(?:[.,]\d+)?)\s*" + _DON_VI, re.IGNORECASE)
# Từ báo hiệu ngưỡng tối thiểu — chỉ khi có nó thì 'nhỏ hơn' mới chắc chắn là không đáp ứng
_TOI_THIEU = re.compile(r"(trở lên|tối thiểu|từ\s|>=|≥|min)", re.IGNORECASE)
_QUY_DOI = {"tb": ("gb", 1024), "mb": ("gb", 1 / 1024), "ghz": ("mhz", 1000)}


def khong_dau(s: str) -> str:
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn").replace("đ", "d")


def chuan_ten_cot(s: str) -> str:
    """Chuẩn hoá tên cột để so khớp: bỏ dấu, và coi '_' '-' như dấu cách.

    Tiêu đề cột trong file thật viết đủ kiểu: 'tieu_chi', 'Tiêu chí', 'TieuChi', 'tieu-chi'.
    Nếu chỉ bỏ dấu mà giữ nguyên gạch dưới thì 'tieu_chi' không khớp 'tieu chi' và script
    báo thiếu cột trong khi cột đang nằm ngay đó.
    """
    return re.sub(r"[^a-z0-9]+", " ", khong_dau(s)).strip()


def _do_luong(chuoi: str) -> dict[str, float]:
    """Bóc mọi cặp (số, đơn vị) trong chuỗi, quy về đơn vị chuẩn."""
    ra: dict[str, float] = {}
    for so, dv in _SO_DV.findall(chuoi or ""):
        gia_tri = float(so.replace(".", "").replace(",", ".")) if so.count(".") > 1 \
            else float(so.replace(",", "."))
        dv = khong_dau(dv).strip('"') or "inch"
        if dv in _QUY_DOI:
            dv_moi, he_so = _QUY_DOI[dv]
            gia_tri, dv = gia_tri * he_so, dv_moi
        # Giữ giá trị LỚN NHẤT cho mỗi đơn vị: "SSD 512 GB NVMe" chỉ có một số, nhưng
        # "16 GB DDR4 (2 x 8 GB)" thì con số có nghĩa là 16, không phải 8.
        ra[dv] = max(ra.get(dv, gia_tri), gia_tri)
    return ra


def doi_chieu(yeu_cau: str, chao: str | None) -> tuple[str, str]:
    """Đối chiếu một tiêu chí. Trả về (doi_chieu_may, ghi_chu_may)."""
    if chao is None or not str(chao).strip():
        return "thieu_du_lieu", "Không tìm thấy tiêu chí này trong HSDT — kiểm tra bằng mắt"

    yc, ch = _do_luong(yeu_cau), _do_luong(chao)
    chung = set(yc) & set(ch)

    if chung:
        thap = [(dv, yc[dv], ch[dv]) for dv in chung if ch[dv] < yc[dv]]
        if thap:
            dv, y, c = thap[0]
            neu_toi_thieu = bool(_TOI_THIEU.search(yeu_cau))
            return ("thap_hon" if neu_toi_thieu else "can_nguoi_xem",
                    f"Chào {c:g} {dv} < yêu cầu {y:g} {dv}"
                    + ("" if neu_toi_thieu else " — HSMT không ghi rõ 'trở lên', cần người xác định"))
        return "khop", f"Số liệu đáp ứng ngưỡng ({', '.join(f'{d}: {ch[d]:g}≥{yc[d]:g}' for d in chung)})"

    # Không có số để so → so chuỗi, và chỉ dám kết luận khi trùng hẳn
    if khong_dau(chao).strip() and khong_dau(chao).strip() in khong_dau(yeu_cau):
        return "khop", "Nội dung chào nằm trong phạm vi yêu cầu"
    return "can_nguoi_xem", "Không so được bằng máy — cần người đọc và quyết định"


def doc_yeu_cau(duong_dan: Path) -> list[dict]:
    """Đọc yêu cầu kỹ thuật từ CSV/Excel, hoặc dò trong HSMT dạng PDF."""
    import pandas as pd

    if duong_dan.suffix.lower() != ".pdf":
        khung = (pd.read_csv(duong_dan, dtype=str) if duong_dan.suffix.lower() == ".csv"
                 else pd.read_excel(duong_dan, dtype=str))
        khung.columns = [lam_sach_text(c, "") for c in khung.columns]

        def tim(*tu):
            for c in khung.columns:
                if any(t in chuan_ten_cot(c) for t in tu):
                    return c
            return None

        # Tìm cột cụ thể trước, chung chung sau — 'ten_hang_hoa' cũng chứa 'ten', nên nếu
        # hỏi 'ten' trước thì cột mặt hàng sẽ nuốt mất cột khác.
        c_tc = tim("tieu chi", "chi tieu")
        c_yc = tim("yeu cau", "toi thieu")
        c_mh = tim("mat hang", "ten hang", "hang hoa", "ten")
        if not (c_tc and c_yc):
            raise SystemExit(f"File yêu cầu phải có cột 'tieu_chi' và 'yeu_cau'. "
                             f"Đang có: {list(khung.columns)}")
        return [{"mat_hang": lam_sach_text(r[c_mh], "") if c_mh else "",
                 "tieu_chi": lam_sach_text(r[c_tc], ""),
                 "yeu_cau": lam_sach_text(r[c_yc], "")}
                for _, r in khung.iterrows() if lam_sach_text(r[c_tc], "")]

    # PDF: dò phần yêu cầu kỹ thuật theo dòng "Tiêu chí | Yêu cầu"
    import pdfplumber
    muc, mat_hang = [], ""
    with pdfplumber.open(duong_dan) as pdf:
        for trang in pdf.pages:
            for dong in (trang.extract_text() or "").splitlines():
                d = dong.strip()
                m = re.match(r"Mặt hàng\s*\d+\s*:\s*(.+)", d, re.IGNORECASE)
                if m:
                    mat_hang = m.group(1).strip()
                    continue
                if not mat_hang or len(d.split()) < 3:
                    continue
                if re.match(r"^(tiêu chí|phương pháp|phần)\b", d, re.IGNORECASE):
                    continue
                tu = d.split()
                for n in (1, 2):                    # tên tiêu chí 1-2 từ
                    ten = " ".join(tu[:n])
                    if khong_dau(ten) in ("cpu", "ram", "o cung", "man hinh",
                                          "xuat xu", "bao hanh", "pin", "chuan"):
                        muc.append({"mat_hang": mat_hang, "tieu_chi": ten,
                                    "yeu_cau": " ".join(tu[n:])})
                        break
    return muc


def doc_chao_ky_thuat(thu_muc: Path) -> dict[tuple[str, str], tuple[str, str]]:
    """Đọc thông số nhà thầu chào → {(mặt hàng chuẩn hoá, tiêu chí chuẩn hoá): (giá trị, nguồn)}."""
    import pdfplumber

    ra: dict[tuple[str, str], tuple[str, str]] = {}
    for tep in sorted(thu_muc.rglob("*.pdf")):
        with pdfplumber.open(tep) as pdf:
            mat_hang = ""
            for i, trang in enumerate(pdf.pages, 1):
                for dong in (trang.extract_text() or "").splitlines():
                    d = dong.strip()
                    m = re.match(r"Mặt hàng\s*\d+\s*:\s*(.+)", d, re.IGNORECASE)
                    if m:
                        mat_hang = m.group(1).strip()
                        continue
                    if not mat_hang:
                        continue
                    tu = d.split()
                    for n in (1, 2):
                        ten = " ".join(tu[:n])
                        if khong_dau(ten) in ("cpu", "ram", "o cung", "man hinh",
                                              "xuat xu", "bao hanh", "pin", "chuan"):
                            # Dòng có dạng: <tiêu chí> <yêu cầu HSMT> <giá trị chào>.
                            # Phần chào là vế cuối; tách bằng cách bỏ đi phần trùng yêu cầu
                            # thì mong manh, nên giữ nguyên cả vế và ghi rõ trong ghi chú.
                            ra[(khong_dau(mat_hang), khong_dau(ten))] = (
                                " ".join(tu[n:]), f"{tep.name} tr.{i}")
                            break
    return ra


def tach_phan_chao(ca_dong: str, yeu_cau: str) -> str:
    """Trong bảng 3 cột, dòng gộp lại là '<yêu cầu> <chào>'. Cắt bỏ phần yêu cầu ở đầu."""
    if not ca_dong:
        return ""
    a, b = ca_dong.strip(), (yeu_cau or "").strip()
    if b and a.lower().startswith(b.lower()):
        return a[len(b):].strip()
    # Không khớp tiền tố: trả nguyên vẹn, người xem tự đọc
    return a


def main() -> int:
    p = argparse.ArgumentParser(
        description="Lập phiếu đối chiếu kỹ thuật HSMT ↔ HSDT.",
        epilog="Script KHÔNG chấm đạt/không đạt — cột ket_luan để tổ chuyên gia điền.")
    p.add_argument("thu_muc", help="Thư mục HSDT (mỗi nhà thầu một thư mục con)")
    p.add_argument("--yeu-cau", help="File yêu cầu kỹ thuật (CSV/Excel)")
    p.add_argument("--hsmt", help="File HSMT (PDF) — thử dò yêu cầu kỹ thuật trong đó")
    p.add_argument("--ra", help="File Excel phiếu chấm")
    args = p.parse_args()

    can_thu_vien("pandas", "openpyxl", "pdfplumber")
    import pandas as pd

    nguon_yc = args.yeu_cau or args.hsmt
    if not nguon_yc:
        print("Cần --yeu-cau hoặc --hsmt", file=sys.stderr)
        return 2
    yeu_cau = doc_yeu_cau(Path(nguon_yc).expanduser())
    if not yeu_cau:
        print(f"Không đọc được yêu cầu kỹ thuật nào từ {nguon_yc}", file=sys.stderr)
        return 1

    goc = Path(args.thu_muc).expanduser()
    con = sorted(d for d in goc.iterdir() if d.is_dir()) or [goc]

    hang_list = []
    for d in con:
        chao = doc_chao_ky_thuat(d)
        for yc in yeu_cau:
            khoa = (khong_dau(yc["mat_hang"]), khong_dau(yc["tieu_chi"]))
            ca_dong, nguon = chao.get(khoa, (None, None))
            gt = tach_phan_chao(ca_dong, yc["yeu_cau"]) if ca_dong else None
            kq, ghi_chu = doi_chieu(yc["yeu_cau"], gt)
            hang_list.append({
                "nha_thau": d.name,
                "mat_hang": yc["mat_hang"],
                "tieu_chi": yc["tieu_chi"],
                "yeu_cau_hsmt": yc["yeu_cau"],
                "nha_thau_chao": gt,
                "nguon_trang": nguon,
                "doi_chieu_may": kq,
                "ghi_chu_may": ghi_chu,
                "ket_luan": "",                      # tổ chuyên gia điền
                "y_kien_to_chuyen_gia": "",
            })

    tom_tat_nt = {}
    for h in hang_list:
        t = tom_tat_nt.setdefault(h["nha_thau"], {"khop": 0, "thap_hon": 0,
                                                  "thieu_du_lieu": 0, "can_nguoi_xem": 0})
        t[h["doi_chieu_may"]] += 1

    if args.ra:
        ra = Path(args.ra).expanduser()
        ra.parent.mkdir(parents=True, exist_ok=True)
        with pd.ExcelWriter(ra, engine="openpyxl") as bo:
            # startrow=2 chừa dòng 1 cho lưu ý, dòng 2 trống; header rơi vào dòng 3.
            # Nhét lưu ý thành một "cột" của DataFrame thì nó tụt xuống DƯỚI header và nằm
            # ở cột không tên — người điền phiếu sẽ không đọc.
            pd.DataFrame(hang_list, columns=COT).to_excel(
                bo, sheet_name="Phieu cham ky thuat", index=False, startrow=2)
            pd.DataFrame([{"Nhà thầu": k, **v} for k, v in tom_tat_nt.items()]).to_excel(
                bo, sheet_name="Tom tat", index=False)
        _hoan_thien(ra, LUU_Y, len(COT))

    can_xem = sum(1 for h in hang_list if h["doi_chieu_may"] != "khop")
    if can_xem:
        canh_bao(f"{can_xem}/{len(hang_list)} tiêu chí cần tổ chuyên gia xem — "
                 "đọc cột doi_chieu_may và ghi_chu_may")
    canh_bao(LUU_Y)

    in_json({
        "tom_tat": {
            "so_nha_thau": len(con),
            "so_tieu_chi_moi_nha_thau": len(yeu_cau),
            "theo_nha_thau": tom_tat_nt,
            "luu_y": LUU_Y,
            "buoc_tiep": ("Tổ chuyên gia điền cột 'ket_luan' (Đạt/Không đạt), rồi nạp lại vào "
                          "so_sanh_thau.py bằng --ket-qua-ky-thuat để giới hạn nhóm vượt kỹ thuật."),
            "tep_ket_qua": str(Path(args.ra).expanduser()) if args.ra else None,
        },
        "chi_tiet": hang_list,
    })
    return 0


def _hoan_thien(tep: Path, luu_y: str, so_cot: int) -> None:
    """Đặt lưu ý lên dòng 1, thêm ô chọn Đạt/Không đạt, tô màu cột cần tổ chuyên gia điền."""
    import openpyxl
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation

    wb = openpyxl.load_workbook(tep)
    ws = wb["Phieu cham ky thuat"]

    ws["A1"] = luu_y
    ws["A1"].font = Font(bold=True, color="C8102E")
    ws["A1"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=so_cot)
    ws.row_dimensions[1].height = 46

    hdr = {str(o.value).strip(): o.column_letter for o in ws[3]}
    ws.freeze_panes = "A4"

    if "ket_luan" in hdr:
        cot = hdr["ket_luan"]
        dv = DataValidation(type="list", formula1='"Đạt,Không đạt,Cần làm rõ"', allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"{cot}4:{cot}{ws.max_row}")
        vang = PatternFill("solid", fgColor="FFF2CC")
        for ten in ("ket_luan", "y_kien_to_chuyen_gia"):
            if ten in hdr:
                for r in range(3, ws.max_row + 1):
                    ws[f"{hdr[ten]}{r}"].fill = vang

    rong = {"nha_thau": 34, "mat_hang": 32, "tieu_chi": 12, "yeu_cau_hsmt": 30,
            "nha_thau_chao": 24, "nguon_trang": 20, "doi_chieu_may": 16,
            "ghi_chu_may": 46, "ket_luan": 14, "y_kien_to_chuyen_gia": 28}
    for ten, w in rong.items():
        if ten in hdr:
            ws.column_dimensions[hdr[ten]].width = w
    for c in range(1, so_cot + 1):
        ws.cell(3, c).font = Font(bold=True)
    _ = get_column_letter
    wb.save(tep)


if __name__ == "__main__":
    sys.exit(main())
