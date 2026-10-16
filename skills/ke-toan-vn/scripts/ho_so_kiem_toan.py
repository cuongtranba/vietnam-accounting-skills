#!/usr/bin/env python3
"""Hồ sơ kiểm toán của các lần chạy: xem, kiểm toàn vẹn, phát lại, ghi nhận duyệt, xuất gói.

    ho_so_kiem_toan.py danh-sach
    ho_so_kiem_toan.py xem <run_id>
    ho_so_kiem_toan.py kiem <run_id>             # nguồn/quy tắc/kết quả còn đúng mã băm?
    ho_so_kiem_toan.py kiem-so-cai               # sổ cái còn nối chuỗi?
    ho_so_kiem_toan.py phat-lai <run_id>         # chạy lại (xem trước), so kết quả nghiệp vụ
    ho_so_kiem_toan.py duyet <run_id> --vai-tro nguoi-phe-duyet --quyet-dinh dong-y --nguoi "..."
    ho_so_kiem_toan.py xuat <run_id> --ra <thư mục>    # gói JSON + Markdown, không kèm dữ liệu dòng
    ho_so_kiem_toan.py kiem-goi <goi.json> --thu-muc-tep <thư mục chứa file nguồn>

Hồ sơ nằm ở <bộ nhớ đơn vị>/ho-so/ (xem _ho_so.py). Lần chạy được ghi bởi quy_trinh.py chay và
doc_hoa_don.py --ghi-ho-so.

DUYỆT không phải chữ ký. Công cụ không có cơ chế xác thực danh tính, nên mọi lần duyệt ghi
`UNVERIFIED_HUMAN_REVIEW` và trạng thái tối đa là `da_xem_chua_xac_thuc` — không bao giờ
`approved`. Lần duyệt gắn với mã băm của hồ sơ (tức của nguồn, quy tắc, kết quả): nội dung đổi
sau đó thì lần duyệt `vo_hieu`. Lần chạy needs_review chỉ ghi nhận đồng ý khi có --ngoai-le
nêu lý do. Bật `[phan_quyen] tach_nhiem = true` trong <bộ nhớ đơn vị>/don-vi.toml thì người lập
không tự duyệt được, và một người không giữ hai vai.

Mã thoát: 0 bình thường / toàn vẹn / phát lại khớp; 2 bị cổng kiểm soát từ chối, hoặc phát hiện
thay đổi; 1 lỗi đầu vào (không có lần chạy, sai tham số).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _ho_so as H  # noqa: E402
from _chung import home_don_vi, in_json, tim_home  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent


class TuChoi(Exception):
    """Cổng kiểm soát từ chối — mã thoát 2."""


def _chinh_sach(home_dv: Path) -> dict:
    p = home_dv / "don-vi.toml"
    if not p.exists():
        return {}
    import tomllib

    with p.open("rb") as f:
        return tomllib.load(f)


def _cung_nguoi(a: str | None, b: str | None) -> bool:
    if not a or not b:
        return False
    return unicodedata.normalize("NFC", a).casefold().split() == \
        unicodedata.normalize("NFC", b).casefold().split()


def lenh_duyet(home_dv: Path, don_vi: str, a) -> dict:
    hs = H.doc_ho_so(home_dv, a.run_id)
    if hs.get("don_vi") != don_vi:
        raise TuChoi(f"Lần chạy thuộc đơn vị {hs.get('don_vi')!r}, không phải {don_vi!r}")
    kiem = H.kiem_lan_chay(home_dv, a.run_id)
    if not kiem["toan_ven"]:
        raise TuChoi("Nguồn, quy tắc hoặc kết quả đã đổi so với hồ sơ — không duyệt được nội "
                     f"dung này. Chi tiết: {kiem['thay_doi'] or kiem['khong_tim_thay']}")
    if a.quyet_dinh == "dong-y" and hs.get("trang_thai_ket_qua") != "draft" and not a.ngoai_le:
        raise TuChoi(f"Lần chạy ở trạng thái {hs.get('trang_thai_ket_qua')} "
                     f"({'; '.join(hs.get('ly_do_trang_thai', [])) or 'xem hồ sơ'}). Chỉ ghi nhận "
                     "đồng ý khi có --ngoai-le nêu lý do chấp nhận ngoại lệ.")
    if _chinh_sach(home_dv).get("phan_quyen", {}).get("tach_nhiem"):
        lap = (hs.get("nguoi_lap") or {}).get("ten")
        if _cung_nguoi(lap, a.nguoi):
            raise TuChoi("Tách nhiệm đang bật: người lập không tự duyệt lần chạy của mình")
        for p in H.cac_phe_duyet(home_dv, a.run_id):
            if p.get("vai_tro") != a.vai_tro and _cung_nguoi((p.get("nguoi") or {}).get("ten"),
                                                            a.nguoi):
                raise TuChoi(f"Tách nhiệm đang bật: {a.nguoi} đã giữ vai {p.get('vai_tro')}")
    xac_thuc = H.danh_tinh_host()
    nguoi = ({**xac_thuc, "xac_thuc": "VERIFIED"} if xac_thuc else H.nguoi(a.nguoi))
    muc = H.them_so_cai(home_dv, {
        "loai": "duyet", "run_id": a.run_id, "ho_so_sha256": H.bam_ho_so(hs),
        "vai_tro": a.vai_tro, "quyet_dinh": a.quyet_dinh, "nguoi": nguoi,
        "ghi_chu": a.ghi_chu, "ngoai_le": a.ngoai_le, "don_vi": don_vi})
    return {"da_ghi": True, "run_id": a.run_id, "vai_tro": a.vai_tro, "quyet_dinh": a.quyet_dinh,
            "xac_thuc": nguoi["xac_thuc"], "ngoai_le": a.ngoai_le,
            "trang_thai_duyet": H.trang_thai_duyet(home_dv, a.run_id, True),
            "so_cai_stt": muc["stt"],
            "luu_y": "Danh tính người duyệt là tự khai — đây là ghi nhận việc xem xét, không phải "
                     "chữ ký số hay phê duyệt đã xác thực."}


def lenh_phat_lai(home_dv: Path, run_id: str) -> dict:
    hs = H.doc_ho_so(home_dv, run_id)
    pl = hs.get("_phat_lai")
    if not pl:
        raise LookupError("Hồ sơ không có thông tin phát lại")
    mat = [x["nhan"] for x in hs.get("dau_vao", [])
           if not Path(x.get("_duong_dan") or "").is_file()]
    if mat:
        return {"run_id": run_id, "tai_lap_duoc": False, "ket_qua_khop": False,
                "ly_do": f"Thiếu file nguồn: {mat}"}
    nguon_doi = [x["nhan"] for x in hs.get("dau_vao", [])
                 if H.bam_tep(Path(x["_duong_dan"])) != x["sha256"]]
    qt = hs.get("quy_tac") or {}
    quy_tac_doi = bool(qt.get("_duong_dan")) and (
        not Path(qt["_duong_dan"]).is_file() or H.bam_tep(Path(qt["_duong_dan"])) != qt["sha256"])
    dm = hs.get("danh_muc") or {}
    if dm.get("_duong_dan"):
        p = Path(dm["_duong_dan"])
        quy_tac_doi = quy_tac_doi or (H.bam_tep(p) if p.is_file() else None) != dm.get("sha256")
    kq = subprocess.run([sys.executable, str(SCRIPTS / pl["script"]), *pl["args"]],
                        capture_output=True, text=True)
    try:
        ra = json.loads(kq.stdout)
    except json.JSONDecodeError:
        return {"run_id": run_id, "tai_lap_duoc": False, "ket_qua_khop": False,
                "ly_do": kq.stderr[-500:]}
    phan = ra.get(pl["truong"]) if pl.get("truong") else None
    bam = H.bam_ket_qua(phan) if phan is not None else None
    return {"run_id": run_id, "tai_lap_duoc": phan is not None,
            "ket_qua_khop": bam == hs.get("ket_qua_sha256"),
            "ket_qua_sha256_ho_so": hs.get("ket_qua_sha256"), "ket_qua_sha256_phat_lai": bam,
            "nguon_da_doi": nguon_doi, "quy_tac_da_doi": quy_tac_doi,
            "trang_thai_lan_phat_lai": ra.get("trang_thai"),
            "luu_y": "Phát lại chạy ở chế độ xem trước: không ghi file, lịch sử hay hồ sơ nào."}


def _markdown(goi: dict) -> str:
    hs = goi["ho_so"]
    d = [f"# Gói kiểm toán — {hs['run_id']}", "", f"> {H.MIEN_TRU}", "",
         f"- Đơn vị: `{hs.get('don_vi')}`  Pháp nhân: `{hs.get('phap_nhan')}`",
         f"- Công cụ: `{hs.get('cong_cu')}` — {hs.get('quy_trinh') or ''}",
         f"- Kỳ: `{hs.get('ky')}`  Thời gian: `{hs.get('thoi_gian')}`",
         f"- Trạng thái kết quả: **{hs.get('trang_thai_ket_qua')}**  "
         f"Trạng thái duyệt: **{goi['kiem_tai_luc_xuat']['trang_thai_duyet']}**",
         f"- Mã băm hồ sơ (phần công khai): `{goi['ho_so_sha256']}`",
         f"- Mã băm kết quả nghiệp vụ: `{hs.get('ket_qua_sha256')}`", "",
         "## Nguồn", "", "| Nhãn | SHA-256 |", "|---|---|"]
    d += [f"| {x['nhan']} | `{x['sha256']}` |" for x in hs.get("dau_vao", [])]
    d += ["", "## Quy tắc", "", f"- {(hs.get('quy_tac') or {}).get('nhan')}: "
          f"`{(hs.get('quy_tac') or {}).get('sha256')}`", "", "## Kết quả", "",
          "| Nhãn | SHA-256 |", "|---|---|"]
    d += [f"| {x['nhan']} | `{x['sha256']}` |" for x in hs.get("dau_ra", [])]
    d += ["", "## Ngoại lệ", ""] + [f"- {x}" for x in hs.get("ngoai_le", [])] + \
         ["", "## Duyệt", ""]
    d += [f"- {p['thoi_gian']} — {p['vai_tro']} {p['quyet_dinh']} bởi "
          f"{(p.get('nguoi') or {}).get('ten')} ({(p.get('nguoi') or {}).get('xac_thuc')})"
          + (f" — ngoại lệ: {p['ngoai_le']}" if p.get("ngoai_le") else "")
          for p in goi["phe_duyet"]] or ["- (chưa có)"]
    d += ["", "## Kiểm lại độc lập", "",
          "`ho_so_kiem_toan.py kiem-goi <file .json này> --thu-muc-tep <thư mục chứa file nguồn>`",
          ""]
    return "\n".join(d)


def lenh_xuat(home_dv: Path, run_id: str, ra: str | None) -> dict:
    hs = H.doc_ho_so(home_dv, run_id)
    so_cai = H.doc_so_cai(home_dv)
    goi = {
        "loai": "goi_kiem_toan", "schema_version": H.SCHEMA, "mien_tru": H.MIEN_TRU,
        "ho_so": H.cong_khai(hs), "ho_so_sha256": H.bam_ho_so(hs),
        "muc_so_cai": [m for m in so_cai if m.get("run_id") == run_id],
        "phe_duyet": H.cac_phe_duyet(home_dv, run_id),
        "kiem_tai_luc_xuat": {k: v for k, v in H.kiem_lan_chay(home_dv, run_id).items()
                              if k in ("toan_ven", "ho_so_khop_so_cai", "so_cai_hop_le",
                                       "thay_doi", "khong_tim_thay", "trang_thai_duyet")},
        "bam_dong_cuoi_so_cai": H.kiem_so_cai(home_dv)["bam_dong_cuoi"],
        "xuat_luc": H.bay_gio(),
    }
    if ra:
        d = Path(ra).expanduser()
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{run_id}.json").write_text(json.dumps(goi, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
        (d / f"{run_id}.md").write_text(_markdown(goi), encoding="utf-8")
        return {"da_ghi": [str(d / f"{run_id}.json"), str(d / f"{run_id}.md")],
                "trang_thai_duyet": goi["kiem_tai_luc_xuat"]["trang_thai_duyet"]}
    return goi


def lenh_kiem_goi(goi_tep: str, thu_muc_tep: str | None) -> dict:
    """Kiểm một gói đã xuất mà không cần bộ nhớ gốc: hồ sơ khớp mã băm ghi trong sổ cái, mục
    sổ cái khớp mã băm của chính nó, file nguồn (nếu đưa thư mục) khớp mã băm theo nhãn."""
    goi = json.loads(Path(goi_tep).read_text(encoding="utf-8"))
    bam = H.bam_bytes(H.chuan_json(goi["ho_so"]))
    muc = next((m for m in goi["muc_so_cai"] if m.get("loai") == "lan_chay"), {})
    muc_hop_le = all(H.bam_bytes(H.chuan_json({k: v for k, v in m.items() if k != "bam"}))
                     == m.get("bam") for m in goi["muc_so_cai"])
    khop = bam == goi["ho_so_sha256"] == muc.get("ho_so_sha256")
    kq = {"ho_so_khop": khop and muc_hop_le, "dau_vao_khop": None, "chi_tiet": []}
    if thu_muc_tep:
        d = Path(thu_muc_tep)
        for x in goi["ho_so"].get("dau_vao", []):
            p = d / x["nhan"]
            ok = p.is_file() and H.bam_tep(p) == x["sha256"]
            kq["chi_tiet"].append({"nhan": x["nhan"], "khop": ok,
                                   "co_file": p.is_file()})
        kq["dau_vao_khop"] = all(c["khop"] for c in kq["chi_tiet"])
    return kq


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--home", help="Thư mục bộ nhớ (mặc định: tự tìm .ke-toan-vn)")
    p.add_argument("--don-vi", help="Mã đơn vị (mặc định KE_TOAN_VN_DON_VI, hoặc mac-dinh)")
    sub = p.add_subparsers(dest="lenh", required=True)
    sub.add_parser("danh-sach")
    for ten in ("xem", "kiem", "phat-lai"):
        sub.add_parser(ten).add_argument("run_id")
    sub.add_parser("kiem-so-cai")
    s = sub.add_parser("duyet")
    s.add_argument("run_id")
    s.add_argument("--vai-tro", required=True, choices=["nguoi-kiem-tra", "nguoi-phe-duyet"])
    s.add_argument("--quyet-dinh", required=True, choices=["dong-y", "tu-choi"])
    s.add_argument("--nguoi", required=True, help="Tên người xem/duyệt (tự khai)")
    s.add_argument("--ghi-chu")
    s.add_argument("--ngoai-le", help="Lý do chấp nhận ngoại lệ khi lần chạy needs_review")
    s = sub.add_parser("xuat")
    s.add_argument("run_id")
    s.add_argument("--ra", help="Thư mục ghi gói (mặc định in JSON ra stdout)")
    s = sub.add_parser("kiem-goi")
    s.add_argument("goi")
    s.add_argument("--thu-muc-tep")
    a = p.parse_args()

    try:
        if a.lenh == "kiem-goi":
            kq = lenh_kiem_goi(a.goi, a.thu_muc_tep)
            in_json(kq)
            return 0 if kq["ho_so_khop"] and kq["dau_vao_khop"] is not False else 2
        home = Path(a.home).expanduser() if a.home else tim_home()
        home_dv, don_vi = home_don_vi(home, a.don_vi)
        if a.lenh == "danh-sach":
            in_json({"don_vi": don_vi, "lan_chay": [
                {"run_id": m["run_id"], "thoi_gian": m["thoi_gian"]}
                for m in H.doc_so_cai(home_dv) if m.get("loai") == "lan_chay"]})
        elif a.lenh == "xem":
            in_json(H.cong_khai(H.doc_ho_so(home_dv, a.run_id)))
        elif a.lenh == "kiem":
            kq = H.kiem_lan_chay(home_dv, a.run_id)
            in_json(kq)
            return 0 if kq["toan_ven"] else 2
        elif a.lenh == "kiem-so-cai":
            kq = H.kiem_so_cai(home_dv)
            in_json(kq)
            return 0 if kq["hop_le"] else 2
        elif a.lenh == "phat-lai":
            kq = lenh_phat_lai(home_dv, a.run_id)
            in_json(kq)
            return 0 if kq["ket_qua_khop"] and not kq.get("quy_tac_da_doi") else 2
        elif a.lenh == "duyet":
            in_json(lenh_duyet(home_dv, don_vi, a))
        elif a.lenh == "xuat":
            in_json(lenh_xuat(home_dv, a.run_id, a.ra))
    except TuChoi as e:
        in_json({"trang_thai": "tu_choi", "thong_diep": str(e)})
        return 2
    except (LookupError, ValueError, OSError) as e:
        in_json({"trang_thai": "loi", "thong_diep": str(e)})
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
