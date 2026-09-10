#!/usr/bin/env python3
"""Sinh dữ liệu mẫu cho evals của skill ke-toan-vn.

Chạy:  python3 tao_fixtures.py
Cần: reportlab (cho PDF). Không có reportlab thì phần XML/CSV vẫn sinh được.
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

GOC = Path(__file__).resolve().parent / "fixtures"

# --- Eval 1: hóa đơn ---------------------------------------------------------
# 5 XML + 2 PDF. Bẫy cài sẵn:
#   - HD003: MST bên bán sai chữ số kiểm tra (0100686200 thay vì ...209)
#   - HD004: thuế suất 8% (hợp lệ, do các đợt giảm thuế GTGT — không phải lỗi)
#   - HD005: hàng không chịu thuế (KCT) — KHÁC với thuế suất 0%
HOA_DON = [
    dict(kh="C26TAA", so="00000101", ngay="2026-07-03", mst_ban="0100109106",
         ten_ban="Công ty Cổ phần Thương mại Bình Minh",
         hang=[("Giấy A4 Double A 70gsm", "Ram", 50, 65000)], ts=10),
    dict(kh="C26TAA", so="00000102", ngay="2026-07-11", mst_ban="0101243150",
         ten_ban="Công ty TNHH Thiết bị Văn phòng Hà Nội",
         hang=[("Mực in Canon 337", "Hộp", 12, 1250000),
               ("Giấy in nhiệt K80", "Cuộn", 40, 12000)], ts=10),
    dict(kh="C26TBB", so="00000103", ngay="2026-07-19", mst_ban="0100686200",
         ten_ban="Công ty Cổ phần Vận tải Sao Mai",
         hang=[("Cước vận chuyển tuyến HN-HP", "Chuyến", 8, 2400000)], ts=10),
    dict(kh="C26TAA", so="00000104", ngay="2026-08-02", mst_ban="0301446006",
         ten_ban="Công ty TNHH Dịch vụ Kỹ thuật Phương Nam",
         hang=[("Bảo trì hệ thống điều hòa", "Gói", 1, 18500000)], ts=8),
    dict(kh="C26TCC", so="00000105", ngay="2026-08-15", mst_ban="0100109106",
         ten_ban="Công ty Cổ phần Thương mại Bình Minh",
         hang=[("Phần mềm kế toán bản quyền 1 năm", "Bộ", 2, 9500000)], ts="KCT"),
]
PDF_HD = [
    dict(kh="C26TDD", so="00000106", ngay="2026-08-21", mst_ban="0101243150",
         ten_ban="Công ty TNHH Thiết bị Văn phòng Hà Nội",
         hang=[("Ghế xoay văn phòng GX-200", "Chiếc", 15, 1850000)], ts=10),
    dict(kh="C26TDD", so="00000107", ngay="2026-09-04", mst_ban="0301446006",
         ten_ban="Công ty TNHH Dịch vụ Kỹ thuật Phương Nam",
         hang=[("Thi công hệ thống mạng LAN", "Gói", 1, 42000000)], ts=10),
]
MUA = dict(mst="0106955987", ten="Công ty TNHH Đầu tư và Phát triển Việt Khang")


def tien(hd):
    hang = sum(sl * dg for _, _, sl, dg in hd["hang"])
    thue = 0 if not isinstance(hd["ts"], int) else round(hang * hd["ts"] / 100)
    return hang, thue, hang + thue


def sinh_xml(hd) -> str:
    hang, thue, tong = tien(hd)
    ts_txt = f"{hd['ts']}%" if isinstance(hd["ts"], int) else hd["ts"]
    dong = []
    for i, (ten, dvt, sl, dg) in enumerate(hd["hang"], 1):
        dong.append(f"""        <HHDVu>
          <STT>{i}</STT>
          <THHDVu>{ten}</THHDVu>
          <DVTinh>{dvt}</DVTinh>
          <SLuong>{sl}</SLuong>
          <DGia>{dg}</DGia>
          <ThTien>{sl * dg}</ThTien>
          <TSuat>{ts_txt}</TSuat>
        </HHDVu>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<HDon>
  <DLHDon Id="data">
    <TTChung>
      <PBan>2.0.0</PBan>
      <KHMSHDon>1</KHMSHDon>
      <KHHDon>{hd['kh']}</KHHDon>
      <SHDon>{hd['so']}</SHDon>
      <NLap>{hd['ngay']}</NLap>
      <DVTTe>VND</DVTTe>
      <TGia>1</TGia>
    </TTChung>
    <NDHDon>
      <NBan>
        <Ten>{hd['ten_ban']}</Ten>
        <MST>{hd['mst_ban']}</MST>
        <DChi>Số 12 phố Láng Hạ, Ba Đình, Hà Nội</DChi>
      </NBan>
      <NMua>
        <Ten>{MUA['ten']}</Ten>
        <MST>{MUA['mst']}</MST>
        <DChi>Tầng 5, toà nhà Sông Đà, Nam Từ Liêm, Hà Nội</DChi>
      </NMua>
      <DSHHDVu>
{chr(10).join(dong)}
      </DSHHDVu>
      <TToan>
        <THTTLTSuat>
          <LTSuat>
            <TSuat>{ts_txt}</TSuat>
            <ThTien>{hang}</ThTien>
            <TThue>{thue}</TThue>
          </LTSuat>
        </THTTLTSuat>
        <TgTCThue>{hang}</TgTCThue>
        <TgTThue>{thue}</TgTThue>
        <TgTTTBSo>{tong}</TgTTTBSo>
      </TToan>
    </NDHDon>
  </DLHDon>
  <DSCKS><NBan><Signature>...</Signature></NBan></DSCKS>
</HDon>
"""


def vnd(n):
    return f"{n:,.0f}".replace(",", ".")


def sinh_pdf(hd, ra: Path) -> bool:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError:
        return False

    font = "Helvetica"
    for thu in ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
                "/Library/Fonts/Arial Unicode.ttf",
                "/System/Library/Fonts/Supplemental/Times New Roman.ttf"):
        if Path(thu).exists():
            try:
                pdfmetrics.registerFont(TTFont("VN", thu))
                font = "VN"
                break
            except Exception:
                continue

    hang, thue, tong = tien(hd)
    c = canvas.Canvas(str(ra), pagesize=A4)
    w, h = A4
    y = h - 60
    c.setFont(font, 14)
    c.drawCentredString(w / 2, y, "HÓA ĐƠN GIÁ TRỊ GIA TĂNG")
    y -= 18
    c.setFont(font, 9)
    c.drawCentredString(w / 2, y, "(Bản thể hiện của hóa đơn điện tử)")
    y -= 30
    c.setFont(font, 10)
    for nhan, gt in [("Ký hiệu:", hd["kh"]), ("Số hóa đơn:", hd["so"]),
                     ("Ngày lập:", "/".join(reversed(hd["ngay"].split("-"))))]:
        c.drawString(60, y, f"{nhan} {gt}")
        y -= 16
    y -= 8
    c.drawString(60, y, f"Đơn vị bán hàng: {hd['ten_ban']}"); y -= 15
    c.drawString(60, y, f"Mã số thuế: {hd['mst_ban']}"); y -= 15
    c.drawString(60, y, "Địa chỉ: Số 12 phố Láng Hạ, Ba Đình, Hà Nội"); y -= 22
    c.drawString(60, y, f"Đơn vị mua hàng: {MUA['ten']}"); y -= 15
    c.drawString(60, y, f"Mã số thuế: {MUA['mst']}"); y -= 26

    c.setFont(font, 9)
    for x, t in ((60, "STT"), (90, "Tên hàng hóa, dịch vụ"), (300, "ĐVT"),
                 (350, "Số lượng"), (420, "Đơn giá"), (500, "Thành tiền")):
        c.drawString(x, y, t)
    y -= 4
    c.line(55, y, w - 55, y)
    y -= 14
    for i, (ten, dvt, sl, dg) in enumerate(hd["hang"], 1):
        c.drawString(60, y, str(i))
        c.drawString(90, y, ten[:40])
        c.drawString(300, y, dvt)
        c.drawRightString(400, y, str(sl))
        c.drawRightString(480, y, vnd(dg))
        c.drawRightString(555, y, vnd(sl * dg))
        y -= 15
    y -= 6
    c.line(55, y, w - 55, y)
    y -= 20
    c.setFont(font, 10)
    for nhan, gt in [("Cộng tiền hàng:", vnd(hang)),
                     (f"Thuế suất GTGT: {hd['ts']}%    Tiền thuế GTGT:", vnd(thue)),
                     ("Tổng cộng tiền thanh toán:", vnd(tong))]:
        c.drawString(300, y, nhan)
        c.drawRightString(555, y, gt)
        y -= 17
    c.save()
    return True


# --- Eval 2: đối chiếu -------------------------------------------------------
# Bảng kê bán ra vs sổ chi tiết TK 511. Ba sai lệch cài sẵn:
#   - HD00000205 có trong bảng kê nhưng THIẾU trong sổ
#   - HD00000207 LỆCH tiền: bảng kê 15.400.000, sổ 14.500.000
#   - HD00000209 bị ghi TRÙNG hai lần trong sổ
def sinh_doi_chieu():
    thu_muc = GOC / "doi-chieu"
    thu_muc.mkdir(parents=True, exist_ok=True)
    random.seed(20260910)

    ban_ra, so_511 = [], []
    for i in range(1, 13):
        so_hd = f"000002{i:02d}"
        mst = random.choice(["0100109106", "0101243150", "0301446006", "0106955982"])
        tien_hang = random.randrange(3, 40) * 500_000
        ban_ra.append({"ky_hieu": "C26TAA", "so_hd": so_hd, "ngay": f"2026-07-{i + 2:02d}",
                       "mst_mua": mst, "tien_hang": tien_hang,
                       "tien_thue": round(tien_hang * 0.1), "tong_cong": round(tien_hang * 1.1)})

    for r in ban_ra:
        if r["so_hd"] == "00000205":
            continue                                    # thiếu trong sổ
        ghi = dict(so_chung_tu=r["so_hd"], ngay=r["ngay"], tk_doi_ung="131",
                   dien_giai=f"Doanh thu bán hàng HĐ {r['so_hd']}", phat_sinh_co=r["tien_hang"])
        if r["so_hd"] == "00000207":
            ghi["phat_sinh_co"] = r["tien_hang"] - 900_000   # lệch tiền
        so_511.append(ghi)
        if r["so_hd"] == "00000209":
            so_511.append(dict(ghi))                    # ghi trùng

    with (thu_muc / "bang_ke_ban_ra.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(ban_ra[0]))
        w.writeheader()
        for r in ban_ra:
            r = dict(r)
            for k in ("tien_hang", "tien_thue", "tong_cong"):
                r[k] = vnd(r[k])
            r["ngay"] = "/".join(reversed(r["ngay"].split("-")))
            w.writerow(r)

    with (thu_muc / "so_chi_tiet_511.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(so_511[0]))
        w.writeheader()
        for r in so_511:
            r = dict(r)
            r["phat_sinh_co"] = vnd(r["phat_sinh_co"])
            r["ngay"] = "/".join(reversed(r["ngay"].split("-")))
            w.writerow(r)
    print(f"  ✅ doi-chieu: {len(ban_ra)} dòng bảng kê, {len(so_511)} dòng sổ")


# --- Eval 4: chấm thầu mua sắm hàng hóa --------------------------------------
# Gói thầu 8 mặt hàng. Bốn nhà thầu, mỗi bên một vấn đề cài sẵn:
#   A - chào THIẾU mặt hàng số 6 (Máy chiếu)
#   B - SAI SỐ HỌC dòng số 3: 25 × 4.200.000 = 105.000.000 nhưng ghi 102.500.000
#   C - có THƯ GIẢM GIÁ 3% (bẫy: phải trừ SAU khi sửa lỗi/hiệu chỉnh, không trừ trước)
#   D - BẢO ĐẢM DỰ THẦU hết hiệu lực 15/10/2026, sớm hơn yêu cầu 30/11/2026
DANH_MUC = [
    ("Máy tính để bàn Dell OptiPlex 7010", "Bộ", 30, 14_500_000),
    ("Màn hình LCD 24 inch", "Chiếc", 30, 3_200_000),
    ("Máy in laser đa chức năng", "Chiếc", 25, 4_200_000),
    ("Máy tính xách tay Dell Latitude 5450", "Chiếc", 12, 22_800_000),
    ("Bộ lưu điện UPS 1000VA", "Bộ", 20, 2_650_000),
    ("Máy chiếu Epson EB-X51", "Chiếc", 6, 11_900_000),
    ("Switch mạng 24 cổng Gigabit", "Chiếc", 8, 5_400_000),
    ("Ổ cứng di động 2TB", "Chiếc", 40, 1_750_000),
]
# Yêu cầu kỹ thuật trong HSMT, cho hai mặt hàng có thông số đáng chấm.
# Phương pháp: đạt/không đạt.
YEU_CAU_KT = {
    0: [("CPU", "Intel Core i5 thế hệ 12 trở lên"),
        ("RAM", "16 GB trở lên"),
        ("Ổ cứng", "SSD 512 GB trở lên"),
        ("Xuất xứ", "G7 hoặc EU"),
        ("Bảo hành", "36 tháng")],
    3: [("CPU", "Intel Core i5 thế hệ 13 trở lên"),
        ("RAM", "16 GB trở lên"),
        ("Màn hình", "14 inch Full HD"),
        ("Bảo hành", "24 tháng")],
}

# Bốn kiểu tình huống kỹ thuật, cố ý khác loại nhau:
#   A - đạt hết  (giữ nguyên để vẫn thử được luật đơn giá cao nhất cho phần chào thiếu)
#   B - THIẾU HẲN một tiêu chí (bảo hành laptop) → máy phát hiện được là thiếu dữ liệu
#   C - RAM 8GB < 16GB yêu cầu → sai lệch SỐ HỌC, máy đối chiếu được khách quan.
#       C cũng là bên có đơn giá cao nhất, nên loại C khỏi nhóm vượt kỹ thuật sẽ
#       LÀM ĐỔI giá trị hiệu chỉnh chào thiếu của A — đúng thứ cần chứng minh.
#   D - xuất xứ Trung Quốc vs yêu cầu "G7 hoặc EU" → khác loại, cần NGƯỜI đọc và quyết
KT_CHAO = {
    "A": {},
    "B": {(3, "Bảo hành"): None},
    "C": {(0, "RAM"): "8 GB"},
    "D": {(0, "Xuất xứ"): "Trung Quốc"},
}
KT_MAC_DINH = {
    (0, "CPU"): "Intel Core i5-12400", (0, "RAM"): "16 GB DDR4",
    (0, "Ổ cứng"): "SSD 512 GB NVMe", (0, "Xuất xứ"): "Đức",
    (0, "Bảo hành"): "36 tháng",
    (3, "CPU"): "Intel Core i5-1335U", (3, "RAM"): "16 GB",
    (3, "Màn hình"): "14 inch Full HD IPS", (3, "Bảo hành"): "24 tháng",
}

NHA_THAU = [
    dict(ma="A", ten="Nha thau A - Cong ty CP Tin hoc Minh Khai", mst="0100109106",
         he_so=1.00, thieu=[5], sai_so_hoc=None, giam_gia=0,
         bao_lanh_den="30/11/2026", doanh_thu=52_000_000_000),
    dict(ma="B", ten="Nha thau B - Cong ty TNHH Cong nghe Tan Phat", mst="0101243150",
         he_so=0.97, thieu=[], sai_so_hoc=(2, 102_500_000), giam_gia=0,
         bao_lanh_den="30/11/2026", doanh_thu=61_000_000_000),
    dict(ma="C", ten="Nha thau C - Cong ty CP Thiet bi Dong A", mst="0301446006",
         he_so=1.03, thieu=[], sai_so_hoc=None, giam_gia_pct=3,
         bao_lanh_den="30/11/2026", doanh_thu=48_500_000_000),
    dict(ma="D", ten="Nha thau D - Cong ty TNHH Giai phap Nam Long", mst="0100686209",
         he_so=0.99, thieu=[], sai_so_hoc=None, giam_gia=0,
         bao_lanh_den="15/10/2026", doanh_thu=44_000_000_000),
]


def _pdf_canvas(ra: Path):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    font = "Helvetica"
    for thu in ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
                "/Library/Fonts/Arial Unicode.ttf"):
        if Path(thu).exists():
            try:
                pdfmetrics.registerFont(TTFont("VN", thu))
                font = "VN"
                break
            except Exception:
                continue
    return canvas.Canvas(str(ra), pagesize=A4), A4, font


def sinh_hsmt(ra: Path) -> bool:
    try:
        c, (w, h), font = _pdf_canvas(ra)
    except ImportError:
        return False

    y = h - 60
    c.setFont(font, 13)
    c.drawCentredString(w / 2, y, "HỒ SƠ MỜI THẦU")
    y -= 18
    c.setFont(font, 10)
    c.drawCentredString(w / 2, y, "Gói thầu số 03: Mua sắm thiết bị tin học năm 2026")
    y -= 34

    c.setFont(font, 10)
    c.drawString(55, y, "Phần 1. Tiêu chuẩn đánh giá hồ sơ dự thầu"); y -= 18
    c.setFont(font, 9)
    for d in [
        "1.1. Đánh giá tính hợp lệ: đơn dự thầu hợp lệ; hiệu lực HSDT tối thiểu 90 ngày;",
        "     bảo đảm dự thầu 500.000.000 đồng, hiệu lực đến hết ngày 30/11/2026.",
        "1.2. Năng lực và kinh nghiệm: doanh thu bình quân 3 năm gần nhất tối thiểu",
        "     40.000.000.000 đồng; tối thiểu 02 hợp đồng tương tự.",
        "1.3. Đánh giá về kỹ thuật: theo phương pháp đạt/không đạt.",
        "1.4. Đánh giá về tài chính: phương pháp giá đánh giá. HSMT không quy định các yếu tố",
        "     quy về một mặt bằng, do đó ΔG = 0.",
    ]:
        c.drawString(55, y, d); y -= 13
    y -= 12

    c.setFont(font, 10)
    c.drawString(55, y, "Phần 2. Danh mục hàng hóa"); y -= 20
    c.setFont(font, 9)
    for x, t in ((55, "STT"), (85, "Tên hàng hóa"), (330, "ĐVT"), (380, "Số lượng")):
        c.drawString(x, y, t)
    y -= 4
    c.line(52, y, w - 52, y)
    y -= 14
    for i, (ten, dvt, sl, _) in enumerate(DANH_MUC, 1):
        c.drawString(58, y, str(i))
        c.drawString(85, y, ten)
        c.drawString(330, y, dvt)
        c.drawRightString(430, y, str(sl))
        y -= 15
    c.line(52, y + 4, w - 52, y + 4)

    c.showPage()
    y = h - 60
    c.setFont(font, 11)
    c.drawString(55, y, "Phần 3. Yêu cầu kỹ thuật"); y -= 16
    c.setFont(font, 9)
    c.drawString(55, y, "Phương pháp đánh giá: đạt/không đạt. Nhà thầu phải đáp ứng TẤT CẢ tiêu chí.")
    y -= 24
    for idx, tieu_chi in YEU_CAU_KT.items():
        c.setFont(font, 10)
        c.drawString(55, y, f"Mặt hàng {idx + 1}: {DANH_MUC[idx][0]}"); y -= 16
        c.setFont(font, 9)
        for x, t in ((70, "Tiêu chí"), (200, "Yêu cầu tối thiểu")):
            c.drawString(x, y, t)
        y -= 4
        c.line(66, y, w - 66, y)
        y -= 13
        for ten_tc, yc in tieu_chi:
            c.drawString(70, y, ten_tc)
            c.drawString(200, y, yc)
            y -= 13
        y -= 12
    c.save()
    return True


def sinh_hsdt(nt, thu_muc: Path) -> bool:
    try:
        thu_muc.mkdir(parents=True, exist_ok=True)
        c, (w, h), font = _pdf_canvas(thu_muc / "ho_so_du_thau.pdf")
    except ImportError:
        return False

    dong = []
    for i, (ten, dvt, sl, dg_goc) in enumerate(DANH_MUC):
        if i in nt["thieu"]:
            continue
        dg = round(dg_goc * nt["he_so"] / 1000) * 1000
        tt = sl * dg
        if nt.get("sai_so_hoc") and nt["sai_so_hoc"][0] == i:
            tt = nt["sai_so_hoc"][1]
        dong.append((ten, dvt, sl, dg, tt))
    gia_du_thau = sum(d[4] for d in dong)
    giam = round(gia_du_thau * nt.get("giam_gia_pct", 0) / 100) if nt.get("giam_gia_pct") else 0

    y = h - 55
    c.setFont(font, 13)
    c.drawCentredString(w / 2, y, "HỒ SƠ DỰ THẦU"); y -= 30
    c.setFont(font, 10)
    c.drawString(55, y, f"Nhà thầu: {nt['ten']}"); y -= 15
    c.drawString(55, y, f"Mã số thuế: {nt['mst']}"); y -= 15
    c.drawString(55, y, "Gói thầu số 03: Mua sắm thiết bị tin học năm 2026"); y -= 26

    c.setFont(font, 11)
    c.drawString(55, y, "ĐƠN DỰ THẦU"); y -= 18
    c.setFont(font, 10)
    c.drawString(55, y, f"Giá dự thầu: {vnd(gia_du_thau)} đồng"); y -= 15
    c.drawString(55, y, "Hiệu lực hồ sơ dự thầu: 90 ngày kể từ ngày đóng thầu"); y -= 15
    c.drawString(55, y, f"Bảo đảm dự thầu: 500.000.000 đồng, "
                        f"có hiệu lực đến ngày {nt['bao_lanh_den']}"); y -= 15
    if giam:
        c.drawString(55, y, f"Thư giảm giá: giảm {nt['giam_gia_pct']}% tương ứng "
                            f"giá trị giảm giá {vnd(giam)} đồng"); y -= 15
    c.drawString(55, y, f"Doanh thu bình quân 3 năm gần nhất: {vnd(nt['doanh_thu'])} đồng"); y -= 15
    c.drawString(55, y, "Số hợp đồng tương tự đã thực hiện: 03 hợp đồng"); y -= 28

    c.setFont(font, 11)
    c.drawString(55, y, "BẢNG GIÁ DỰ THẦU"); y -= 20
    c.setFont(font, 8)
    for x, t in ((55, "STT"), (82, "Tên hàng hóa"), (300, "ĐVT"),
                 (345, "Số lượng"), (410, "Đơn giá"), (495, "Thành tiền")):
        c.drawString(x, y, t)
    y -= 4
    c.line(52, y, w - 52, y)
    y -= 13
    for i, (ten, dvt, sl, dg, tt) in enumerate(dong, 1):
        c.drawString(58, y, str(i))
        c.drawString(82, y, ten[:44])
        c.drawString(300, y, dvt)
        c.drawRightString(395, y, str(sl))
        c.drawRightString(480, y, vnd(dg))
        c.drawRightString(558, y, vnd(tt))
        y -= 13
    c.line(52, y + 3, w - 52, y + 3)
    y -= 14
    c.setFont(font, 9)
    c.drawString(410, y, "Tổng cộng:")
    c.drawRightString(558, y, vnd(gia_du_thau))

    # Trang 2: bảng thông số kỹ thuật chào
    c.showPage()
    y = h - 60
    c.setFont(font, 11)
    c.drawString(55, y, "BẢNG THÔNG SỐ KỸ THUẬT CHÀO THẦU"); y -= 16
    c.setFont(font, 9)
    c.drawString(55, y, f"Nhà thầu: {nt['ten']}"); y -= 24

    chao = dict(KT_MAC_DINH)
    chao.update(KT_CHAO.get(nt["ma"], {}))
    for idx, tieu_chi in YEU_CAU_KT.items():
        c.setFont(font, 10)
        c.drawString(55, y, f"Mặt hàng {idx + 1}: {DANH_MUC[idx][0]}"); y -= 16
        c.setFont(font, 9)
        for x, t in ((70, "Tiêu chí"), (200, "Yêu cầu HSMT"), (370, "Nhà thầu chào")):
            c.drawString(x, y, t)
        y -= 4
        c.line(66, y, w - 66, y)
        y -= 13
        for ten_tc, yc in tieu_chi:
            gt = chao.get((idx, ten_tc))
            if gt is None:
                continue                      # cố ý bỏ trống — thiếu dữ liệu
            c.drawString(70, y, ten_tc)
            c.drawString(200, y, yc)
            c.drawString(370, y, gt)
            y -= 13
        y -= 12
    c.save()
    return True


def sinh_dau_thau():
    goc = GOC / "goi-thau"
    goc.mkdir(parents=True, exist_ok=True)

    with (goc / "danh_muc_hsmt.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["stt", "ten_hang_hoa", "dvt", "so_luong"])
        for i, (ten, dvt, sl, _) in enumerate(DANH_MUC, 1):
            w.writerow([i, ten, dvt, sl])

    with (goc / "yeu_cau_ky_thuat.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["ten_hang_hoa", "tieu_chi", "yeu_cau"])
        for idx, tc in YEU_CAU_KT.items():
            for ten_tc, yc in tc:
                w.writerow([DANH_MUC[idx][0], ten_tc, yc])

    if not sinh_hsmt(goc / "hsmt.pdf"):
        print("  ⚠️  Chưa cài reportlab — bỏ qua HSMT/HSDT dạng PDF")
        return
    n = sum(sinh_hsdt(nt, goc / "hsdt" / nt["ten"]) for nt in NHA_THAU)
    print(f"  ✅ goi-thau: HSMT + {n} bộ HSDT, danh mục {len(DANH_MUC)} mặt hàng")


def main():
    print("Sinh dữ liệu mẫu...")

    hd_dir = GOC / "hoa-don"
    hd_dir.mkdir(parents=True, exist_ok=True)
    for hd in HOA_DON:
        (hd_dir / f"HD{hd['so']}.xml").write_text(sinh_xml(hd), encoding="utf-8")
    print(f"  ✅ hoa-don: {len(HOA_DON)} file XML")

    thanh_cong = sum(sinh_pdf(hd, hd_dir / f"HD{hd['so']}.pdf") for hd in PDF_HD)
    if thanh_cong:
        print(f"  ✅ hoa-don: {thanh_cong} file PDF")
    else:
        print("  ⚠️  Chưa cài reportlab — bỏ qua phần PDF")

    sinh_doi_chieu()
    sinh_dau_thau()
    print(f"\nXong. Dữ liệu ở: {GOC}")


if __name__ == "__main__":
    main()
