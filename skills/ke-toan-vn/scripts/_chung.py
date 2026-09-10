"""Tiện ích dùng chung cho các script của skill ke-toan-vn."""

from __future__ import annotations

import json
import os
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


def in_json(du_lieu) -> None:
    """In JSON ra stdout để model đọc được."""
    json.dump(du_lieu, sys.stdout, ensure_ascii=False, indent=2, default=str)
    sys.stdout.write("\n")


def canh_bao(thong_diep: str) -> None:
    """Ghi cảnh báo ra stderr, tách khỏi kết quả JSON ở stdout."""
    print(f"⚠️  {thong_diep}", file=sys.stderr)


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
