#!/usr/bin/env python3
"""Sinh gói kiểm toán mẫu (dữ liệu tổng hợp) vào docs/audit/examples/goi-kiem-toan-mau/.

    python evals/tao_goi_kiem_toan_mau.py

Các bước làm giống một lần dùng thật: chạy một quy trình lọc, người kiểm tra ghi nhận đã xem,
xuất gói, rồi kiểm độc lập gói đó với file nguồn. Bộ nhớ nằm trong thư mục tạm. Gói xuất ra
không chứa đường dẫn máy hay nội dung dòng dữ liệu. run_id và giờ đổi mỗi lần sinh, nên chỉ
nên sinh lại khi định dạng gói đổi.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
SCRIPTS = GOC / "skills" / "ke-toan-vn" / "scripts"
RA = GOC / "docs" / "audit" / "examples" / "goi-kiem-toan-mau"
QUY_TRINH = """loai = "loc"
mo_ta = "Lọc bản kết xuất doanh thu mẫu: bỏ dòng nhóm Máu"
[nguon]
cot_tien = "SOTIEN"
[ket_qua]
ra = "LOC-{ten_file}.xlsx"
[[quy_tac]]
ma = "1"
mo_ta = "nhóm Máu tính ở báo cáo riêng"
khi = { NHOM = { bang = ["Máu"] } }
"""


def chay(*lenh) -> dict:
    kq = subprocess.run([sys.executable, *map(str, lenh)], capture_output=True, text=True)
    if kq.returncode not in (0, 2):
        raise SystemExit(kq.stderr[-2000:])
    return json.loads(kq.stdout)


def main() -> None:
    import openpyxl

    tmp = Path(tempfile.mkdtemp(prefix="kt-goi-mau-"))
    home = tmp / "bo-nho"
    (home / "quy-trinh").mkdir(parents=True)
    (home / "quy-trinh" / "loc-mau.toml").write_text(QUY_TRINH, encoding="utf-8")
    shutil.rmtree(RA, ignore_errors=True)
    (RA / "nguon").mkdir(parents=True)
    nguon = RA / "nguon" / "DT-MAU-09.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    for r in [["QUYENSO", "NHOM", "TENDV", "SOTIEN"], ["HD01", "Thuốc", "Dịch vụ mẫu 1", 100000],
              ["HD01", "Máu", "Dịch vụ mẫu 2", 50000], ["HD02", "Khám", "Dịch vụ mẫu 3", 30000]]:
        ws.append(r)
    wb.save(nguon)
    shutil.copy(home / "quy-trinh" / "loc-mau.toml", RA / "loc-mau.toml")

    d = chay(SCRIPTS / "quy_trinh.py", "--home", home, "chay", "loc-mau", nguon,
             "--ra-thu-muc", tmp / "ket-qua", "--nguoi-lap", "Người lập mẫu")
    run = d["run_id"]
    duyet = chay(SCRIPTS / "ho_so_kiem_toan.py", "--home", home, "duyet", run,
                 "--vai-tro", "nguoi-kiem-tra", "--quyet-dinh", "dong-y",
                 "--nguoi", "Người kiểm tra mẫu", "--ghi-chu", "Đã đối chiếu tổng với bản kết xuất")
    chay(SCRIPTS / "ho_so_kiem_toan.py", "--home", home, "xuat", run, "--ra", RA)
    kiem = chay(SCRIPTS / "ho_so_kiem_toan.py", "kiem-goi", RA / f"{run}.json",
                "--thu-muc-tep", RA / "nguon")
    (RA / "KET-QUA-KIEM-DOC-LAP.json").write_text(
        json.dumps({"lenh": f"ho_so_kiem_toan.py kiem-goi {run}.json --thu-muc-tep nguon",
                    "ket_qua": kiem, "trang_thai_duyet_luc_xuat": duyet["trang_thai_duyet"]},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.rmtree(tmp, ignore_errors=True)
    print(json.dumps({"run_id": run, "kiem_doc_lap": kiem}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
