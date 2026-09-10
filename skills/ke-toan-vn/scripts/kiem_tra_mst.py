#!/usr/bin/env python3
"""Kiểm tra mã số thuế Việt Nam (10 số / 13 số / mã định danh 12 số).

    kiem_tra_mst.py 0100109106
    kiem_tra_mst.py 0100109106-001 0101243150
    kiem_tra_mst.py --tep danh_sach.csv --cot mst_ban

⚠️  VỀ ĐỘ TIN CẬY CỦA CHECKSUM

Cấu trúc MST 10 số là N1N2 (mã phân khoảng tỉnh) + N3..N9 (số tăng dần) + N10 (chữ số kiểm tra),
theo khoản 2 Điều 30 Luật Quản lý thuế 2019 và TT 105/2020/TT-BTC.

Bộ trọng số modulus-11 dùng ở đây — [31,29,23,19,17,13,7,5,3] — là quy ước được dùng rộng rãi
trong các thư viện mã nguồn mở, NHƯNG không đối chiếu được nguyên văn với TT 105/2020/TT-BTC.

Vì vậy script này CỐ TÌNH không kết luận 'sai'. Nó báo `nghi_ngo` và đề nghị tra cứu trực tuyến.
Lý do nghiệp vụ: với kế toán, báo nhầm một MST hợp lệ là 'sai' gây mất thời gian đi xác minh và
làm mất lòng tin vào công cụ, tệ hơn nhiều so với việc gợi ý kiểm tra lại một MST vốn đúng.
Sai checksum thường là do OCR nhầm số chứ không phải hóa đơn giả.

Muốn chắc chắn: tra tại https://tracuunnt.gdt.gov.vn hoặc Cổng thông tin quốc gia về ĐKDN.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _chung import in_json  # noqa: E402
from chuan_hoa import chuan_mst  # noqa: E402

TRONG_SO = [31, 29, 23, 19, 17, 13, 7, 5, 3]

# Mã phân khoảng tỉnh hợp lệ nằm trong khoảng này; ngoài khoảng là chắc chắn có vấn đề.
_PHAN_KHOANG_MIN, _PHAN_KHOANG_MAX = 1, 99


def chu_so_kiem_tra(chin_so: str) -> int:
    tong = sum(int(d) * w for d, w in zip(chin_so, TRONG_SO))
    return 10 - (tong % 11)


def kiem_tra(gia_tri) -> dict:
    """Trả về dict mô tả tình trạng MST.

    tinh_trang: hop_le | nghi_ngo | sai_dinh_dang | ma_dinh_danh | trong
    """
    goc = "" if gia_tri is None else str(gia_tri).strip()
    kq = {"gia_tri_goc": goc, "mst": None, "tinh_trang": None, "ghi_chu": ""}

    if not goc:
        kq["tinh_trang"] = "trong"
        kq["ghi_chu"] = "Không có giá trị"
        return kq

    mst = chuan_mst(goc)
    if not mst:
        kq["tinh_trang"] = "sai_dinh_dang"
        kq["ghi_chu"] = "Không tìm thấy dãy số nào giống mã số thuế"
        return kq

    kq["mst"] = mst
    so = mst.replace("-", "")

    if len(so) == 12:
        # Mã định danh cá nhân (CCCD) dùng thay MST cho cá nhân — không có checksum kiểu MST
        kq["tinh_trang"] = "ma_dinh_danh"
        kq["ghi_chu"] = ("12 chữ số — có vẻ là số định danh cá nhân (CCCD) dùng thay MST. "
                         "Không áp dụng được checksum của MST doanh nghiệp.")
        return kq

    if len(so) not in (10, 13) or not so.isdigit():
        kq["tinh_trang"] = "sai_dinh_dang"
        kq["ghi_chu"] = f"Độ dài {len(so)} chữ số — MST phải là 10 hoặc 13 chữ số"
        return kq

    if len(so) == 13:
        duoi = so[10:]
        if not (_int_an_toan(duoi) and 1 <= int(duoi) <= 999):
            kq["tinh_trang"] = "sai_dinh_dang"
            kq["ghi_chu"] = f"Ba số cuối '{duoi}' phải nằm trong 001–999 (số thứ tự đơn vị phụ thuộc)"
            return kq
        kq["ghi_chu"] = f"MST đơn vị phụ thuộc của {so[:10]}, số thứ tự {duoi}. "

    phan_khoang = int(so[:2])
    if not (_PHAN_KHOANG_MIN <= phan_khoang <= _PHAN_KHOANG_MAX):
        kq["tinh_trang"] = "nghi_ngo"
        kq["ghi_chu"] += f"Hai số đầu '{so[:2]}' không giống mã phân khoảng tỉnh hợp lệ."
        return kq

    mong_doi = chu_so_kiem_tra(so[:9])
    thuc_te = int(so[9])

    if mong_doi > 9:
        # tổng % 11 == 0 -> công thức ra 10, không phải chữ số hợp lệ. Quy ước xử lý
        # trường hợp này không tra được trong văn bản, nên không kết luận gì cả.
        kq["tinh_trang"] = "khong_ket_luan"
        kq["ghi_chu"] += ("Thuật toán rơi vào trường hợp biên (tổng chia hết cho 11) mà quy ước "
                          "xử lý không tra được trong văn bản. Không kết luận — tra tại "
                          "tracuunnt.gdt.gov.vn nếu cần chắc chắn.")
        return kq

    if mong_doi == thuc_te:
        kq["tinh_trang"] = "hop_le"
        kq["ghi_chu"] += "Chữ số kiểm tra khớp."
    else:
        kq["tinh_trang"] = "nghi_ngo"
        kq["ghi_chu"] += (
            f"Chữ số kiểm tra không khớp (tính ra {mong_doi}, trên hóa đơn là {thuc_te}). "
            "Thường do đọc/OCR nhầm một chữ số. Nên tra lại tại tracuunnt.gdt.gov.vn "
            "trước khi kết luận — xem cảnh báo ở đầu script về độ tin cậy của thuật toán."
        )
    return kq


def _int_an_toan(s: str) -> bool:
    return s.isdigit()


def main() -> int:
    p = argparse.ArgumentParser(
        description="Kiểm tra mã số thuế Việt Nam.",
        epilog="Script báo 'nghi_ngo' chứ không báo 'sai' — xem docstring để biết vì sao.",
    )
    p.add_argument("mst", nargs="*", help="Một hoặc nhiều mã số thuế")
    p.add_argument("--tep", help="File CSV/Excel chứa cột MST cần kiểm")
    p.add_argument("--cot", default="mst", help="Tên cột MST trong file (mặc định: mst)")
    args = p.parse_args()

    danh_sach = list(args.mst)

    if args.tep:
        from _chung import can_thu_vien
        can_thu_vien("pandas")
        import pandas as pd

        duong_dan = Path(args.tep).expanduser()
        if not duong_dan.exists():
            print(f"Không tìm thấy file: {duong_dan}", file=sys.stderr)
            return 1
        khung = (pd.read_csv(duong_dan, dtype=str) if duong_dan.suffix.lower() == ".csv"
                 else pd.read_excel(duong_dan, dtype=str))
        if args.cot not in khung.columns:
            print(f"Không có cột '{args.cot}'. Các cột hiện có: {list(khung.columns)}",
                  file=sys.stderr)
            return 1
        danh_sach += khung[args.cot].dropna().tolist()

    if not danh_sach:
        p.print_help()
        return 2

    ket_qua = [kiem_tra(m) for m in danh_sach]
    tom_tat = {}
    for r in ket_qua:
        tom_tat[r["tinh_trang"]] = tom_tat.get(r["tinh_trang"], 0) + 1

    in_json({"tong_so": len(ket_qua), "tom_tat": tom_tat, "chi_tiet": ket_qua})

    # Thoát 0 kể cả khi có MST nghi ngờ: đây là công cụ rà soát, không phải cổng chặn.
    return 0


if __name__ == "__main__":
    sys.exit(main())
