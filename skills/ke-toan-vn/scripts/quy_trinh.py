#!/usr/bin/env python3
"""Chạy các quy trình định kỳ đã ghi nhớ (tách theo khoa, lọc bản kết xuất, đối chiếu).

    quy_trinh.py danh-sach                         # các quy trình đã ghi nhớ
    quy_trinh.py xem tach-so-tai-san               # quy tắc, câu hỏi còn mở, lần chạy gần nhất
    quy_trinh.py kiem tach-so-tai-san              # kiểm cú pháp, không đọc dữ liệu
    quy_trinh.py chay tach-so-tai-san "SO TAI SAN T09.xlsx" --ky T09.2026
    quy_trinh.py chay loc-dlbc-khoa MAT-10.xlsx NT-10.xlsx YHCT-10.xlsx
    quy_trinh.py chay doi-chieu-mau --a "MAU T10.xlsx" --b "XNT 10.xlsx" --ky T10.2026
    quy_trinh.py chay ./thu.toml file.xlsx         # chạy một file quy trình chưa ghi nhớ

Quy trình nằm ở <bộ nhớ>/quy-trinh/<tên>.toml (bộ nhớ: xem references/bo-nho.md). Danh mục
dùng chung (tên gọi khoa theo từng nguồn, các tập mã) ở <bộ nhớ>/danh-muc.toml. Cú pháp đầy
đủ: references/quy-trinh.md.

Kết quả luôn là JSON ở stdout với `trang_thai`:
  xong     đã ghi file kết quả                                  (mã thoát 0)
  xem_truoc  đã tính, KHÔNG ghi gì (--xem-truoc)                 (mã thoát 0)
  can_hoi  dừng lại, cần hỏi kế toán (giá trị mới chưa có quy tắc, hoặc bố cục đổi ở cột quy
           trình dùng) (mã thoát 2) — không ghi file kết quả nào
  loi      quy trình hoặc dữ liệu sai                             (mã thoát 1)
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _chung import can_thu_vien, in_json  # noqa: E402
from _quy_trinh import (  # noqa: E402
    CanHoi, LoiQuyTrinh, dien_ky, doc_danh_muc, doc_quy_trinh, doc_tieu_de, doc_toml,
    ghi_gia_tri_da_biet, ghi_lich_su, home_mac_dinh, kiem_gia_tri_moi, lan_chay_truoc,
    so_bo_cuc, thu_muc_quy_trinh, tim_quy_trinh,
)
from _xuat import BoGhi  # noqa: E402


def _dong_co(loai: str):
    if loai == "tach":
        import _tach as m
    elif loai == "loc":
        import _loc as m
    else:
        import _doi_chieu_bang as m
    return m


def _nap(ten: str, home: Path, ky: str | None) -> dict:
    qt = doc_quy_trinh(tim_quy_trinh(ten, home))
    qt = {k: (v if k in ("nhat_ky", "cau_hoi_mo") else dien_ky(v, ky)) for k, v in qt.items()}
    return _dong_co(qt["loai"]).kiem(qt, doc_danh_muc(home))


def _cong_khai(qt: dict) -> dict:
    return {k: v for k, v in qt.items() if not k.startswith("_")}


def lenh_danh_sach(home: Path) -> dict:
    ds = []
    for p in sorted(thu_muc_quy_trinh(home).glob("*.toml")):
        try:
            qt = doc_toml(p)
        except LoiQuyTrinh as e:
            ds.append({"ten": p.stem, "loi": str(e)})
            continue
        truoc = lan_chay_truoc(home, p.stem)
        ds.append({"ten": p.stem, "loai": qt.get("loai"), "mo_ta": qt.get("mo_ta"),
                   "so_cau_hoi_mo": len(qt.get("cau_hoi_mo", [])),
                   "lan_chay_gan_nhat": truoc and truoc.get("thoi_gian")})
    return {"thu_muc": str(thu_muc_quy_trinh(home)), "quy_trinh": ds}


def lenh_xem(home: Path, ten: str) -> dict:
    p = tim_quy_trinh(ten, home)
    qt = doc_toml(p)
    return {"tep": str(p), "quy_trinh": qt, "lan_chay_gan_nhat": lan_chay_truoc(home, p.stem)}


def _tep_theo_vai(spec: dict, tep) -> list[tuple[str, Path]]:
    if spec["loai"] == "doi-chieu":
        return [(v, tep[v]) for v in ("a", "b") if v in tep]
    return [("nguon", p) for p in tep]


def kiem_bo_cuc(spec: dict, m, tep, truoc: dict | None, chap_nhan: bool) -> list:
    """Kiểm bố cục cột TRƯỚC khi đọc dữ liệu hay ghi bất cứ gì.

    Bản cũ so bố cục SAU khi đã ghi file kết quả, nên một cột đổi nghĩa chỉ hiện thành cảnh báo
    cạnh một file đã nằm trên đĩa. Nay: thay đổi vô hại thì chạy tiếp và báo; thay đổi chạm tới
    cột quy trình dùng thì dừng hỏi, chưa ghi gì.
    """
    cau_hinh = m.cot_tham_chieu(spec)
    cu = (truoc or {}).get("dau_vao") or []
    ra = []
    for i, (vai, p) in enumerate(_tep_theo_vai(spec, tep)):
        ch = cau_hinh[vai]
        _, tieu_de = doc_tieu_de(p, ch["sheet"], ch["dong_tieu_de"])
        if spec["loai"] == "doi-chieu":
            mau = next((x for x in cu if x.get("vai") == vai), None)
        else:
            mau = cu[min(i, len(cu) - 1)] if cu else None
        d = so_bo_cuc((mau or {}).get("tieu_de"), tieu_de, ch["cot"])
        if d:
            ra.append({"tep": str(p), **d})
    if any(x["muc_do"] == "nghiem_trong" for x in ra) and not chap_nhan:
        raise CanHoi("Bố cục cột đổi ở cột mà quy trình dùng — số liệu có thể đổi nghĩa",
                     {"bo_cuc_thay_doi": ra, "buoc_tiep": (
                         "Cho kế toán xem `bo_cuc_thay_doi`. Nếu bản kết xuất đổi mẫu thì sửa "
                         "quy trình (tên/vị trí cột) rồi chạy lại; nếu đã kiểm và chắc chắn cột "
                         "vẫn đúng nghĩa thì chạy lại với --chap-nhan-bo-cuc. Chưa file kết quả "
                         "nào được ghi.")})
    return ra


def lenh_chay(home: Path, a) -> int:
    spec = _nap(a.quy_trinh, home, a.ky)
    m = _dong_co(spec["loai"])
    bo_ghi = BoGhi(xem_truoc=a.xem_truoc)
    tuy_chon = {"ky": a.ky, "ra_thu_muc": a.ra_thu_muc, "bien_the": a.bien_the,
                "khong_bien_the": a.khong_bien_the, "bo_ghi": bo_ghi}
    if spec["loai"] == "doi-chieu":
        if a.tep:
            raise LoiQuyTrinh("Quy trình đối chiếu nhận file qua --a và --b, không nhận file rời")
        tep = {k: Path(v) for k, v in (("a", a.a), ("b", a.b)) if v}
    else:
        if a.a or a.b:
            raise LoiQuyTrinh("--a/--b chỉ dùng cho quy trình đối chiếu")
        tep = [Path(t) for t in a.tep]

    ghi_lai = not (a.khong_ghi_lich_su or a.xem_truoc)
    truoc = lan_chay_truoc(home, spec["ten"])
    try:
        bo_cuc = kiem_bo_cuc(spec, m, tep, truoc, a.chap_nhan_bo_cuc)
        if spec["loai"] == "loc":
            tg = m.chay(spec, tep, tuy_chon)
            gia_tri = kiem_gia_tri_moi(home, spec["ten"], tg["_quan_sat"],
                                       a.chap_nhan_gia_tri_moi, ghi=False)
            kq = m.ghi_tat_ca(spec, tg, tuy_chon)
            kq.setdefault("canh_bao", [])
        else:
            kq = m.chay(spec, tep, tuy_chon)
            gia_tri = kiem_gia_tri_moi(home, spec["ten"], kq["_quan_sat"],
                                       a.chap_nhan_gia_tri_moi, ghi=False) \
                if kq["_quan_sat"] else None
        bo_ghi.cong_bo()
    finally:
        bo_ghi.huy()

    if any(x["muc_do"] == "vo_hai" for x in bo_cuc):
        kq["canh_bao"].append("Bố cục cột khác lần chạy trước ở các cột quy trình không dùng "
                              "theo vị trí — kiểm tra bản kết xuất có đổi phần mềm/mẫu không "
                              "(chi tiết ở `bo_cuc_thay_doi`)")
    if any(x["muc_do"] == "nghiem_trong" for x in bo_cuc):
        kq["canh_bao"].append("Đã chạy dù bố cục đổi ở cột quy trình dùng (--chap-nhan-bo-cuc) — "
                              "xác nhận này là của người chạy, chưa được xác thực")

    thoi_gian = datetime.now().astimezone().isoformat(timespec="seconds")
    if ghi_lai:
        if gia_tri is not None:
            ghi_gia_tri_da_biet(home, spec["ten"], gia_tri["_gop"])
        ghi_lich_su(home, spec["ten"], {
            "thoi_gian": thoi_gian, "ky": a.ky, "dau_vao": kq["_dau_vao"],
            "ket_qua": kq["ket_qua"], "canh_bao": kq["canh_bao"]})
    if gia_tri is not None:
        gia_tri.pop("_gop", None)
    in_json({
        "trang_thai": "xem_truoc" if a.xem_truoc else "xong",
        "quy_trinh": spec["ten"], "loai": spec["loai"],
        "thoi_gian": thoi_gian, "ket_qua": kq["ket_qua"], "canh_bao": kq["canh_bao"],
        "bo_cuc_thay_doi": bo_cuc, "gia_tri_theo_doi": gia_tri,
        "cau_hoi_mo": spec.get("cau_hoi_mo", []),
        "da_ghi_file": not a.xem_truoc,
        "buoc_tiep": ("Xem trước: chưa ghi file hay lịch sử nào." if a.xem_truoc else
                      "Báo kế toán: file kết quả, các cảnh báo, và nhắc lại mọi câu hỏi còn mở."),
    })
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--home", help="Thư mục bộ nhớ (mặc định: tự tìm .ke-toan-vn)")
    sub = p.add_subparsers(dest="lenh", required=True)
    sub.add_parser("danh-sach", help="Liệt kê quy trình đã ghi nhớ")
    s = sub.add_parser("xem", help="Xem một quy trình")
    s.add_argument("quy_trinh")
    s = sub.add_parser("kiem", help="Kiểm cú pháp quy trình")
    s.add_argument("quy_trinh")
    s.add_argument("--ky", help="Kỳ dùng để điền {thang}/{nam} khi kiểm (mặc định một kỳ giả)")
    s = sub.add_parser("chay", help="Chạy quy trình trên dữ liệu kỳ mới")
    s.add_argument("quy_trinh", help="Tên quy trình hoặc đường dẫn file .toml")
    s.add_argument("tep", nargs="*", help="File nguồn (tach: 1 file; loc: một hoặc nhiều)")
    s.add_argument("--a", help="File bên A (quy trình đối chiếu)")
    s.add_argument("--b", help="File bên B (quy trình đối chiếu)")
    s.add_argument("--ky", help='Nhãn kỳ, thay vào {ky} trong tên file kết quả, vd "T09.2026"')
    s.add_argument("--ra-thu-muc", help="Thư mục ghi kết quả; mặc định cạnh file nguồn")
    s.add_argument("--bien-the", help="Ép dùng một biến thể (quy trình loc)")
    s.add_argument("--khong-bien-the", action="store_true", help="Không áp biến thể nào")
    s.add_argument("--chap-nhan-gia-tri-moi", action="store_true",
                   help="Kế toán đã xác nhận các giá trị mới: ghi nhận và chạy tiếp")
    s.add_argument("--khong-ghi-lich-su", action="store_true",
                   help="Chạy thử, không ghi vào lịch sử (vd khi kiểm chứng kỳ cũ)")
    s.add_argument("--xem-truoc", action="store_true",
                   help="Tính đủ kết quả nhưng KHÔNG ghi file kết quả, lịch sử hay hồ sơ")
    s.add_argument("--chap-nhan-bo-cuc", action="store_true",
                   help="Kế toán đã kiểm: bố cục đổi ở cột quy trình dùng nhưng nghĩa không đổi")
    a = p.parse_args()

    home = Path(a.home).expanduser() if a.home else home_mac_dinh()
    try:
        if a.lenh == "danh-sach":
            in_json(lenh_danh_sach(home))
        elif a.lenh == "xem":
            in_json(lenh_xem(home, a.quy_trinh))
        elif a.lenh == "kiem":
            spec = _nap(a.quy_trinh, home, a.ky or "T01.2000")
            in_json({"trang_thai": "hop_le", "quy_trinh": _cong_khai(spec)})
        else:
            can_thu_vien("openpyxl")
            return lenh_chay(home, a)
    except CanHoi as e:
        in_json({"trang_thai": "can_hoi", "thong_diep": str(e),
                 "buoc_tiep": "Hỏi kế toán từng giá trị: giữ hay loại? Loại thì thêm quy tắc vào "
                              "quy trình; giữ thì chạy lại với --chap-nhan-gia-tri-moi. Chưa "
                              "file kết quả nào được ghi.", **e.chi_tiet})
        return 2
    except (LoiQuyTrinh, OSError) as e:
        in_json({"trang_thai": "loi", "thong_diep": str(e)})
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
