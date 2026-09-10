#!/usr/bin/env python3
"""Đối chiếu hai bảng số liệu, tìm chênh lệch.

    doi_chieu.py bang_ke.csv so_sach.csv \\
        --khoa-a "so_hd" --khoa-b "so_chung_tu" \\
        --tien-a "tien_hang" --tien-b "phat_sinh_co" \\
        --nguong 1 --ra ket_qua.xlsx

Nếu tên cột hai bảng giống nhau thì chỉ cần --khoa và --tien.

Bốn nhóm kết quả:
  chi_co_a     có ở bảng A, không có ở B  (vd: có hóa đơn nhưng chưa vào sổ)
  chi_co_b     có ở bảng B, không có ở A  (vd: đã ghi sổ nhưng thiếu hóa đơn — nghiêm trọng hơn)
  lech_tien    có ở cả hai nhưng số tiền khác
  trung_lap    trùng khoá TRONG cùng một bảng

Nhóm thứ tư quan trọng nhưng hay bị bỏ sót: một hóa đơn vào sổ hai lần không xuất hiện ở ba nhóm
đầu, nhưng làm sai tổng — và đây là lỗi rất hay gặp khi nhập liệu thủ công.

Ngưỡng làm tròn: chênh 1-2 đồng do làm tròn thuế là bình thường. Báo hết thì người dùng phải lọc
tay hàng trăm dòng vô nghĩa và sẽ bỏ qua luôn cả những dòng thật. Nhưng script LUÔN báo tổng số
dòng đã bỏ qua — người dùng cần biết mình đang không nhìn thấy gì.
"""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _chung import can_thu_vien, canh_bao, in_json  # noqa: E402
from chuan_hoa import chuan_mst, lam_sach_text, so_vn  # noqa: E402


def doc(duong_dan: Path, sheet=None):
    import pandas as pd

    if duong_dan.suffix.lower() in (".csv", ".txt"):
        return pd.read_csv(duong_dan, dtype=str)
    if duong_dan.suffix.lower() == ".tsv":
        return pd.read_csv(duong_dan, dtype=str, sep="\t")
    return pd.read_excel(duong_dan, sheet_name=sheet or 0, dtype=str)


def tao_khoa(hang, cot_khoa) -> str:
    """Ghép khoá, chuẩn hoá từng thành phần.

    Chỉ dùng số hóa đơn làm khoá là sai lầm phổ biến: hai nhà cung cấp khác nhau hoàn toàn
    có thể cùng phát hành số '00000123'. Nên khuyến nghị ghép với MST.
    """
    phan = []
    for cot in cot_khoa:
        gt = hang.get(cot)
        s = lam_sach_text(gt, "") or ""
        if "mst" in cot.lower():
            s = chuan_mst(s, s) or s
        # Bỏ số 0 đầu để '00000205' khớp với '205' — hai phần mềm ghi khác nhau
        s = s.lstrip("0") or s
        phan.append(s.upper())
    return "|".join(phan)


def main() -> int:
    p = argparse.ArgumentParser(description="Đối chiếu hai bảng số liệu.")
    p.add_argument("bang_a")
    p.add_argument("bang_b")
    p.add_argument("--khoa", help="Cột khoá dùng cho cả hai bảng, cách nhau bởi dấu phẩy")
    p.add_argument("--khoa-a", help="Cột khoá bảng A (nếu tên khác bảng B)")
    p.add_argument("--khoa-b", help="Cột khoá bảng B")
    p.add_argument("--tien", help="Cột tiền dùng cho cả hai bảng")
    p.add_argument("--tien-a", help="Cột tiền bảng A")
    p.add_argument("--tien-b", help="Cột tiền bảng B")
    p.add_argument("--nguong", type=float, default=1.0,
                   help="Bỏ qua chênh lệch nhỏ hơn/bằng ngưỡng này (mặc định 1 đồng)")
    p.add_argument("--sheet-a")
    p.add_argument("--sheet-b")
    p.add_argument("--ra", help="File kết quả .xlsx")
    args = p.parse_args()

    can_thu_vien("pandas", "openpyxl")
    import pandas as pd

    khoa_a = [c.strip() for c in (args.khoa_a or args.khoa or "").split(",") if c.strip()]
    khoa_b = [c.strip() for c in (args.khoa_b or args.khoa or "").split(",") if c.strip()]
    if not khoa_a or not khoa_b:
        print("Cần --khoa (hoặc --khoa-a và --khoa-b)", file=sys.stderr)
        return 2
    if len(khoa_a) != len(khoa_b):
        print("Số cột khoá hai bảng phải bằng nhau", file=sys.stderr)
        return 2

    tien_a = args.tien_a or args.tien
    tien_b = args.tien_b or args.tien

    a = doc(Path(args.bang_a).expanduser(), args.sheet_a)
    b = doc(Path(args.bang_b).expanduser(), args.sheet_b)
    a.columns = [lam_sach_text(c, "") for c in a.columns]
    b.columns = [lam_sach_text(c, "") for c in b.columns]

    for ten, khung, cot in (("A", a, khoa_a + ([tien_a] if tien_a else [])),
                            ("B", b, khoa_b + ([tien_b] if tien_b else []))):
        thieu = [c for c in cot if c and c not in khung.columns]
        if thieu:
            print(f"Bảng {ten} không có cột: {thieu}\nCác cột hiện có: {list(khung.columns)}",
                  file=sys.stderr)
            return 2

    def gom(khung, cot_khoa, cot_tien):
        muc = {}
        trung = []
        for _, hang in khung.iterrows():
            k = tao_khoa(hang, cot_khoa)
            if not k.strip("|"):
                continue
            t = so_vn(hang.get(cot_tien)) if cot_tien else None
            if k in muc:
                trung.append({"khoa": k, "so_tien": t,
                              "so_tien_lan_dau": muc[k]["tien"]})
                muc[k]["tien"] = (muc[k]["tien"] or Decimal(0)) + (t or Decimal(0))
                muc[k]["so_lan"] += 1
            else:
                muc[k] = {"tien": t, "so_lan": 1, "hang": hang.to_dict()}
        return muc, trung

    mA, trung_a = gom(a, khoa_a, tien_a)
    mB, trung_b = gom(b, khoa_b, tien_b)

    nguong = Decimal(str(args.nguong))
    chi_co_a, chi_co_b, lech, bo_qua = [], [], [], 0

    for k, v in mA.items():
        if k not in mB:
            chi_co_a.append({"khoa": k, "so_tien": v["tien"], "chi_tiet": v["hang"]})
    for k, v in mB.items():
        if k not in mA:
            chi_co_b.append({"khoa": k, "so_tien": v["tien"], "chi_tiet": v["hang"]})

    if tien_a and tien_b:
        for k, v in mA.items():
            if k not in mB:
                continue
            ta, tb = v["tien"], mB[k]["tien"]
            if ta is None or tb is None:
                continue
            d = ta - tb
            if abs(d) <= nguong:
                if d != 0:
                    bo_qua += 1
                continue
            lech.append({
                "khoa": k, "tien_a": ta, "tien_b": tb, "chenh_lech": d,
                "chenh_lech_pct": (float(d / ta * 100) if ta else None),
                "so_lan_a": v["so_lan"], "so_lan_b": mB[k]["so_lan"],
            })
        lech.sort(key=lambda r: -abs(r["chenh_lech"]))

    tong_a = sum((v["tien"] or Decimal(0)) for v in mA.values()) if tien_a else None
    tong_b = sum((v["tien"] or Decimal(0)) for v in mB.values()) if tien_b else None

    # Phép kiểm quan trọng nhất: các chênh lệch tìm được có cộng lại thành chênh lệch tổng không?
    # Nếu không, nghĩa là khoá đối chiếu chưa đúng hoặc còn lỗi chưa bắt được — phải nói ra.
    giai_thich = None
    if tong_a is not None and tong_b is not None:
        chenh_tong = tong_a - tong_b
        da_giai_thich = (
            sum(r["chenh_lech"] for r in lech)
            + sum((r["so_tien"] or Decimal(0)) for r in chi_co_a)
            - sum((r["so_tien"] or Decimal(0)) for r in chi_co_b)
        )
        con_lai = chenh_tong - da_giai_thich
        giai_thich = {
            "chenh_lech_tong": chenh_tong,
            "da_giai_thich_boi_cac_dong_tren": da_giai_thich,
            "chua_giai_thich_duoc": con_lai,
            "ket_luan": (
                "Các chênh lệch tìm được giải thích đủ chênh lệch tổng."
                if abs(con_lai) <= nguong else
                f"CÒN {con_lai:,.0f} đồng CHƯA giải thích được — khoá đối chiếu có thể chưa đúng, "
                "hoặc còn lỗi chưa bắt được. Cần xem lại trước khi tin kết quả."
            ),
        }

    tom_tat = {
        "bang_a": {"tep": args.bang_a, "so_dong": len(a), "so_khoa": len(mA), "tong_tien": tong_a},
        "bang_b": {"tep": args.bang_b, "so_dong": len(b), "so_khoa": len(mB), "tong_tien": tong_b},
        "khop": len(set(mA) & set(mB)),
        "so_chi_co_a": len(chi_co_a),
        "so_chi_co_b": len(chi_co_b),
        "so_lech_tien": len(lech),
        "so_trung_lap_a": len(trung_a),
        "so_trung_lap_b": len(trung_b),
        "bo_qua_duoi_nguong": bo_qua,
        "nguong": float(nguong),
        "doi_chieu_tong": giai_thich,
    }

    ket_qua = {
        "tom_tat": tom_tat,
        "chi_co_a": chi_co_a,
        "chi_co_b": chi_co_b,
        "lech_tien": lech,
        "trung_lap_a": trung_a,
        "trung_lap_b": trung_b,
    }

    if args.ra:
        ra = Path(args.ra).expanduser()
        ra.parent.mkdir(parents=True, exist_ok=True)
        with pd.ExcelWriter(ra, engine="openpyxl") as bo:
            pd.DataFrame([{"Chỉ tiêu": k, "Giá trị": str(v)}
                          for k, v in tom_tat.items()]).to_excel(
                bo, sheet_name="Tong hop", index=False)
            for ten_sheet, du_lieu in (("Chi co bang A", chi_co_a),
                                       ("Chi co bang B", chi_co_b),
                                       ("Lech tien", lech),
                                       ("Trung lap A", trung_a),
                                       ("Trung lap B", trung_b)):
                pd.DataFrame(du_lieu or [{"(không có)": ""}]).to_excel(
                    bo, sheet_name=ten_sheet[:31], index=False)
        tom_tat["tep_ket_qua"] = str(ra)

    if bo_qua:
        canh_bao(f"Đã bỏ qua {bo_qua} dòng có chênh lệch nhỏ hơn ngưỡng {nguong} đồng")
    if trung_a or trung_b:
        canh_bao(f"Có trùng lặp: bảng A {len(trung_a)} dòng, bảng B {len(trung_b)} dòng")
    if giai_thich and "CÒN" in giai_thich["ket_luan"]:
        canh_bao(giai_thich["ket_luan"])

    in_json(ket_qua)
    return 0


if __name__ == "__main__":
    sys.exit(main())
