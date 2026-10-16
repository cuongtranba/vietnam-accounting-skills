#!/usr/bin/env python3
"""Kiểm thử các kiểm soát: chế độ áp dụng theo ngày, xác thực hóa đơn, cổng đầy đủ, bố cục,
hồ sơ lần chạy, phê duyệt, cô lập đơn vị, bất biến kế toán, đầu vào không tin cậy.

    python evals/kiem_soat.py

Bổ sung cho evals/kiem_thu.py (so con số đã biết): ở đây mỗi phép kiểm gắn với một mã kịch bản
(ACC-001, INV-003, WF-001...) trong docs/audit/CONTROL-MATRIX.md, và kiểm một LỜI HỨA của
công cụ — không phải một con số trong file mẫu. Mọi dữ liệu là dữ liệu tổng hợp, sinh ngay tại
chỗ trong thư mục tạm; bộ nhớ (KE_TOAN_VN_HOME) cũng nằm trong thư mục tạm.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
SCRIPTS = GOC / "skills" / "ke-toan-vn" / "scripts"
FIX = GOC / "evals" / "fixtures"
PY = sys.executable
TMP = Path(tempfile.mkdtemp(prefix="kt-kiem-soat-"))
HOME = TMP / "bo-nho"
MOI_TRUONG = {**os.environ, "KE_TOAN_VN_HOME": str(HOME)}
MOI_TRUONG.pop("KE_TOAN_VN_DON_VI", None)

loi: list[str] = []


def chay(*lenh: str, env: dict | None = None) -> tuple[int, dict]:
    """Chạy một script; mã thoát là một phần của kết quả cần kiểm, stdout phải là JSON."""
    kq = subprocess.run([PY, *lenh], capture_output=True, text=True, env=env or MOI_TRUONG)
    try:
        return kq.returncode, json.loads(kq.stdout)
    except json.JSONDecodeError:
        return kq.returncode, {"_stdout": kq.stdout[-1500:], "_stderr": kq.stderr[-1500:]}


def kiem(ten: str, thuc_te, mong_doi) -> None:
    if thuc_te == mong_doi:
        print(f"  ✅ {ten}")
    else:
        print(f"  ❌ {ten}: được {thuc_te!r}, mong đợi {mong_doi!r}")
        loi.append(ten)


def luu_bang(ra: Path, tieu_de: list, dong: list) -> Path:
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.worksheets[0]
    for r in [tieu_de] + dong:
        ws.append(r)
    ra.parent.mkdir(parents=True, exist_ok=True)
    wb.save(ra)
    return ra


# --- G01 -----------------------------------------------------------------------------------
print("[G01] Chế độ kế toán theo loại đơn vị và ngày BẮT ĐẦU năm tài chính")
CD = str(SCRIPTS / "che_do_ke_toan.py")

ma, d = chay(CD, "--loai-don-vi", "doanh-nghiep", "--dau-nam-tai-chinh", "2026-01-01")
kiem("[ACC-001] DN năm dương lịch 2026 → TT 99/2025, dẫn Điều 31 và nguồn Công báo",
     (ma, d.get("trang_thai"), (d.get("che_do") or {}).get("id"),
      any("Điều 31" in c["dieu_khoan"] and "congbao" in c["nguon"]
          for c in d.get("trich_dan", []))),
     (0, "xac_dinh", "TT99/2025", True))

ma, d = chay(CD, "--loai-don-vi", "doanh-nghiep", "--dau-nam-tai-chinh", "2025-10-01")
kiem("[ACC-002] năm tài chính 01/10/2025–30/09/2026 giữ TT 200 cả năm, không đổi giữa năm",
     ((d.get("che_do") or {}).get("id"), d.get("nam_tai_chinh", {}).get("ket_thuc"),
      any("2026-10-01" in x for x in d.get("ly_do", []))),
     ("TT200/2014", "2026-09-30", True))

ma, d = chay(CD, "--ngay", "2026-03-15", "--thang-dau-nam", "10", "--loai-don-vi", "doanh-nghiep")
kiem("[ACC-002] suy năm tài chính từ ngày giao dịch + tháng đầu năm (15/3/2026, tháng 10)",
     (d.get("nam_tai_chinh", {}).get("bat_dau"), (d.get("che_do") or {}).get("id")),
     ("2025-10-01", "TT200/2014"))

ma, d = chay(CD, "--loai-don-vi", "sieu-nho", "--dau-nam-tai-chinh", "2026-07-01")
ma2, d2 = chay(CD, "--loai-don-vi", "sieu-nho", "--dau-nam-tai-chinh", "2026-04-01")
kiem("[ACC-003] DN siêu nhỏ: năm bắt đầu 01/7/2026 → TT 58/2026; năm bắt đầu 01/4/2026 → giữ "
     "TT 132/2018 cả năm, TT 58 từ năm sau (suy theo hỏi đáp Cục QLKT về TT 99 và khoản 3 Điều 4 "
     "TT 58), có ghi rõ là suy luận cần người duyệt",
     ((d.get("che_do") or {}).get("id"), ma2, d2.get("trang_thai"),
      (d2.get("che_do") or {}).get("id"), d2.get("co_so"),
      any("159102" in c.get("nguon", "") for c in d2.get("trich_dan", []))),
     ("TT58/2026", 0, "xac_dinh", "TT132/2018", "suy_luan_tuong_tu", True))

ma, d = chay(CD, "--loai-don-vi", "su-nghiep-cong-lap", "--tu-chu", "chi-thuong-xuyen",
             "--dau-nam-tai-chinh", "2026-01-01")
ma2, d2 = chay(CD, "--loai-don-vi", "doanh-nghiep", "--dau-nam-tai-chinh", "2026-01-01")
ma3, d3 = chay(CD, "--loai-don-vi", "su-nghiep-cong-lap", "--dau-nam-tai-chinh", "2026-01-01")
kiem("[ACC-004] bệnh viện công (ĐVSNCL tự chủ chi thường xuyên) → TT 24/2024; bệnh viện tư "
     "(doanh nghiệp) → TT 99/2025; ĐVSNCL chưa rõ mức tự chủ → cần xác nhận",
     ((d.get("che_do") or {}).get("id"), (d2.get("che_do") or {}).get("id"), ma3,
      d3.get("trang_thai")),
     ("TT24/2024", "TT99/2025", 2, "can_xac_nhan"))

ma, d = chay(CD, "--loai-don-vi", "su-nghiep-cong-lap", "--tu-chu", "chi-thuong-xuyen-va-dau-tu",
             "--duoc-phep-ap-dung-che-do-dn", "co", "--dau-nam-tai-chinh", "2026-01-01")
kiem("[ACC-004] ĐVSNCL tự bảo đảm chi thường xuyên và chi đầu tư, được phép → chế độ DN (TT 99), "
     "kèm nhắc báo cáo quyết toán kinh phí",
     ((d.get("che_do") or {}).get("id"), any("Phụ lục III" in x for x in d.get("ly_do", []))),
     ("TT99/2025", True))

ma, d = chay(CD, "--loai-don-vi", "khac", "--dau-nam-tai-chinh", "2026-01-01")
ma2, d2 = chay(CD, "--dau-nam-tai-chinh", "2026-01-01")
kiem("loại đơn vị khác/không khai → cần xác nhận, KHÔNG rơi về TT 200",
     (ma, d.get("che_do"), ma2, d2.get("che_do"), "TT200" in json.dumps(d2.get("che_do"))),
     (2, None, 2, None, False))

ma, d = chay(CD, "--loai-don-vi", "doanh-nghiep", "--dau-nam-tai-chinh", "2024-01-01")
kiem("năm tài chính 2024 vẫn TT 200 — số liệu lịch sử không bị diễn giải lại theo TT 99",
     (d.get("che_do") or {}).get("id"), "TT200/2014")

ma, d = chay(CD, "--loai-don-vi", "dnnvv", "--dau-nam-tai-chinh", "2026-01-01")
ma2, d2 = chay(CD, "--loai-don-vi", "dnnvv", "--dau-nam-tai-chinh", "2026-01-01",
               "--da-chon", "TT133")
kiem("DNNVV chưa khai chế độ đã chọn → cần xác nhận giữa TT 133 và TT 99; đã chọn TT 133 → TT 133",
     (ma, sorted(u["id"] for u in d.get("ung_vien", [])), (d2.get("che_do") or {}).get("id")),
     (2, ["TT133/2016", "TT99/2025"], "TT133/2016"))

ma, d = chay(CD, "--hoa-don-ngay", "2026-06-30")
ma2, d2 = chay(CD, "--hoa-don-ngay", "2026-07-01")
kiem("hóa đơn lập 30/6/2026 theo NĐ 123/2020 (căn cứ khoản 2 Điều 24 TT 91/2026); lập 01/7/2026 "
     "theo NĐ 254/2026",
     ((d.get("che_do_hoa_don") or {}).get("id"), (d2.get("che_do_hoa_don") or {}).get("id"),
      any(c["id"] == "TT91-D24" for c in (d.get("che_do_hoa_don") or {}).get("trich_dan", []))),
     ("ND123/2020", "ND254/2026", True))

# --- G02 -----------------------------------------------------------------------------------
print("\n[G02/G08] Ghi chú pháp lý theo ngày hiệu lực, hồi tố, nhiều phiên bản cùng ngày")
BN = str(SCRIPTS / "bo_nho.py")


def ghi(*a: str) -> tuple[int, dict]:
    return chay(BN, "ghi", "--loai", "phap-ly", *a)


ghi("--chu-de", "Nguong doanh thu ho kinh doanh", "--van-ban", "NĐ 68/2026/NĐ-CP",
    "--hieu-luc-tu", "2026-01-01", "--ngay-ban-hanh", "2026-03-05",
    "--nguon", "https://vanban.chinhphu.vn/a", "--noi-dung", "Ngưỡng 500 triệu đồng/năm.")
ghi("--chu-de", "Nguong doanh thu ho kinh doanh", "--van-ban", "NĐ 141/2026/NĐ-CP",
    "--sua-doi", "NĐ 68/2026/NĐ-CP", "--hieu-luc-tu", "2026-01-01",
    "--ngay-ban-hanh", "2026-04-29", "--nguon", "https://chinhphu.vn/b",
    "--noi-dung", "Ngưỡng 1 tỷ đồng/năm.")
ma, d = chay(BN, "tra", "nguong doanh thu ho kinh doanh", "--ngay", "2026-02-01")
ap = d.get("ap_dung") or {}
kiem("[ACC-005] tra theo ngày 01/02/2026: áp dụng NĐ 141/2026 (hồi tố từ 01/01/2026, ban hành "
     "29/4/2026), cảnh báo quyết định lập trước ngày ban hành cần rà soát",
     ("1 tỷ" in ap.get("noi_dung", ""), ap.get("hoi_to"),
      any("hồi tố" in c for c in d.get("canh_bao", []))),
     (True, True, True))
kiem("[ACC-005] bản NĐ 68/2026 vẫn truy được làm nguồn gốc lịch sử, không phải bản áp dụng",
     [g.get("van_ban") for g in d.get("lich_su", [])], [["NĐ 68/2026/NĐ-CP"]])

ghi("--chu-de", "Thue suat mau", "--hieu-luc-tu", "2025-01-01", "--nguon",
    "https://vanban.chinhphu.vn/c", "--noi-dung", "Mức cũ 8%.")
ghi("--chu-de", "Thue suat mau", "--hieu-luc-tu", "2026-01-01", "--nguon",
    "https://vanban.chinhphu.vn/d", "--noi-dung", "Mức mới 10%.")
_, d25 = chay(BN, "tra", "thue suat mau", "--ngay", "2025-06-30")
_, d26 = chay(BN, "tra", "thue suat mau", "--ngay", "2026-06-30")
kiem("năm thuế cũ lấy bản cũ (đã lưu trữ), năm mới lấy bản mới",
     ("8%" in (d25.get("ap_dung") or {}).get("noi_dung", ""),
      (d25.get("ap_dung") or {}).get("ban_luu_tru"),
      "10%" in (d26.get("ap_dung") or {}).get("noi_dung", "")),
     (True, True, True))

ghi("--chu-de", "Quy dinh tuong lai", "--hieu-luc-tu", "2026-07-01", "--nguon",
    "https://vanban.chinhphu.vn/e", "--noi-dung", "Áp dụng từ 01/7/2026.")
_, d = chay(BN, "tra", "quy dinh tuong lai", "--ngay", "2026-03-01")
kiem("ghi chú còn hạn nhưng CHƯA hiệu lực tại ngày tra → không dùng, phải tra lại",
     (d.get("ap_dung"), d.get("can_tra_web")), (None, True))

ghi("--chu-de", "Khong ro hieu luc", "--nguon", "https://vanban.chinhphu.vn/f",
    "--noi-dung", "Không ghi ngày hiệu lực.")
_, d = chay(BN, "tra", "khong ro hieu luc", "--ngay", "2026-03-01")
kiem("ghi chú không có ngày hiệu lực → không coi là áp dụng được cho một ngày cụ thể",
     (d.get("ap_dung"), d.get("can_tra_web")), (None, True))

for i in range(3):
    ghi("--chu-de", "Cung ngay", "--hieu-luc-tu", "2026-01-01", "--nguon",
        "https://vanban.chinhphu.vn/g", "--noi-dung", f"Phiên bản {i + 1}.")
_, d = chay(BN, "lich-su", "cung ngay")
kiem("[AUD-003] ghi 3 lần cùng một ngày: cả 3 phiên bản còn đọc được, không bản nào bị đè",
     sorted(x["noi_dung"].strip() for x in d.get("phien_ban", [])),
     ["Phiên bản 1.", "Phiên bản 2.", "Phiên bản 3."])

ma, _ = ghi("--chu-de", "Nguon sai", "--nguon", "khong-phai-url", "--noi-dung", "x")
kiem("nguồn không phải URL https bị từ chối", ma != 0, True)
ma, d = ghi("--chu-de", "Nguon blog", "--nguon", "https://blog.example.com/x",
            "--do-tin-cay", "cao", "--noi-dung", "x")
_, t = chay(BN, "tra", "nguon blog")
kiem("độ tin cậy 'cao' mà không có nguồn .gov.vn bị hạ xuống trung_binh",
     (t.get("ghi_chu") or [{}])[0].get("do_tin_cay"), "trung_binh")

# --- G03 / G04 -----------------------------------------------------------------------------
print("\n[G03/G04] Hóa đơn: phân tích ≠ xác thực; cổng đầy đủ trước khi cộng tổng")
DH = str(SCRIPTS / "doc_hoa_don.py")


def hdon(so: str, tien: int | None = 1_000_000, thue: int | None = 100_000, ngay="2026-07-03",
         mst="0100109106", kh="C26TAA", them="") -> str:
    tg = "" if tien is None else f"<TgTCThue>{tien}</TgTCThue>"
    tt = "" if thue is None else f"<TgTThue>{thue}</TgTThue>"
    tong = (tien or 0) + (thue or 0)
    return (f'<HDon><DLHDon Id="d{so}"><TTChung><KHHDon>{kh}</KHHDon><SHDon>{so}</SHDon>'
            f"<NLap>{ngay}</NLap></TTChung><NDHDon><NBan><Ten>Cong ty mau</Ten>"
            f"<MST>{mst}</MST></NBan><NMua><Ten>Benh vien mau</Ten><MST>0106955987</MST></NMua>"
            f"<TToan><THTTLTSuat><LTSuat><TSuat>10%</TSuat></LTSuat></THTTLTSuat>{tg}{tt}"
            f"<TgTTTBSo>{tong}</TgTTTBSo></TToan>{them}</NDHDon></DLHDon></HDon>")


def thu_muc(ten: str, tep: dict) -> Path:
    d = TMP / "hd" / ten
    d.mkdir(parents=True, exist_ok=True)
    for k, v in tep.items():
        (d / k).write_bytes(v if isinstance(v, bytes) else v.encode("utf-8"))
    return d


d_boc = thu_muc("boc", {"tdiep.xml": "<TDiep><DLieu>" + hdon("00000001", 1_000_000, 100_000)
                        + hdon("00000002", 2_000_000, 200_000) + "</DLieu></TDiep>"})
ma, d = chay(DH, str(d_boc))
kiem("[INV-005] một thông điệp có 2 hóa đơn → 2 dòng, mỗi dòng đúng số và tiền của nó",
     sorted((h["so_hd"], str(h["tien_hang"])) for h in d.get("chi_tiet", [])),
     [("00000001", "1000000"), ("00000002", "2000000")])

d_trung_the = thu_muc("trung-the", {"a.xml": hdon(
    "00000003", them="<TTKhac><TgTCThue>9999</TgTCThue></TTKhac>")})
_, d = chay(DH, str(d_trung_the))
h = (d.get("chi_tiet") or [{}])[0]
kiem("thẻ tiền lặp với giá trị khác nhau → không tự chọn thẻ đầu, để trống và cảnh báo",
     (h.get("tien_hang"), "nhiều giá trị" in (h.get("canh_bao") or "")), (None, True))

d_ns = thu_muc("ns", {"a.xml": hdon("00000004").replace(
    "<HDon>", '<HDon xmlns="http://example.invalid/hoadon">', 1)})
_, d = chay(DH, str(d_ns))
kiem("XML có namespace mặc định vẫn đọc đúng", (d.get("chi_tiet") or [{}])[0].get("so_hd"),
     "00000004")

d_hong = thu_muc("hong", {"a.xml": "<HDon><DLHDon>"})
_, d = chay(DH, str(d_hong))
h = (d.get("chi_tiet") or [{}])[0]
kiem("XML hỏng → xml_schema=fail, cả lô needs_review",
     ((h.get("xac_thuc") or {}).get("xml_schema"), d.get("tom_tat", {}).get("trang_thai")),
     ("fail", "needs_review"))

d3 = thu_muc("ba", {"1.xml": hdon("00000011", 1_000_000, 100_000),
                    "2.xml": hdon("00000012", None, 50_000),
                    "3.xml": hdon("00000013", 3_000_000, 300_000)})
ma, d = chay(DH, str(d3))
t = d.get("tom_tat", {})
kiem("[INV-003] 3 hóa đơn, 1 thiếu tiền hàng: tổng quan sát 4.000.000 ghi rõ là chưa đủ, "
     "tổng đã kiểm để trống, trạng thái needs_review",
     (str(t.get("tong_tien_hang")), t.get("tong_da_kiem"), t.get("kiem_soat", {}).get(
         "du_lieu_day_du"), t.get("trang_thai")),
     ("4000000", None, False, "needs_review"))
ma, _ = chay(DH, str(d3), "--yeu-cau-day-du")
kiem("[INV-003] --yeu-cau-day-du: thiếu dữ liệu thì mã thoát 2 cho bên gọi chặn lại", ma, 2)

d_dup = thu_muc("dup", {"1.xml": hdon("00000021"), "2.xml": hdon("00000021"),
                        "3.xml": hdon("00000022", 500_000, 50_000)})
_, d = chay(DH, str(d_dup))
t = d.get("tom_tat", {})
kiem("[INV-004] 2 hóa đơn trùng người bán/ký hiệu/số: báo trùng, tổng chỉ cộng một lần",
     (len(t.get("hoa_don_trung", [])), str(t.get("tong_tien_hang")), t.get("trang_thai")),
     (1, "1500000", "needs_review"))

d_dc = thu_muc("dieu-chinh", {"1.xml": hdon("00000031", -200_000, -20_000),
                              "2.xml": hdon("00000032", 0, 0)})
_, d = chay(DH, str(d_dc))
theo_so = {h["so_hd"]: h for h in d.get("chi_tiet", [])}
kiem("hóa đơn điều chỉnh giảm (số âm) và hóa đơn 0 đồng không bị coi là thiếu tiền",
     (str(theo_so.get("00000031", {}).get("tien_hang")),
      str(theo_so.get("00000032", {}).get("tien_hang")),
      d.get("tom_tat", {}).get("kiem_soat", {}).get("so_dong_thieu_tien")),
     ("-200000", "0", 0))

d_kn = thu_muc("ky-ngay", {"1.xml": hdon("00000041", ngay="2026-06-15"),
                           "2.xml": hdon("00000042", ngay="2026-07-03")})
_, d = chay(DH, str(d_kn))
theo_so = {h["so_hd"]: h for h in d.get("chi_tiet", [])}
kiem("chế độ hóa đơn theo NGÀY LẬP từng hóa đơn (6/2026 → NĐ 123/2020, 7/2026 → NĐ 254/2026)",
     (theo_so.get("00000041", {}).get("che_do_hoa_don"),
      theo_so.get("00000042", {}).get("che_do_hoa_don")),
     ("ND123/2020", "ND254/2026"))

_, d = chay(DH, str(d3))
kiem("trạng thái tra cứu cơ quan thuế luôn not_checked — công cụ không có kết nối được cấp phép",
     {(h.get("xac_thuc") or {}).get("trang_thai_cqt") for h in d.get("chi_tiet", [])},
     {"not_checked"})
kiem("hóa đơn không có chữ ký số → signature=absent",
     {(h.get("xac_thuc") or {}).get("chu_ky") for h in d.get("chi_tiet", [])}, {"absent"})

pdf_mau = FIX / "hoa-don" / "HD00000106.pdf"
if pdf_mau.exists():
    d_pdf = thu_muc("pdf", {"HD00000106.pdf": pdf_mau.read_bytes()})
    _, d = chay(DH, str(d_pdf))
    h = (d.get("chi_tiet") or [{}])[0]
    x = h.get("xac_thuc") or {}
    kiem("[INV-002] chỉ có PDF: đọc ra bản nháp, không giả vờ đã kiểm XML/chữ ký",
         (h.get("nguon"), x.get("xml_schema"), x.get("chu_ky"), x.get("trang_thai_cqt")),
         ("PDF", "unsupported", "not_checked", "not_checked"))
    d_lech = thu_muc("xml-pdf-lech", {"X.pdf": pdf_mau.read_bytes(),
                                      "X.xml": hdon("00000106", 1_000_000, 100_000)})
    _, d = chay(DH, str(d_lech))
    h = (d.get("chi_tiet") or [{}])[0]
    kiem("XML và PDF cùng tên lệch tổng tiền → cảnh báo, needs_review",
         ("PDF" in (h.get("canh_bao") or "") and "khác" in (h.get("canh_bao") or ""),
          d.get("tom_tat", {}).get("trang_thai")),
         (True, "needs_review"))
else:
    kiem("[INV-002] cần evals/fixtures (chạy evals/tao_fixtures.py trước)", False, True)

# Chữ ký số: sinh chứng thư và ký ngay tại chỗ (tổng hợp, không dùng khoá thật nào)
try:
    import signxml  # noqa: F401
    from cryptography import x509
    CO_SIGNXML = True
except ImportError:
    CO_SIGNXML = False

if CO_SIGNXML:
    import datetime as _dt

    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
    from lxml import etree
    from signxml import XMLSigner, methods

    BAY_GIO = _dt.datetime.now(_dt.timezone.utc)

    def _chung_thu(ten, khoa, ca=None, ca_khoa=None, la_ca=False):
        ten_x = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, ten)])
        b = (x509.CertificateBuilder().subject_name(ten_x)
             .issuer_name(ca.subject if ca else ten_x).public_key(khoa.public_key())
             .serial_number(x509.random_serial_number())
             .not_valid_before(BAY_GIO - _dt.timedelta(days=1))
             .not_valid_after(BAY_GIO + _dt.timedelta(days=365))
             .add_extension(x509.BasicConstraints(ca=la_ca, path_length=None), critical=True)
             .add_extension(x509.KeyUsage(
                 digital_signature=not la_ca, content_commitment=not la_ca,
                 key_encipherment=False, data_encipherment=False, key_agreement=False,
                 key_cert_sign=la_ca, crl_sign=la_ca, encipher_only=False,
                 decipher_only=False), critical=True)
             .add_extension(x509.SubjectKeyIdentifier.from_public_key(khoa.public_key()),
                            critical=False))
        if ca is not None:
            b = b.add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(
                ca_khoa.public_key()), critical=False)
            b = b.add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]),
                                critical=False)
        return b.sign(ca_khoa or khoa, hashes.SHA256())

    ca_khoa = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca = _chung_thu("CA mau tong hop", ca_khoa, la_ca=True)
    nb_khoa = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nb = _chung_thu("Nguoi ban mau", nb_khoa, ca, ca_khoa)
    la_khoa = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    la = _chung_thu("Nguoi la", la_khoa, ca, ca_khoa)
    (TMP / "ca.pem").write_bytes(ca.public_bytes(serialization.Encoding.PEM))

    def ky(xml: str, khoa=nb_khoa, cert=nb) -> bytes:
        goc = etree.fromstring(xml.encode())
        dl = goc.find("DLHDon")
        chu_ky = XMLSigner(method=methods.detached, signature_algorithm="rsa-sha256",
                           digest_algorithm="sha256").sign(
            goc, key=khoa, cert=[cert], reference_uri="#" + dl.get("Id"))
        dscks = etree.SubElement(goc, "DSCKS")
        etree.SubElement(dscks, "NBan").append(chu_ky)
        return etree.tostring(goc, xml_declaration=True, encoding="UTF-8")

    da_ky = ky(hdon("00000051"))
    d_ky = thu_muc("ky", {"a.xml": da_ky})
    _, d = chay(DH, str(d_ky))
    h = (d.get("chi_tiet") or [{}])[0]
    x = h.get("xac_thuc") or {}
    kiem("chữ ký toàn vẹn nhưng chưa có chuỗi tin cậy → signature=not_checked (không nói valid), "
         "lô ở trạng thái draft",
         (x.get("chu_ky"), x.get("toan_ven_chu_ky"), d.get("tom_tat", {}).get("trang_thai")),
         ("not_checked", "valid", "draft"))
    _, d = chay(DH, str(d_ky), "--ca-tin-cay", str(TMP / "ca.pem"))
    x = ((d.get("chi_tiet") or [{}])[0]).get("xac_thuc") or {}
    kiem("chữ ký toàn vẹn + chứng thư chuỗi về CA tin cậy được cung cấp → signature=valid",
         x.get("chu_ky"), "valid")

    sua = da_ky.replace(b"<TgTCThue>1000000<", b"<TgTCThue>1000001<")
    d_sua = thu_muc("ky-sua", {"a.xml": sua})
    _, d = chay(DH, str(d_sua), "--ca-tin-cay", str(TMP / "ca.pem"))
    x = ((d.get("chi_tiet") or [{}])[0]).get("xac_thuc") or {}
    kiem("[INV-001] XML đã ký bị sửa 1 byte → signature=invalid, needs_review",
         (x.get("chu_ky"), d.get("tom_tat", {}).get("trang_thai")), ("invalid", "needs_review"))

    goc = etree.fromstring(da_ky)
    the_cert = goc.find(".//{http://www.w3.org/2000/09/xmldsig#}X509Certificate")
    import base64

    the_cert.text = base64.b64encode(la.public_bytes(serialization.Encoding.DER)).decode()
    d_cert = thu_muc("ky-cert-la", {"a.xml": etree.tostring(goc)})
    _, d = chay(DH, str(d_cert))
    x = ((d.get("chi_tiet") or [{}])[0]).get("xac_thuc") or {}
    kiem("chứng thư trong chữ ký không khớp khoá đã ký → signature=invalid", x.get("chu_ky"),
         "invalid")
else:
    _, d = chay(DH, str(thu_muc("ky-khong-thu-vien", {"a.xml": hdon("00000051").replace(
        "</HDon>", '<DSCKS><NBan><Signature xmlns="http://www.w3.org/2000/09/xmldsig#"/>'
        "</NBan></DSCKS></HDon>")})))
    x = ((d.get("chi_tiet") or [{}])[0]).get("xac_thuc") or {}
    kiem("thiếu thư viện kiểm chữ ký → signature=not_checked, không bao giờ valid",
         x.get("chu_ky"), "not_checked")

# --- G05 -----------------------------------------------------------------------------------
print("\n[G05] Kiểm tra bố cục TRƯỚC khi ghi; ghi nguyên tử; không ghi gì khi phải hỏi")
QT = str(SCRIPTS / "quy_trinh.py")
qt_home = TMP / "qt-home"
(qt_home / "quy-trinh").mkdir(parents=True, exist_ok=True)
(qt_home / "quy-trinh" / "loc-vi-tri.toml").write_text("""
loai = "loc"
theo_doi = ["MADT"]
[nguon]
cot_tien = "$F"
[ket_qua]
ra = "LOC-{ten_file}.xlsx"
[[quy_tac]]
ma = "1"
khi = { NHOM = { bang = ["Máu"] } }
""", encoding="utf-8")
(qt_home / "quy-trinh" / "tach-theo-doi.toml").write_text("""
loai = "tach"
theo_doi = ["KHOA"]
[nguon]
cot_khoa = "KHOA"
cot_tong = ["TIEN"]
[ket_qua]
ra = "TACH-{ky}.xlsx"
[[nhom]]
gia_tri = ["K. MẮT"]
[[nhom]]
gia_tri = ["K. NỘI"]
""", encoding="utf-8")
du = TMP / "qt-du-lieu"
ra_qt = TMP / "qt-ra"
TD = ["QUYENSO", "NHOM", "LOAI", "TENDV", "MADT", "SOTIEN"]
DONG = [["A", "Thuốc", "T", "Paracetamol", 1, 100_000], ["A", "Máu", "M", "Hồng cầu", 1, 50_000],
        ["A", "Khám", "K", "Khám bệnh", 2, 30_000]]
luu_bang(du / "T09.xlsx", TD, DONG)
luu_bang(du / "T10.xlsx", TD[:2] + ["GHICHU"] + TD[2:], [r[:2] + [None] + r[2:] for r in DONG])
luu_bang(du / "T11.xlsx", [TD[0]] + TD[2:], [[r[0]] + r[2:] for r in DONG])
doi = [0, 1, 3, 2, 4, 5]
luu_bang(du / "T12.xlsx", [TD[i] for i in doi], [[r[i] for i in doi] for r in DONG])


def qt(*a: str) -> tuple[int, dict]:
    return chay(QT, "--home", str(qt_home), *a)


ma, d0 = qt("chay", "loc-vi-tri", str(du / "T09.xlsx"), "--ra-thu-muc", str(ra_qt))
kiem("lần chạy mốc (chưa có lần trước) ghi kết quả bình thường",
     (ma, (ra_qt / "LOC-T09.xlsx").exists()), (0, True))
ma, d = qt("chay", "loc-vi-tri", str(du / "T10.xlsx"), "--ra-thu-muc", str(ra_qt))
kiem("[WF-001] chèn cột làm cột tham chiếu theo vị trí ($F) đổi nghĩa → dừng hỏi, không ghi file, "
     "có diff bố cục chỉ rõ cột nghiêm trọng",
     (ma, d.get("trang_thai"), (ra_qt / "LOC-T10.xlsx").exists(),
      any(x.get("muc_do") == "nghiem_trong" for x in d.get("bo_cuc_thay_doi", []))),
     (2, "can_hoi", False, True))
ma, d = qt("chay", "loc-vi-tri", str(du / "T11.xlsx"), "--ra-thu-muc", str(ra_qt))
kiem("[WF-001] mất cột NHOM mà quy tắc dùng → dừng, không ghi file",
     (ma != 0, (ra_qt / "LOC-T11.xlsx").exists()), (True, False))
ma, d = qt("chay", "loc-vi-tri", str(du / "T12.xlsx"), "--ra-thu-muc", str(ra_qt))
k0, k = (d0.get("ket_qua") or [{}])[0], (d.get("ket_qua") or [{}])[0]
kiem("[WF-002] đổi chỗ hai cột không tham chiếu theo vị trí → kết quả như cũ, chỉ cảnh báo vô hại",
     (ma, (k.get("so_dong_giu"), k.get("tong_tien_giu")),
      [x.get("muc_do") for x in d.get("bo_cuc_thay_doi", [])]),
     (0, (2, 130_000), ["vo_hai"]))
kiem("[WF-002] lần chạy mốc cũng ra đúng 2 dòng giữ / 130.000 (cột tiền theo vị trí $F)",
     (k0.get("so_dong_giu"), k0.get("tong_tien_giu")), (2, 130_000))

luu_bang(du / "ts-09.xlsx", ["STT", "KHOA", "TIEN"], [[1, "K. MẮT", 100], [2, "K. NỘI", 200]])
luu_bang(du / "ts-10.xlsx", ["STT", "KHOA", "TIEN"],
         [[1, "K. MẮT", 100], [2, "K. NỘI", 200], [3, "K. MỚI", 300]])
qt("chay", "tach-theo-doi", str(du / "ts-09.xlsx"), "--ky", "T09.2026", "--ra-thu-muc", str(ra_qt))
ma, d = qt("chay", "tach-theo-doi", str(du / "ts-10.xlsx"), "--ky", "T10.2026",
           "--ra-thu-muc", str(ra_qt))
kiem("[WF-003] tach gặp giá trị mới ở cột theo dõi → dừng hỏi và KHÔNG có file kết quả nào",
     (ma, d.get("gia_tri_moi"), (ra_qt / "TACH-T10.2026.xlsx").exists()),
     (2, {"KHOA": ["K. MỚI"]}, False))

ma, d = qt("chay", "loc-vi-tri", str(du / "T09.xlsx"), "--ra-thu-muc", str(TMP / "xem-truoc"),
           "--xem-truoc")
kiem("--xem-truoc: tính đủ kết quả nhưng không ghi file và không ghi lịch sử",
     (ma, (d.get("ket_qua") or [{}])[0].get("so_dong_giu"), (TMP / "xem-truoc").exists()),
     (0, 2, False))

luu_bang(du / "lo" / "A.xlsx", TD, DONG)
luu_bang(du / "lo" / "B.xlsx", TD, DONG)
(qt_home / "quy-trinh" / "loc-lo.toml").write_text("""
loai = "loc"
[nguon]
cot_tien = "SOTIEN"
[ket_qua]
ra = "LOC-{ten_file}.xlsx"
[[quy_tac]]
ma = "1"
khi = { NHOM = { bang = ["Máu"] } }
""", encoding="utf-8")
ra_lo = TMP / "qt-ra-lo"
(ra_lo / "LOC-B.xlsx").mkdir(parents=True)  # đích thứ hai không ghi được
ma, d = qt("chay", "loc-lo", str(du / "lo" / "A.xlsx"), str(du / "lo" / "B.xlsx"),
           "--ra-thu-muc", str(ra_lo))
kiem("ghi một lô: file thứ hai lỗi thì file thứ nhất cũng không được công bố (không ghi dở dang)",
     (ma != 0, (ra_lo / "LOC-A.xlsx").exists(), sorted(p.name for p in ra_lo.iterdir())),
     (True, False, ["LOC-B.xlsx"]))

# --- G06 / G07 / G08 -----------------------------------------------------------------------
print("\n[G06/G07/G08] Hồ sơ lần chạy, phát lại, phê duyệt gắn nội dung, sửa sau khi duyệt")
import hashlib  # noqa: E402
import re  # noqa: E402

HS = str(SCRIPTS / "ho_so_kiem_toan.py")
au = TMP / "au-home"
(au / "quy-trinh").mkdir(parents=True, exist_ok=True)
QT_AU = (qt_home / "quy-trinh" / "loc-lo.toml").read_text(encoding="utf-8")
(au / "quy-trinh" / "loc-au.toml").write_text(QT_AU, encoding="utf-8")
src_au = luu_bang(TMP / "au-du-lieu" / "DT.xlsx", TD, DONG)
ra_au = TMP / "au-ra"


def qt_au(*a: str, home: Path = au) -> tuple[int, dict]:
    return chay(QT, "--home", str(home), *a)


def hs(*a: str, home: Path = au) -> tuple[int, dict]:
    return chay(HS, "--home", str(home), *a)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


ma, d1 = qt_au("chay", "loc-au", str(src_au), "--ra-thu-muc", str(ra_au),
               "--nguoi-lap", "Nguyen Van A")
ma, d2 = qt_au("chay", "loc-au", str(src_au), "--ra-thu-muc", str(ra_au),
               "--nguoi-lap", "Nguyen Van A")
r1, r2 = d1.get("run_id"), d2.get("run_id")
_, m1 = hs("xem", str(r1))
_, m2 = hs("xem", str(r2))
kiem("[AUD] mỗi lần chạy có hồ sơ: SHA-256 đầy đủ của nguồn, quy tắc, kết quả; giờ có múi giờ; "
     "mã đơn vị",
     (len((m1.get("dau_vao") or [{}])[0].get("sha256", "")),
      len((m1.get("quy_tac") or {}).get("sha256", "")),
      len((m1.get("dau_ra") or [{}])[0].get("sha256", "")),
      bool(re.search(r"[+-]\d\d:\d\d$", m1.get("thoi_gian", ""))), m1.get("don_vi")),
     (64, 64, 64, True, "mac-dinh"))
kiem("[AUD] chạy lại cùng dữ liệu, cùng quy tắc → run_id khác nhau, ket_qua_sha256 như nhau",
     (r1 != r2 and r1 is not None, m1.get("ket_qua_sha256") == m2.get("ket_qua_sha256")
      and m1.get("ket_qua_sha256") is not None), (True, True))
ma, v = hs("kiem", str(r2))
kiem("[AUD] kiểm hồ sơ vừa tạo: nguồn, quy tắc, kết quả còn nguyên; sổ cái nối chuỗi hợp lệ",
     (ma, v.get("toan_ven"), v.get("so_cai_hop_le")), (0, True, True))
ma, p = hs("phat-lai", str(r2))
kiem("[AUD] phát lại từ hồ sơ (cùng nguồn + cùng quy tắc) ra đúng kết quả nghiệp vụ",
     (ma, p.get("ket_qua_khop")), (0, True))

ma, a = hs("duyet", str(r2), "--vai-tro", "nguoi-phe-duyet", "--quyet-dinh", "dong-y",
           "--nguoi", "Tran Thi B")
kiem("[G07] phê duyệt khi không có danh tính được xác thực → UNVERIFIED_HUMAN_REVIEW, KHÔNG "
     "bao giờ thành 'approved'",
     (ma, a.get("xac_thuc"), a.get("trang_thai_duyet")),
     (0, "UNVERIFIED_HUMAN_REVIEW", "da_xem_chua_xac_thuc"))
env_gia = {**MOI_TRUONG, "KE_TOAN_VN_NGUOI_DUYET": "Tran Thi B", "USER": "tranthib"}
ma, a = chay(HS, "--home", str(au), "duyet", str(r2), "--vai-tro", "nguoi-kiem-tra",
             "--quyet-dinh", "dong-y", "--nguoi", "Tran Thi B", env=env_gia)
kiem("[G07] khai tên qua biến môi trường / tài khoản máy không phải là xác thực", a.get("xac_thuc"),
     "UNVERIFIED_HUMAN_REVIEW")

ra_file = ra_au / "LOC-DT.xlsx"
truoc = sha(ra_file)
ma, d = qt_au("chay", "loc-au", str(src_au), "--ra-thu-muc", str(ra_au))
kiem("[G08] chạy lại ghi đè lên kết quả ĐÃ DUYỆT → dừng hỏi, file đã duyệt giữ nguyên từng byte",
     (ma, d.get("trang_thai"), sha(ra_file) == truoc), (2, "can_hoi", True))
ma, d = qt_au("chay", "loc-au", str(src_au), "--ra-thu-muc", str(ra_au), "--ban-sua-doi")
_, m3 = hs("xem", str(d.get("run_id")))
kiem("[G08] --ban-sua-doi → ghi bản mới -SUA1 trỏ về lần chạy đã duyệt; bản đã duyệt không đổi",
     ((ra_au / "LOC-DT-SUA1.xlsx").exists(), m3.get("sua_doi_cho"), sha(ra_file) == truoc),
     (True, r2, True))

with ra_file.open("ab") as f:
    f.write(b"\0")
ma, v = hs("kiem", str(r2))
kiem("[AUD-001] kết quả đã duyệt bị đổi 1 byte → phát hiện, phê duyệt mất hiệu lực",
     (ma != 0, v.get("toan_ven"), [x.get("nhan") for x in v.get("thay_doi", [])],
      v.get("trang_thai_duyet")),
     (True, False, ["LOC-DT.xlsx"], "vo_hieu"))

qt_au_tep = au / "quy-trinh" / "loc-au.toml"
qt_au_tep.write_text(QT_AU.replace('bang = ["Máu"]', 'bang = ["Máu", "Khám"]'), encoding="utf-8")
ma, p = hs("phat-lai", str(r1))
ma_k, v1 = hs("kiem", str(r1))
kiem("[AUD-002] quy tắc đổi sau lần chạy → phát lại báo quy tắc đã đổi và kết quả lệch; hồ sơ cũ "
     "vẫn nguyên (sổ cái hợp lệ)",
     (ma, p.get("quy_tac_da_doi"), p.get("ket_qua_khop"), v1.get("so_cai_hop_le"),
      v1.get("ho_so_khop_so_cai")),
     (2, True, False, True, True))
qt_au_tep.write_text(QT_AU, encoding="utf-8")

xuat_dir = TMP / "goi-kiem-toan"
ma, x = hs("xuat", str(r1), "--ra", str(xuat_dir))
goi = (xuat_dir / f"{r1}.json").read_text(encoding="utf-8") if (xuat_dir / f"{r1}.json").exists() \
    else ""
kiem("[AUD] gói kiểm toán: có JSON + Markdown, không lộ đường dẫn tuyệt đối hay nội dung dòng dữ "
     "liệu, có câu miễn trừ không phải chứng nhận",
     (ma, (xuat_dir / f"{r1}.md").exists(), str(TMP) in goi, "Paracetamol" in goi,
      "không phải chứng nhận" in goi),
     (0, True, False, False, True))
ma, g = chay(HS, "kiem-goi", str(xuat_dir / f"{r1}.json"), "--thu-muc-tep", str(src_au.parent))
kiem("[AUD] kiểm độc lập gói kiểm toán với file nguồn gốc: hồ sơ khớp mã băm, nguồn khớp",
     (ma, g.get("ho_so_khop"), g.get("dau_vao_khop")), (0, True, True))

mf = next((au / "ho-so").glob(f"{r1}.json"))
mf.write_text(mf.read_text(encoding="utf-8").replace('"loc-au"', '"loc-sua"'), encoding="utf-8")
ma, v = hs("kiem", str(r1))
kiem("sửa tay file hồ sơ → không còn khớp mã băm đã ghi trong sổ cái", (ma != 0,
     v.get("ho_so_khop_so_cai")), (True, False))

# Cổng: lần chạy needs_review (chấp nhận giá trị mới) không duyệt được nếu không ghi ngoại lệ
au2 = TMP / "au2-home"
(au2 / "quy-trinh").mkdir(parents=True)
(au2 / "don-vi.toml").write_text("[phan_quyen]\ntach_nhiem = true\n", encoding="utf-8")
(au2 / "quy-trinh" / "loc-td.toml").write_text(
    QT_AU.replace('loai = "loc"', 'loai = "loc"\ntheo_doi = ["MADT"]'), encoding="utf-8")
src_td1 = luu_bang(TMP / "au2-du-lieu" / "M1.xlsx", TD, DONG)
src_td2 = luu_bang(TMP / "au2-du-lieu" / "M2.xlsx", TD, DONG + [["A", "Khám", "K", "X", 17, 1]])
qt_au("chay", "loc-td", str(src_td1), "--ra-thu-muc", str(TMP / "au2-ra"), home=au2)
ma, d = qt_au("chay", "loc-td", str(src_td2), "--ra-thu-muc", str(TMP / "au2-ra"),
              "--chap-nhan-gia-tri-moi", "--nguoi-lap", "Le Van C", home=au2)
r_nl = d.get("run_id")
kiem("[G04/G07] chấp nhận giá trị mới = ngoại lệ do người chạy khai → lần chạy needs_review",
     (ma, d.get("trang_thai_ket_qua")), (0, "needs_review"))
ma, a = hs("duyet", str(r_nl), "--vai-tro", "nguoi-phe-duyet", "--quyet-dinh", "dong-y",
           "--nguoi", "Pham D", home=au2)
kiem("[G04/G07] duyệt lần chạy needs_review mà không ghi lý do ngoại lệ → bị từ chối", ma, 2)
ma, a = hs("duyet", str(r_nl), "--vai-tro", "nguoi-phe-duyet", "--quyet-dinh", "dong-y",
           "--nguoi", "Le Van C", "--ngoai-le", "Đã kiểm MADT 17", home=au2)
kiem("[G07] tách nhiệm bật: người lập không tự duyệt lần chạy của mình", ma, 2)
ma, a = hs("duyet", str(r_nl), "--vai-tro", "nguoi-phe-duyet", "--quyet-dinh", "dong-y",
           "--nguoi", "Pham D", "--ngoai-le", "Đã kiểm MADT 17 là đối tượng hợp lệ", home=au2)
kiem("[G07] người khác duyệt, có ghi lý do ngoại lệ → ghi nhận (vẫn chưa xác thực danh tính)",
     (ma, a.get("xac_thuc"), a.get("ngoai_le")),
     (0, "UNVERIFIED_HUMAN_REVIEW", "Đã kiểm MADT 17 là đối tượng hợp lệ"))

# Hóa đơn: lần đọc needs_review cũng không duyệt được nếu không ghi ngoại lệ
ma, d = chay(DH, str(d3), "--ghi-ho-so")
ma2, a = hs("duyet", str(d.get("run_id")), "--vai-tro", "nguoi-phe-duyet", "--quyet-dinh",
            "dong-y", "--nguoi", "Pham D", home=HOME)
kiem("[INV-003] lô hóa đơn thiếu số có hồ sơ, nhưng không duyệt được nếu không ghi ngoại lệ",
     (ma, d.get("run_id") is not None, ma2), (0, True, 2))

# --- G10 -----------------------------------------------------------------------------------
print("\n[G10] Cô lập đơn vị: danh mục, quy trình, quy ước, hồ sơ không lẫn sang nhau")
ten = TMP / "ten-home"
for dv, ten_goi in (("bv-a", "KHS"), ("bv-b", "SINH HÓA")):
    g = ten / "don-vi" / dv
    (g / "quy-trinh").mkdir(parents=True)
    (g / "danh-muc.toml").write_text(f'[khoa.KHS]\nluong = "{ten_goi}"\n', encoding="utf-8")
    (g / "quy-trinh" / "tach-khoa.toml").write_text("""
loai = "tach"
[nguon]
cot_khoa = "KHOA"
cot_tong = ["TIEN"]
[ten_goi]
bang = "khoa"
nguon = "luong"
[ket_qua]
ra = "TACH-{ten_file}.xlsx"
[[nhom]]
ten = "KHS"
ma = ["KHS"]
""", encoding="utf-8")
(ten / "don-vi" / "bv-a" / "quy-trinh" / "chi-cua-a.toml").write_text(
    (ten / "don-vi" / "bv-a" / "quy-trinh" / "tach-khoa.toml").read_text(), encoding="utf-8")
src_ten = luu_bang(TMP / "ten-du-lieu" / "luong.xlsx", ["KHOA", "TIEN"],
                   [["KHS", 100], ["SINH HÓA", 200]])
kq_dv = {}
for dv in ("bv-a", "bv-b"):
    ma, d = chay(QT, "--home", str(ten), "--don-vi", dv, "chay", "tach-khoa", str(src_ten),
                 "--ra-thu-muc", str(TMP / f"ten-ra-{dv}"))
    kq_dv[dv] = (d.get("ket_qua") or [{}])[0].get("nhom", [{}])[0].get("tong", {}).get("TIEN")
kiem("[TEN-001] hai đơn vị dùng cùng mã KHS khác nghĩa → mỗi bên dùng danh mục của chính mình",
     kq_dv, {"bv-a": 100, "bv-b": 200})
_, ds = chay(QT, "--home", str(ten), "--don-vi", "bv-b", "danh-sach")
kiem("[TEN-001] đơn vị B không thấy quy trình riêng của đơn vị A",
     sorted(x["ten"] for x in ds.get("quy_trinh", [])), ["tach-khoa"])
ma, d = chay(QT, "--home", str(ten), "--don-vi", "bv-a", "chay", "tach-khoa", str(src_ten),
             "--ra-thu-muc", str(TMP / "ten-ra-a2"))
ma2, _ = chay(HS, "--home", str(ten), "--don-vi", "bv-b", "duyet", str(d.get("run_id")),
              "--vai-tro", "nguoi-phe-duyet", "--quyet-dinh", "dong-y", "--nguoi", "X")
kiem("[TEN-001] đơn vị B không duyệt được (thậm chí không thấy) lần chạy của đơn vị A",
     ma2 != 0, True)
ma, d = chay(QT, "--home", str(ten), "--don-vi", "../bv-a", "danh-sach")
kiem("mã đơn vị có '../' bị từ chối (không thoát ra ngoài thư mục bộ nhớ)", ma, 1)
chay(BN, "--don-vi", "bv-a", "ghi", "--loai", "quy-uoc", "--chu-de", "Ten cot luong",
     "--noi-dung", "Cột KHS là khoa sinh hóa.")
_, t = chay(BN, "--don-vi", "bv-b", "tra", "ten cot luong")
_, t2 = chay(BN, "--don-vi", "bv-a", "tra", "ten cot luong")
kiem("[TEN-001] quy ước riêng của đơn vị A không hiện ra khi tra cho đơn vị B",
     (t.get("so_ghi_chu"), t2.get("so_ghi_chu")), (0, 1))
mang = re.compile(r"^\s*(import|from)\s+(urllib\.request|http\.client|requests|socket|ftplib|"
                  r"smtplib|httpx|aiohttp)\b", re.M)
co_mang = sorted(p.name for p in SCRIPTS.glob("*.py") if mang.search(p.read_text(encoding="utf-8")))
kiem("không script nào tự gọi mạng — dữ liệu đơn vị không thể rời máy qua công cụ", co_mang, [])

# --- G11 -----------------------------------------------------------------------------------
print("\n[G11] Bất biến kế toán — không chỉ so với file mẫu")
(qt_home / "quy-trinh" / "loc-bb.toml").write_text(QT_AU, encoding="utf-8")
src_bb = luu_bang(TMP / "bb" / "BB.xlsx", TD, DONG + [["A", "Thuốc", "T", "Hoàn trả", 8, -20_000]])
ma, d = qt("chay", "loc-bb", str(src_bb), "--ra-thu-muc", str(TMP / "bb-ra"))
bb = (d.get("ket_qua") or [{}])[0].get("bat_bien", {})
kiem("bảo toàn: gốc = giữ + loại cả số dòng lẫn tiền (kể cả dòng hoàn trả âm), và đọc lại file "
     "kết quả khớp đúng số đó",
     (bb.get("bao_toan_dong"), bb.get("bao_toan_tien"), bb.get("doc_lai_khop"),
      d.get("trang_thai_ket_qua")), (True, True, True, "draft"))
src_tong = luu_bang(TMP / "bb" / "TONG.xlsx", TD, DONG + [[None, "Tổng cộng", None, None, None,
                                                            180_000]])
ma, d = qt("chay", "loc-bb", str(src_tong), "--ra-thu-muc", str(TMP / "bb-ra"))
bb = (d.get("ket_qua") or [{}])[0].get("bat_bien", {})
kiem("dòng 'Tổng cộng' lẫn trong dữ liệu (sẽ cộng trùng) → chỉ ra đúng dòng, needs_review",
     (bb.get("dong_tong_nghi_ngo"), d.get("trang_thai_ket_qua")), ([5], "needs_review"))
src_cbc = luu_bang(TMP / "bb" / "CBC.xlsx", TD, DONG + [["A", "Xét nghiệm", "XN",
                                                         "Tổng phân tích tế bào máu", 1, 40_000]])
ma, d = qt("chay", "loc-bb", str(src_cbc), "--ra-thu-muc", str(TMP / "bb-ra"))
kiem("tên dịch vụ bắt đầu bằng 'Tổng ...' (Tổng phân tích tế bào máu) KHÔNG bị nhầm là dòng tổng",
     (d.get("ket_qua") or [{}])[0].get("bat_bien", {}).get("dong_tong_nghi_ngo"), [])

import xlsxwriter  # noqa: E402

wb = xlsxwriter.Workbook(str(TMP / "bb" / "ts-cong.xlsx"))
ws = wb.add_worksheet()
ws.write_row("A1", ["STT", "KHOA", "TIEN"])
ws.write_row("A2", [1, "K. MẮT", 100])
ws.write_row("A3", [2, "K. NỘI", 200])
ws.write_row("A4", [3, "K. MẮT"])
ws.write_formula("C4", "=SUM(C2:C3)", None, 300)
wb.close()
ma, d = qt("chay", "tach-theo-doi", str(TMP / "bb" / "ts-cong.xlsx"), "--ky", "T09.2026",
           "--ra-thu-muc", str(TMP / "bb-ra"), "--khong-ghi-lich-su")
bb = (d.get("ket_qua") or [{}])[0].get("bat_bien", {})
kiem("tach: ô tiền là công thức SUM trong vùng dữ liệu (dòng cộng dồn) → chỉ ra dòng 4, "
     "needs_review; bảo toàn nguồn = các nhóm + ngoài nhóm",
     (bb.get("dong_tong_nghi_ngo"), d.get("trang_thai_ket_qua"), bb.get("bao_toan_tien")),
     ([4], "needs_review", True))
# 0,005 đồng mỗi phần: làm tròn từng phần (0,01 + 0,01 + 0,01) ≠ làm tròn tổng (0,015 → 0,01)
le = [[1, "K. MẮT", 0.005], [2, "K. NỘI", 0.005], [3, "K. KHÁC", 0.005]]
luu_bang(TMP / "bb" / "ts-le.xlsx", ["STT", "KHOA", "TIEN"], le)
ma, d = qt("chay", "tach-theo-doi", str(TMP / "bb" / "ts-le.xlsx"), "--ky", "T09.2026",
           "--ra-thu-muc", str(TMP / "bb-ra"), "--khong-ghi-lich-su", "--chap-nhan-gia-tri-moi")
src_le = luu_bang(TMP / "bb" / "LE.xlsx", TD, [["A", "Máu", "T", "x", 1, 0.005],
                                                ["A", "Thuốc", "T", "y", 1, 0.005]])
ma2, d2 = qt("chay", "loc-bb", str(src_le), "--ra-thu-muc", str(TMP / "bb-ra"),
             "--khong-ghi-lich-su")
kiem("số tiền lẻ (0,005 đồng mỗi phần, như khấu hao chia 12) không làm hỏng bảo toàn GIẢ do làm tròn từng "
     "phần (tach và loc vẫn chạy)", (ma, ma2), (0, 0))
(qt_home / "quy-trinh" / "tach-stt.toml").write_text(
    'loai = "tach"\n[nguon]\ncot_khoa = "STT"\ncot_stt = "STT"\n[[nhom]]\ngia_tri = ["1"]\n',
    encoding="utf-8")
ma, d = qt("kiem", "tach-stt")
kiem("dùng cột STT làm khoá tách bị từ chối (STT đánh lại mỗi kỳ, không phải mã ổn định)",
     ma, 1)

# --- G09 -----------------------------------------------------------------------------------
print("\n[G09] Chấm thầu: bảng so sánh sơ bộ vs kết luận chính thức")
SS = str(SCRIPTS / "so_sanh_thau.py")
tdir = TMP / "thau"
tdir.mkdir()
home_thau = TMP / "home-thau"
env_thau = {**MOI_TRUONG, "KE_TOAN_VN_HOME": str(home_thau)}
ma, _ = chay(str(SCRIPTS / "doc_hsdt.py"), str(FIX / "goi-thau/hsdt"), "--ra",
             str(tdir / "h.json"), env=env_thau)
ma, d = chay(SS, str(tdir / "h.json"), "--danh-muc", str(FIX / "goi-thau/danh_muc_hsmt.csv"),
             env=env_thau)
kiem("mặc định (sơ bộ) vẫn chạy và xếp hạng như cũ, nhưng ghi rõ trang_thai = so_bo",
     (ma, d.get("tom_tat", {}).get("trang_thai"), len(d.get("tom_tat", {}).get("xep_hang_so_bo",
                                                                               [])) > 0),
     (0, "so_bo", True))
ma, d = chay(SS, str(tdir / "h.json"), "--danh-muc", str(FIX / "goi-thau/danh_muc_hsmt.csv"),
             "--che-do", "chinh-thuc", env=env_thau)
t = d.get("tom_tat", {})
kiem("[BID-001] chính thức mà chưa có kết quả kỹ thuật do tổ chuyên gia điền → từ chối xếp hạng, "
     "mã 2",
     (ma, t.get("trang_thai"), t.get("xep_hang_so_bo"),
      t.get("gia_de_nghi_trung_thau_du_kien_khoan_4")),
     (2, "needs_review", [], None))
chay(str(SCRIPTS / "cham_ky_thuat.py"), str(FIX / "goi-thau/hsdt"), "--yeu-cau",
     str(FIX / "goi-thau/yeu_cau_ky_thuat.csv"), "--ra", str(tdir / "phieu.xlsx"), env=env_thau)
import openpyxl  # noqa: E402


def dien_phieu(ket_luan_c: str) -> None:
    wb = openpyxl.load_workbook(tdir / "phieu.xlsx")
    ws = wb["Phieu cham ky thuat"]
    hdr = {str(c.value).strip(): int(c.column or 0) for c in ws[3]}
    for r in range(4, ws.max_row + 1):
        nt = str(ws.cell(row=r, column=hdr["nha_thau"]).value or "")
        ws.cell(row=r, column=hdr["ket_luan"]).value = (
            ket_luan_c if nt.startswith("Nha thau C") else "Đạt")
    wb.save(tdir / "phieu.xlsx")


dien_phieu("")
ma, d = chay(SS, str(tdir / "h.json"), "--danh-muc", str(FIX / "goi-thau/danh_muc_hsmt.csv"),
             "--ket-qua-ky-thuat", str(tdir / "phieu.xlsx"), "--che-do", "chinh-thuc",
             env=env_thau)
kiem("[BID-001] chính thức mà còn nhà thầu chưa có kết luận kỹ thuật → needs_review, mã 2",
     (ma, d.get("tom_tat", {}).get("trang_thai")), (2, "needs_review"))
dien_phieu("Không đạt")
ma, d = chay(SS, str(tdir / "h.json"), "--danh-muc", str(FIX / "goi-thau/danh_muc_hsmt.csv"),
             "--ket-qua-ky-thuat", str(tdir / "phieu.xlsx"), "--che-do", "chinh-thuc",
             env=env_thau)
t = d.get("tom_tat", {})
kiem("[BID-001] đủ kết luận kỹ thuật → bảng để tổ chuyên gia ký (không phải kết luận của máy), "
     "chỉ nhà thầu vượt kỹ thuật được xếp hạng",
     (ma, t.get("trang_thai"), [x["nha_thau"].split(" - ")[0] for x in t.get("xep_hang_so_bo", [])]),
     (0, "cho_to_chuyen_gia_ky", ["Nha thau B", "Nha thau D", "Nha thau A"]))
kiem("chấm thầu không ghi gì vào bộ nhớ (HSDT không lưu lại, không vào hồ sơ kiểm toán)",
     sorted(str(p.relative_to(home_thau)) for p in home_thau.rglob("*") if p.is_file())
     if home_thau.exists() else [], [])

# --- G12 -----------------------------------------------------------------------------------
print("\n[G12] Đầu vào không tin cậy")
import time  # noqa: E402

bom = ('<?xml version="1.0"?><!DOCTYPE l [<!ENTITY a "aaaaaaaaaa">'
       + "".join(f'<!ENTITY {chr(98 + i)} "&{chr(97 + i)};&{chr(97 + i)};&{chr(97 + i)};'
                 f'&{chr(97 + i)};&{chr(97 + i)};&{chr(97 + i)};&{chr(97 + i)};&{chr(97 + i)};'
                 f'&{chr(97 + i)};&{chr(97 + i)};">' for i in range(8))
       + "]><HDon><SHDon>&i;</SHDon></HDon>")
d_bom = thu_muc("bom", {"bom.xml": bom})
bat_dau = time.monotonic()
ma, d = chay(DH, str(d_bom))
kiem("[SEC-001] XML có ENTITY lồng nhau (billion laughs) bị từ chối ngay, không treo máy",
     (((d.get("chi_tiet") or [{}])[0]).get("trang_thai_dong"), time.monotonic() - bat_dau < 10),
     ("loi_doc", True))
d_lon = TMP / "hd" / "lon"
d_lon.mkdir(parents=True)
with (d_lon / "lon.xml").open("wb") as f:
    f.write(b"<HDon>" + b" " * (21 * 1024 * 1024) + b"</HDon>")
ma, d = chay(DH, str(d_lon))
kiem("XML lớn hơn giới hạn 20 MB → không đọc, báo lỗi đọc",
     ((d.get("chi_tiet") or [{}])[0]).get("trang_thai_dong"), "loi_doc")
d_ct = thu_muc("cong-thuc", {"a.xml": hdon("00000061").replace(
    "<Ten>Cong ty mau</Ten>", "<Ten>=HYPERLINK(\"http://x.invalid\",\"bam\")</Ten>")})
chay(DH, str(d_ct), "--ra", str(TMP / "ct.csv"))
chay(DH, str(d_ct), "--ra", str(TMP / "ct.xlsx"))
import csv  # noqa: E402

with (TMP / "ct.csv").open(encoding="utf-8-sig") as f:
    ten_csv = next(csv.DictReader(f))["ten_ban"]
o = openpyxl.load_workbook(TMP / "ct.xlsx").worksheets[0]
cot_ten = [c.value for c in o[1]].index("ten_ban") + 1
kiem("[SEC-001] tên người bán dạng công thức → ra CSV/Excel là CHỮ, không phải công thức chạy được",
     (ten_csv.startswith("'="), o.cell(2, cot_ten).data_type), (True, "s"))
src_ct = luu_bang(TMP / "bb" / "CT.xlsx", TD, [["A", "Thuốc", "T", "x", 1, 1]])
wb_ct = openpyxl.load_workbook(src_ct)
wb_ct.worksheets[0]["D2"].value = "=1+1"
wb_ct.worksheets[0]["D2"].data_type = "s"
wb_ct.save(src_ct)
qt("chay", "loc-bb", str(src_ct), "--ra-thu-muc", str(TMP / "ct-ra"), "--khong-ghi-lich-su")
o = openpyxl.load_workbook(TMP / "ct-ra" / "LOC-CT.xlsx")["GIỮ LẠI"]
kiem("[SEC-001] ô chữ '=1+1' trong bản kết xuất được chép sang kết quả lọc vẫn là CHỮ",
     (o["D2"].value, o["D2"].data_type), ("=1+1", "s"))

# --- Kết thúc ------------------------------------------------------------------------------
print()
shutil.rmtree(TMP, ignore_errors=True)
if loi:
    print(f"❌ {len(loi)} phép kiểm thất bại:")
    for x in loi:
        print(f"   - {x}")
    sys.exit(1)
print("✅ Tất cả phép kiểm kiểm soát đều đạt")
