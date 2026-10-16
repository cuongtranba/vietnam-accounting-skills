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
kiem("[ACC-003] DN siêu nhỏ: năm bắt đầu 01/7/2026 → TT 58/2026; 01/4/2026 → cần xác nhận "
     "(TT 132/2018 hết hiệu lực giữa năm, TT 58 chỉ áp cho năm bắt đầu từ 01/7/2026)",
     ((d.get("che_do") or {}).get("id"), ma2, d2.get("trang_thai"),
      sorted(u["id"] for u in d2.get("ung_vien", []))),
     ("TT58/2026", 2, "can_xac_nhan", ["TT132/2018", "TT58/2026"]))

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
kiem("hóa đơn lập 30/6/2026 theo NĐ 123/2020; lập 01/7/2026 theo NĐ 254/2026",
     ((d.get("che_do_hoa_don") or {}).get("id"), (d2.get("che_do_hoa_don") or {}).get("id")),
     ("ND123/2020", "ND254/2026"))

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

# --- Kết thúc ------------------------------------------------------------------------------
print()
shutil.rmtree(TMP, ignore_errors=True)
if loi:
    print(f"❌ {len(loi)} phép kiểm thất bại:")
    for x in loi:
        print(f"   - {x}")
    sys.exit(1)
print("✅ Tất cả phép kiểm kiểm soát đều đạt")
