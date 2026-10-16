#!/usr/bin/env python3
"""Xác định chế độ kế toán (và chế độ hóa đơn) áp dụng cho một đơn vị trong một năm tài chính.

    che_do_ke_toan.py --loai-don-vi doanh-nghiep --dau-nam-tai-chinh 2026-01-01
    che_do_ke_toan.py --loai-don-vi sieu-nho --ngay 2026-03-15 --thang-dau-nam 4
    che_do_ke_toan.py --loai-don-vi su-nghiep-cong-lap --tu-chu chi-thuong-xuyen \
                      --dau-nam-tai-chinh 2026-01-01
    che_do_ke_toan.py --hoa-don-ngay 2026-06-30

Chế độ kế toán đổi theo NGÀY BẮT ĐẦU NĂM TÀI CHÍNH, không theo ngày hôm nay: TT 99/2025 áp
dụng cho năm tài chính bắt đầu từ hoặc sau 01/01/2026, nên doanh nghiệp có năm tài chính
01/10/2025–30/09/2026 vẫn dùng TT 200 cho cả năm đó. Và chế độ đổi theo LOẠI ĐƠN VỊ — chữ
"bệnh viện" không nói gì: bệnh viện công là đơn vị sự nghiệp công lập (TT 24/2024), bệnh viện
tư là doanh nghiệp.

Kết quả là JSON ở stdout:
  trang_thai = xac_dinh      đủ căn cứ để chọn một chế độ          (mã thoát 0)
  trang_thai = can_xac_nhan  thiếu thông tin hoặc luật để ngỏ — liệt kê ứng viên và câu
                             cần hỏi; KHÔNG chọn thay người dùng   (mã thoát 2)

Đây là bảng tra có trích dẫn, không phải ý kiến pháp lý. Mọi trích dẫn ghi ngày kiểm; khi
bảng này cũ hơn văn bản mới thì văn bản mới thắng — tra lại theo references/phap-ly.md.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _chung import in_json  # noqa: E402

KIEM_NGAY = "2026-10-16"

# Một nơi duy nhất giữ căn cứ. `xac_minh` = đã đọc nguyên văn điều khoản ở nguồn ghi bên cạnh.
CAN_CU = {
    "TT99-D31": {
        "van_ban": "Thông tư 99/2025/TT-BTC (27/10/2025)", "dieu_khoan": "Điều 31 khoản 1, 2, 3",
        "trich": "có hiệu lực thi hành kể từ ngày 01/01/2026 và áp dụng cho năm tài chính bắt đầu "
                 "từ hoặc sau ngày 01/01/2026. Thông tư này thay thế cho các Thông tư số "
                 "200/2014/TT-BTC ...",
        "nguon": "https://congbao.chinhphu.vn/van-ban/thong-tu-so-99-2025-tt-btc-46529.htm",
        "xac_minh": True},
    "TT99-D2": {
        "van_ban": "Thông tư 99/2025/TT-BTC", "dieu_khoan": "Điều 2",
        "trich": "áp dụng cho các doanh nghiệp thuộc mọi lĩnh vực, mọi thành phần kinh tế; tổ chức "
                 "tín dụng ... theo hướng dẫn của Ngân hàng Nhà nước",
        "nguon": "https://congbao.chinhphu.vn/van-ban/thong-tu-so-99-2025-tt-btc-46529.htm",
        "xac_minh": True},
    "TT58-D12": {
        "van_ban": "Thông tư 58/2026/TT-BTC (25/5/2026)", "dieu_khoan": "Điều 12 khoản 1, 2",
        "trich": "có hiệu lực thi hành kể từ ngày 01/7/2026 và áp dụng cho năm tài chính bắt đầu từ "
                 "ngày hoặc sau ngày 01/7/2026. Thông tư số 132/2018/TT-BTC ... hết hiệu lực kể "
                 "từ ngày Thông tư này có hiệu lực thi hành.",
        "nguon": "https://congbao.chinhphu.vn/van-ban/thong-tu-so-58-2026-tt-btc-469663.htm",
        "xac_minh": True},
    "TT58-D2-D4": {
        "van_ban": "Thông tư 58/2026/TT-BTC", "dieu_khoan": "Điều 2 khoản 2; Điều 4 khoản 3",
        "trich": "Hộ kinh doanh, cá nhân kinh doanh nếu có nhu cầu thì được lựa chọn áp dụng; "
                 "doanh nghiệp siêu nhỏ được lựa chọn áp dụng chế độ kế toán doanh nghiệp nhỏ và vừa",
        "nguon": "https://congbao.chinhphu.vn/van-ban/thong-tu-so-58-2026-tt-btc-469663.htm",
        "xac_minh": True},
    "TT24-D2": {
        "van_ban": "Thông tư 24/2024/TT-BTC (17/4/2024)", "dieu_khoan": "Điều 2 khoản 1 điểm b",
        "trich": "Đơn vị sự nghiệp công lập (trừ các đơn vị sự nghiệp công lập tự đảm bảo chi thường "
                 "xuyên và chi đầu tư được cơ quan có thẩm quyền cho phép áp dụng chế độ kế toán "
                 "doanh nghiệp; ... thì phải lập báo cáo quyết toán kinh phí hoạt động quy định tại "
                 "Phụ lục III ...)",
        "nguon": "https://congbao.chinhphu.vn/van-ban/thong-tu-so-24-2024-tt-btc-41775/49902.htm",
        "xac_minh": True},
    "TT24-D13": {
        "van_ban": "Thông tư 24/2024/TT-BTC", "dieu_khoan": "Điều 13 khoản 1, 2",
        "trich": "có hiệu lực kể từ ngày 01 tháng 01 năm 2025 và áp dụng từ năm tài chính 2025 ... "
                 "Thông tư số 107/2017/TT-BTC ... hết hiệu lực",
        "nguon": "https://congbao.chinhphu.vn/van-ban/thong-tu-so-24-2024-tt-btc-41775/49902.htm",
        "xac_minh": True},
    "TT133": {
        "van_ban": "Thông tư 133/2016/TT-BTC", "dieu_khoan": "(chế độ kế toán DN nhỏ và vừa)",
        "trich": "Không bị TT 99/2025 thay thế (Điều 31 TT 99 chỉ thay TT 200, 75/2015, 53/2016, "
                 "195/2012); TT 58/2026 Điều 4 khoản 3 vẫn dẫn chiếu chế độ kế toán DNNVV.",
        "nguon": "https://congbao.chinhphu.vn/van-ban/thong-tu-so-99-2025-tt-btc-46529.htm",
        "xac_minh": False},
    "ND254-D43": {
        "van_ban": "Nghị định 254/2026/NĐ-CP (30/6/2026)", "dieu_khoan": "Điều 43",
        "trich": "có hiệu lực thi hành từ ngày 01 tháng 7 năm 2026 ... các Nghị định sau đây hết "
                 "hiệu lực: Nghị định số 123/2020/NĐ-CP; Điều 1 Nghị định số 41/2022/NĐ-CP; "
                 "Nghị định số 70/2025/NĐ-CP",
        "nguon": "https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-254-2026-nd-cp-469957.htm",
        "xac_minh": True},
    "TT91": {
        "van_ban": "Thông tư 91/2026/TT-BTC (30/6/2026)", "dieu_khoan": "(hướng dẫn NĐ 254/2026)",
        "trich": "hiệu lực 01/7/2026 (thuộc tính văn bản trên Công báo)",
        "nguon": "https://congbao.chinhphu.vn/van-ban/thong-tu-so-91-2026-tt-btc-470171.htm",
        "xac_minh": True},
}

CHE_DO = {
    "TT99/2025": "Chế độ kế toán doanh nghiệp — Thông tư 99/2025/TT-BTC",
    "TT200/2014": "Chế độ kế toán doanh nghiệp — Thông tư 200/2014/TT-BTC (năm tài chính bắt đầu "
                  "trước 01/01/2026)",
    "TT133/2016": "Chế độ kế toán doanh nghiệp nhỏ và vừa — Thông tư 133/2016/TT-BTC",
    "TT58/2026": "Chế độ kế toán doanh nghiệp siêu nhỏ — Thông tư 58/2026/TT-BTC",
    "TT132/2018": "Chế độ kế toán doanh nghiệp siêu nhỏ — Thông tư 132/2018/TT-BTC (hết hiệu lực "
                  "01/7/2026)",
    "TT24/2024": "Chế độ kế toán hành chính, sự nghiệp — Thông tư 24/2024/TT-BTC",
    "TT107/2017": "Chế độ kế toán hành chính, sự nghiệp — Thông tư 107/2017/TT-BTC (trước năm "
                  "tài chính 2025)",
}

MOC_TT99 = date(2026, 1, 1)
MOC_TT58 = date(2026, 7, 1)
MOC_TT24 = date(2025, 1, 1)
MOC_ND254 = date(2026, 7, 1)
MOC_ND123 = date(2022, 7, 1)

LOAI_DON_VI = ("doanh-nghiep", "dnnvv", "sieu-nho", "ho-kinh-doanh", "su-nghiep-cong-lap",
               "co-quan-nha-nuoc", "khac")
TU_CHU = ("chi-thuong-xuyen-va-dau-tu", "chi-thuong-xuyen", "mot-phan-chi-thuong-xuyen",
          "nsnn-bao-dam", "chua-ro")


def _ngay(s: str) -> date:
    return date.fromisoformat(s)


def nam_tai_chinh(dau: date) -> dict:
    """Năm tài chính 12 tháng bắt đầu từ `dau` (Luật Kế toán: kỳ kế toán năm là mười hai tháng)."""
    ket_thuc = date(dau.year + 1, dau.month, 1) - timedelta(days=1)
    return {"bat_dau": dau.isoformat(), "ket_thuc": ket_thuc.isoformat()}


def dau_nam_tu_ngay(ngay: date, thang_dau: int) -> date:
    nam = ngay.year if ngay.month >= thang_dau else ngay.year - 1
    return date(nam, thang_dau, 1)


def _kq(che_do: str | None, ly_do: list, can_cu: list, ung_vien=(), hoi=()) -> dict:
    return {
        "trang_thai": "xac_dinh" if che_do else "can_xac_nhan",
        "che_do": {"id": che_do, "ten": CHE_DO[che_do]} if che_do else None,
        "ung_vien": [{"id": u, "ten": CHE_DO[u]} for u in ung_vien],
        "can_xac_nhan": list(hoi),
        "ly_do": ly_do,
        "trich_dan": [{"id": c, **CAN_CU[c], "kiem_ngay": KIEM_NGAY} for c in can_cu],
    }


def _dn(dau: date, ly_do: list) -> dict:
    if dau >= MOC_TT99:
        return _kq("TT99/2025", ly_do + [
            f"Năm tài chính bắt đầu {dau.isoformat()} ≥ 01/01/2026 → TT 99/2025 (thay TT 200)."],
            ["TT99-D31", "TT99-D2"])
    return _kq("TT200/2014", ly_do + [
        f"Năm tài chính bắt đầu {dau.isoformat()} < 01/01/2026 → TT 99/2025 chưa áp dụng cho năm "
        f"này; dùng TT 200/2014 cho CẢ năm, không đổi giữa năm. TT 99 áp dụng từ năm tài chính kế "
        f"tiếp, bắt đầu {date(dau.year + 1, dau.month, dau.day).isoformat()}."],
        ["TT99-D31"])


def xac_dinh(loai: str | None, dau: date, da_chon: str | None = None,
             tu_chu: str | None = None, duoc_phep_dn: str | None = None,
             co_phan_hoa: bool = False, to_chuc_tin_dung: bool = False) -> dict:
    if loai is None:
        return _kq(None, ["Chưa biết loại đơn vị — không suy chế độ từ tên đơn vị."], [], hoi=[
            "Đơn vị là doanh nghiệp (lớn / nhỏ và vừa / siêu nhỏ), hộ kinh doanh, đơn vị sự nghiệp "
            "công lập hay cơ quan nhà nước?"])
    if loai == "khac":
        return _kq(None, ["Loại đơn vị 'khác' không có quy tắc chọn sẵn."], [], hoi=[
            "Đơn vị thuộc đối tượng áp dụng của văn bản nào (TT 99/2025, TT 133/2016, "
            "TT 58/2026, TT 24/2024, hay chế độ đặc thù ngành)? Cần người có chuyên môn xác nhận."])

    if to_chuc_tin_dung:
        return _kq(None, ["Tổ chức tín dụng theo chế độ của Ngân hàng Nhà nước (Điều 2 TT 99)."],
                   ["TT99-D2"], hoi=["Văn bản chế độ kế toán của NHNN áp dụng cho đơn vị?"])

    if loai == "doanh-nghiep":
        kq = _dn(dau, [])
        if co_phan_hoa and kq["che_do"] and kq["che_do"]["id"] == "TT99/2025":
            kq["ly_do"].append("Đang cổ phần hóa: các nội dung kế toán cổ phần hóa DNNN liệt kê ở "
                               "khoản 2 Điều 31 TT 99 vẫn thực hiện theo TT 200/2014.")
        return kq

    if loai == "dnnvv":
        ung = ["TT133/2016"] + (["TT99/2025"] if dau >= MOC_TT99 else ["TT200/2014"])
        can_cu = ["TT133", "TT99-D31"]
        if da_chon:
            chon = {"TT133": "TT133/2016", "TT99": "TT99/2025", "TT200": "TT200/2014"}.get(da_chon)
            if chon in ung:
                return _kq(chon, [f"DNNVV đã chọn {chon}; áp dụng nhất quán tối thiểu một kỳ kế "
                                  f"toán năm (khoản 3 Điều 31 TT 99)."], can_cu)
            return _kq(None, [f"Chế độ đã chọn {da_chon} không áp dụng được cho năm tài chính "
                              f"bắt đầu {dau.isoformat()}."], can_cu, ung,
                       ["Đơn vị thực sự áp dụng chế độ nào cho năm này?"])
        return _kq(None, ["DNNVV được chọn chế độ — phải lấy lựa chọn thực tế của đơn vị, "
                          "không đoán."], can_cu, ung,
                   ["Đơn vị đang áp dụng TT 133/2016 hay chế độ doanh nghiệp?"])

    if loai == "sieu-nho":
        can_cu = ["TT58-D12", "TT58-D2-D4"]
        if da_chon == "TT133":
            return _kq("TT133/2016", ["DN siêu nhỏ đã chọn chế độ DNNVV (khoản 3 Điều 4 TT 58)."],
                       can_cu + ["TT133"])
        nam = nam_tai_chinh(dau)
        if dau >= MOC_TT58:
            return _kq("TT58/2026", [f"Năm tài chính bắt đầu {dau.isoformat()} ≥ 01/7/2026 → "
                                     f"TT 58/2026."], can_cu)
        if _ngay(nam["ket_thuc"]) < MOC_TT58:
            return _kq("TT132/2018", [f"Năm tài chính kết thúc {nam['ket_thuc']} trước 01/7/2026 "
                                      f"→ TT 132/2018 còn hiệu lực cho cả năm."], can_cu)
        return _kq(None, [
            f"Năm tài chính {nam['bat_dau']}–{nam['ket_thuc']} vắt qua 01/7/2026: TT 132/2018 hết "
            f"hiệu lực từ 01/7/2026 nhưng TT 58/2026 chỉ áp dụng cho năm tài chính bắt đầu từ "
            f"01/7/2026. Văn bản không nói rõ phần còn lại của năm này dùng chế độ nào."],
            can_cu, ["TT132/2018", "TT58/2026"],
            ["Cần người có chuyên môn (hoặc hướng dẫn của Bộ Tài chính) xác nhận chế độ cho phần "
             "năm tài chính từ 01/7/2026."])

    if loai == "ho-kinh-doanh":
        if da_chon == "TT58" and dau >= MOC_TT58:
            return _kq("TT58/2026", ["Hộ kinh doanh tự chọn áp dụng TT 58/2026 (khoản 2 Điều 2)."],
                       ["TT58-D2-D4", "TT58-D12"])
        return _kq(None, ["Hộ kinh doanh có chế độ kế toán riêng; chỉ dùng TT 58/2026 khi tự chọn "
                          "và năm tài chính bắt đầu từ 01/7/2026."], ["TT58-D2-D4"],
                   hoi=["Hộ kinh doanh áp dụng chế độ kế toán nào (văn bản riêng cho hộ, hay đã "
                        "chọn TT 58/2026)?"])

    if loai in ("su-nghiep-cong-lap", "co-quan-nha-nuoc"):
        cu = dau < MOC_TT24
        hcsn = "TT107/2017" if cu else "TT24/2024"
        can_cu = ["TT24-D2", "TT24-D13"]
        ly_do = []
        if (dau.month, dau.day) != (1, 1):
            ly_do.append("Đơn vị hành chính, sự nghiệp dùng năm tài chính theo năm ngân sách "
                         "(01/01–31/12) — kiểm lại ngày bắt đầu đã khai.")
        if loai == "co-quan-nha-nuoc":
            return _kq(hcsn, ly_do + [f"Cơ quan nhà nước → {hcsn}."], can_cu)
        if tu_chu is None or tu_chu == "chua-ro":
            return _kq(None, ly_do + ["Đơn vị sự nghiệp công lập: chế độ phụ thuộc mức tự chủ tài "
                                      "chính và quyết định cho phép của cơ quan có thẩm quyền."],
                       can_cu, [hcsn, "TT99/2025" if dau >= MOC_TT99 else "TT200/2014"],
                       ["Mức tự chủ tài chính của đơn vị (tự bảo đảm chi thường xuyên và chi đầu "
                        "tư / chi thường xuyên / một phần / NSNN bảo đảm)?",
                        "Đơn vị có văn bản cho phép áp dụng chế độ kế toán doanh nghiệp không?"])
        if tu_chu == "chi-thuong-xuyen-va-dau-tu":
            if duoc_phep_dn == "co":
                kq = _dn(dau, ly_do + [
                    "ĐVSNCL tự bảo đảm chi thường xuyên và chi đầu tư, được cơ quan có thẩm quyền "
                    "cho phép → chế độ kế toán doanh nghiệp (ngoại lệ ở điểm b khoản 1 Điều 2 "
                    "TT 24/2024). Nếu có kinh phí NSNN, viện trợ, vay nợ nước ngoài hoặc phí được "
                    "khấu trừ để lại thì vẫn phải lập báo cáo quyết toán kinh phí hoạt động theo "
                    "Phụ lục III TT 24/2024."])
                kq["trich_dan"].append({"id": "TT24-D2", **CAN_CU["TT24-D2"],
                                        "kiem_ngay": KIEM_NGAY})
                return kq
            if duoc_phep_dn is None:
                return _kq(None, ly_do + ["Tự chủ chi thường xuyên và chi đầu tư nhưng chưa rõ đã "
                                          "được phép áp dụng chế độ doanh nghiệp."], can_cu,
                           [hcsn, "TT99/2025" if dau >= MOC_TT99 else "TT200/2014"],
                           ["Đơn vị có văn bản cho phép áp dụng chế độ kế toán doanh nghiệp không?"])
        return _kq(hcsn, ly_do + [f"Đơn vị sự nghiệp công lập (mức tự chủ: {tu_chu}) → {hcsn}."],
                   can_cu)

    raise ValueError(loai)


def che_do_hoa_don(ngay: date) -> dict:
    """Văn bản hóa đơn điện tử theo NGÀY LẬP hóa đơn.

    NĐ 254/2026 có hiệu lực 01/7/2026 và chấm dứt NĐ 123/2020 (Điều 43); Điều 44 không có điều
    khoản chuyển tiếp chung cho hóa đơn lập trước đó, nên hóa đơn lập trước 01/7/2026 vẫn xét
    theo văn bản có hiệu lực tại thời điểm lập. Đây là cách hiểu chung về hiệu lực theo thời
    gian — ghi rõ để người duyệt thấy.
    """
    if ngay >= MOC_ND254:
        return {"id": "ND254/2026", "ten": "NĐ 254/2026/NĐ-CP + TT 91/2026/TT-BTC",
                "trang_thai": "xac_dinh", "can_cu": ["ND254-D43", "TT91"]}
    if ngay >= MOC_ND123:
        return {"id": "ND123/2020", "ten": "NĐ 123/2020/NĐ-CP (đã sửa bởi NĐ 41/2022, NĐ 70/2025)",
                "trang_thai": "xac_dinh", "can_cu": ["ND254-D43"],
                "ghi_chu": "Lập trước 01/7/2026: xét theo văn bản có hiệu lực tại ngày lập (NĐ 254 "
                           "không có chuyển tiếp chung cho hóa đơn đã lập)."}
    return {"id": None, "ten": None, "trang_thai": "can_xac_nhan", "can_cu": [],
            "ghi_chu": "Hóa đơn lập trước 01/7/2022 — ngoài phạm vi bảng tra này."}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--loai-don-vi", choices=LOAI_DON_VI)
    p.add_argument("--dau-nam-tai-chinh", help="Ngày bắt đầu năm tài chính, YYYY-MM-DD")
    p.add_argument("--ngay", help="Ngày giao dịch/báo cáo, YYYY-MM-DD (dùng với --thang-dau-nam)")
    p.add_argument("--thang-dau-nam", type=int, default=1,
                   help="Tháng bắt đầu năm tài chính (mặc định 1)")
    p.add_argument("--da-chon", choices=["TT133", "TT99", "TT200", "TT58"],
                   help="Chế độ đơn vị ĐÃ chọn (khi được phép chọn)")
    p.add_argument("--tu-chu", choices=TU_CHU, help="Mức tự chủ tài chính (ĐVSNCL)")
    p.add_argument("--duoc-phep-ap-dung-che-do-dn", choices=["co", "khong"])
    p.add_argument("--dang-co-phan-hoa", action="store_true")
    p.add_argument("--to-chuc-tin-dung", action="store_true")
    p.add_argument("--hoa-don-ngay", help="Chỉ tra chế độ hóa đơn cho ngày lập YYYY-MM-DD")
    a = p.parse_args()

    try:
        if a.hoa_don_ngay:
            hd = che_do_hoa_don(_ngay(a.hoa_don_ngay))
            hd["trich_dan"] = [{"id": c, **CAN_CU[c], "kiem_ngay": KIEM_NGAY}
                               for c in hd["can_cu"]]
            in_json({"trang_thai": hd["trang_thai"], "che_do_hoa_don": hd})
            return 0 if hd["trang_thai"] == "xac_dinh" else 2
        if a.dau_nam_tai_chinh:
            dau = _ngay(a.dau_nam_tai_chinh)
        elif a.ngay:
            dau = dau_nam_tu_ngay(_ngay(a.ngay), a.thang_dau_nam)
        else:
            in_json({"trang_thai": "loi", "thong_diep": "Cần --dau-nam-tai-chinh hoặc --ngay"})
            return 1
    except ValueError as e:
        in_json({"trang_thai": "loi", "thong_diep": f"Ngày không hợp lệ: {e}"})
        return 1
    if dau.day != 1:
        in_json({"trang_thai": "loi", "thong_diep": "Năm tài chính 12 tháng bắt đầu từ ngày 01 "
                                                    f"của một tháng; nhận được {dau.isoformat()}"})
        return 1

    kq = xac_dinh(a.loai_don_vi, dau, a.da_chon, a.tu_chu, a.duoc_phep_ap_dung_che_do_dn,
                  a.dang_co_phan_hoa, a.to_chuc_tin_dung)
    kq["nam_tai_chinh"] = nam_tai_chinh(dau)
    kq["luu_y"] = ("Bảng tra có trích dẫn, kiểm ngày " + KIEM_NGAY + " — không phải ý kiến pháp "
                   "lý. Trường hợp can_xac_nhan cần người có chuyên môn quyết định.")
    in_json(kq)
    return 0 if kq["trang_thai"] == "xac_dinh" else 2


if __name__ == "__main__":
    sys.exit(main())
