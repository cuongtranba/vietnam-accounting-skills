"""Tiện ích dùng chung cho các script của skill ke-toan-vn."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


def tim_home() -> Path:
    """Tìm thư mục bộ nhớ .ke-toan-vn.

    Thứ tự: biến môi trường KE_TOAN_VN_HOME -> thư mục cha đầu tiên (tính từ vị trí
    thật của script) có chứa .ke-toan-vn/ -> ~/.ke-toan-vn.

    Phải resolve() vì Codex gọi skill qua symlink; đường dẫn tương đối sẽ trỏ sai chỗ.
    Không hardcode số cấp thư mục — bố cục đổi là vỡ.
    """
    bien = os.environ.get("KE_TOAN_VN_HOME")
    if bien:
        return Path(bien).expanduser()

    for cha in Path(__file__).resolve().parents:
        ung_vien = cha / ".ke-toan-vn"
        if ung_vien.is_dir():
            return ung_vien

    return Path.home() / ".ke-toan-vn"


MAC_DINH_DON_VI = "mac-dinh"


def home_don_vi(home: Path, don_vi: str | None = None) -> tuple[Path, str]:
    """Thư mục bộ nhớ RIÊNG của một đơn vị (khách hàng, pháp nhân) và mã của nó.

    Quy trình, danh mục, quy ước và hồ sơ kiểm toán là của từng đơn vị: cùng mã "KHS" ở hai
    bệnh viện có thể là hai khoa khác nhau. Có mã đơn vị (--don-vi hoặc KE_TOAN_VN_DON_VI) thì
    mọi thứ đó nằm ở `<bộ nhớ>/don-vi/<mã>/` và không đơn vị nào thấy của đơn vị khác. Không có
    mã thì dùng thẳng `<bộ nhớ>/` như trước (mã "mac-dinh"). Ghi chú pháp lý thì dùng chung.

    Mã chỉ gồm chữ thường không dấu, số và '-': chặn '../' thoát ra ngoài thư mục bộ nhớ.
    """
    don_vi = don_vi or os.environ.get("KE_TOAN_VN_DON_VI") or None
    if don_vi is None or don_vi == MAC_DINH_DON_VI:
        return home, MAC_DINH_DON_VI
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,62}", don_vi):
        raise ValueError(f"Mã đơn vị {don_vi!r} không hợp lệ — chỉ dùng a-z, 0-9 và '-'")
    return home / "don-vi" / don_vi, don_vi


def in_json(du_lieu) -> None:
    """In JSON ra stdout để model đọc được."""
    json.dump(du_lieu, sys.stdout, ensure_ascii=False, indent=2, default=str)
    sys.stdout.write("\n")


def canh_bao(thong_diep: str) -> None:
    """Ghi cảnh báo ra stderr, tách khỏi kết quả JSON ở stdout."""
    print(f"⚠️  {thong_diep}", file=sys.stderr)


def o_an_toan(v):
    """Giá trị đưa ra CSV/Excel: chuỗi mở đầu bằng = + - @ (hoặc tab, xuống dòng) được thêm dấu
    nháy đơn để bảng tính hiểu là chữ, không phải công thức. Dữ liệu đến từ hóa đơn/bản kết xuất
    của bên ngoài; một tên người bán "=HYPERLINK(...)" không được biến thành công thức chạy được."""
    if isinstance(v, str) and v[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + v
    return v


def can_thu_vien(*ten_module: str) -> None:
    """Kiểm thư viện trước khi chạy, báo lỗi tử tế bằng tiếng Việt thay vì ImportError."""
    import importlib

    thieu = []
    for ten in ten_module:
        try:
            importlib.import_module(ten)
        except ImportError:
            thieu.append(ten)
    if thieu:
        print(
            f"Thiếu thư viện: {', '.join(thieu)}\n"
            f"Chạy:  bash {Path(__file__).resolve().parent / 'bootstrap.sh'}\n"
            f"rồi chạy lại bằng python trong venv:\n"
            f'  PY=$(bash {Path(__file__).resolve().parent / "bootstrap.sh"} --duong-dan-python)\n'
            f'  "$PY" {sys.argv[0]} ...',
            file=sys.stderr,
        )
        sys.exit(3)
