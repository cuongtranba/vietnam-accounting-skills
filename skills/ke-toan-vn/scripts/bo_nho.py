#!/usr/bin/env python3
"""Bộ nhớ cục bộ của skill ke-toan-vn.

    bo_nho.py tra "nguong doanh thu ho kinh doanh"
    bo_nho.py ghi --loai phap-ly --chu-de "..." --tep noi_dung.md \
              --van-ban "Luật 149/2025/QH15" --hieu-luc-tu 2026-01-01 \
              --nguon https://vanban.chinhphu.vn/... --do-tin-cay cao
    bo_nho.py ghi --loai quy-uoc --chu-de "cot-excel" --noi-dung "..."
    bo_nho.py kiem-han
    bo_nho.py nhat-ky "Đã lập bảng kê mua vào quý 3"
    bo_nho.py muc-luc

Hai loại kiến thức, xử lý khác nhau:

  phap-ly/  cache quy định — CÓ hạn dùng. Một cache luật không hết hạn thì tệ hơn là
            không có cache: nó biến câu trả lời sai thành câu trả lời sai có vẻ đáng tin,
            được lặp lại tự tin qua nhiều tháng.

  quy-uoc/  quy ước riêng của người dùng — KHÔNG hết hạn. Chỉ người dùng mới đổi được.
            Đây mới là phần 'học' thật sự của skill.

Không dùng thư viện ngoài — chạy được bằng python hệ thống, nên bộ nhớ luôn tra được
kể cả khi chưa chạy bootstrap.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _chung import in_json, tim_home  # noqa: E402

# TTL theo mức độ biến động. Không dùng một hạn chung — các mảng biến động rất khác nhau.
TTL_NGAY = {
    "dau-thau": 45,    # NĐ 214/2025 mới hiệu lực 8/2025 và ĐÃ CÓ dự thảo sửa
    "thue": 60,        # thuế suất/ngưỡng đổi 3 lần trong 18 tháng
    "hoa-don": 90,     # đổi theo nghị định
    "tai-khoan": 365,  # TT 200/TT 133 ổn định từ 2014
    "khac": 60,
}

TU_KHOA_CHU_DE = {
    "dau-thau": ["dau thau", "thau", "hsdt", "hsmt", "nha thau", "goi thau", "214/2025",
                 "sai lech", "gia danh gia", "chi dinh thau"],
    "thue": ["thue", "gtgt", "tndn", "tncn", "to khai", "nguong", "khau tru", "thue suat",
             "quyet toan", "48/2024", "149/2025", "181/2025"],
    "hoa-don": ["hoa don", "123/2020", "70/2025", "78/2021", "1450", "xml", "chung tu"],
    "tai-khoan": ["tai khoan", "tt 200", "200/2014", "133/2016", "che do ke toan", "so sach"],
}


def khong_dau(s: str) -> str:
    """Bỏ dấu tiếng Việt để so khớp — người dùng có thể gõ có dấu hoặc không."""
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").strip()


def doan_nhom(chu_de: str) -> str:
    """Đoán nhóm chủ đề để chọn TTL phù hợp."""
    can = khong_dau(chu_de)
    for nhom, tu_khoa in TU_KHOA_CHU_DE.items():
        if any(tk in can for tk in tu_khoa):
            return nhom
    return "khac"


def slug(s: str) -> str:
    s = khong_dau(s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80] or "ghi-chu"


# --- Đọc/ghi frontmatter -----------------------------------------------------

def doc_ghi_chu(duong_dan: Path) -> dict:
    """Đọc file markdown có frontmatter YAML đơn giản (không cần thư viện yaml)."""
    van_ban = duong_dan.read_text(encoding="utf-8")
    meta, than = {}, van_ban

    if van_ban.startswith("---"):
        phan = van_ban.split("---", 2)
        if len(phan) >= 3:
            than = phan[2].lstrip("\n")
            for dong in phan[1].splitlines():
                dong = dong.rstrip()
                if not dong.strip() or dong.lstrip().startswith("#"):
                    continue
                if dong.startswith("  - ") or dong.startswith("- "):
                    khoa = meta.get("_khoa_cuoi")
                    if khoa:
                        meta.setdefault(khoa, [])
                        if not isinstance(meta[khoa], list):
                            meta[khoa] = []
                        meta[khoa].append(dong.split("-", 1)[1].strip())
                    continue
                if ":" in dong:
                    khoa, _, gt = dong.partition(":")
                    khoa, gt = khoa.strip(), gt.strip()
                    meta["_khoa_cuoi"] = khoa
                    if gt in ("", "null", "~"):
                        meta[khoa] = None
                    elif gt.startswith("["):
                        try:
                            meta[khoa] = json.loads(gt.replace("'", '"'))
                        except json.JSONDecodeError:
                            meta[khoa] = gt
                    else:
                        meta[khoa] = gt.strip("\"'")
    meta.pop("_khoa_cuoi", None)
    meta["_tep"] = str(duong_dan)
    return {"meta": meta, "noi_dung": than}


def _yaml_gia_tri(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, list):
        return "\n" + "\n".join(f"  - {x}" for x in v) if v else "[]"
    return str(v)


def ghi_ghi_chu(duong_dan: Path, meta: dict, noi_dung: str) -> None:
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    dong = ["---"]
    for k, v in meta.items():
        if k.startswith("_"):
            continue
        dong.append(f"{k}: {_yaml_gia_tri(v)}")
    dong.append("---")
    dong.append("")
    dong.append(noi_dung.rstrip())
    dong.append("")
    duong_dan.write_text("\n".join(dong), encoding="utf-8")


def _ngay(gt):
    if not gt:
        return None
    try:
        return datetime.strptime(str(gt)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def tinh_trang_ghi_chu(meta: dict) -> tuple[str, str]:
    """Trả về (tình trạng, giải thích)."""
    if meta.get("thay_the_boi"):
        return "het_hieu_luc", f"Đã bị thay bởi {meta['thay_the_boi']}"
    het = _ngay(meta.get("het_han"))
    if het is None:
        return "khong_han", "Không có hạn dùng (quy ước riêng)"
    hom_nay = date.today()
    if het < hom_nay:
        return "qua_han", f"Quá hạn {(hom_nay - het).days} ngày (hết hạn {het})"
    return "con_han", f"Còn {(het - hom_nay).days} ngày (hết hạn {het})"


# --- Lệnh --------------------------------------------------------------------

def lenh_tra(home: Path, tu_khoa: str) -> dict:
    can = khong_dau(tu_khoa)
    tu = [t for t in can.split() if len(t) > 2]
    tim_thay = []

    for thu_muc in ("phap-ly", "quy-uoc"):
        goc = home / thu_muc
        if not goc.is_dir():
            continue
        for tep in sorted(goc.glob("*.md")):
            # Bỏ qua bản lưu trữ .cu-YYYY-MM-DD.md. Chúng giữ lại để đối chiếu lịch sử,
            # nhưng trả chúng về trong kết quả tra cứu thì người đọc có thể lấy nhầm con số
            # ĐÃ BỊ THAY — đúng cái sai mà cả bộ nhớ này sinh ra để chống.
            if ".cu-" in tep.name:
                continue
            gc = doc_ghi_chu(tep)
            noi_dung_can = khong_dau(
                f"{gc['meta'].get('chu_de', '')} {tep.stem} {gc['noi_dung'][:2000]}"
            )
            diem = sum(1 for t in tu if t in noi_dung_can)
            if diem:
                tt, giai_thich = tinh_trang_ghi_chu(gc["meta"])
                tim_thay.append({
                    "loai": thu_muc,
                    "tep": str(tep),
                    "chu_de": gc["meta"].get("chu_de", tep.stem),
                    "tinh_trang": tt,
                    "giai_thich": giai_thich,
                    "van_ban": gc["meta"].get("van_ban"),
                    "hieu_luc_tu": gc["meta"].get("hieu_luc_tu"),
                    "het_han": gc["meta"].get("het_han"),
                    "thay_the_boi": gc["meta"].get("thay_the_boi"),
                    "do_tin_cay": gc["meta"].get("do_tin_cay"),
                    "nguon": gc["meta"].get("nguon"),
                    "diem_khop": diem,
                    "noi_dung": gc["noi_dung"].strip(),
                })

    tim_thay.sort(key=lambda g: -g["diem_khop"])
    dung_duoc = [g for g in tim_thay if g["tinh_trang"] in ("con_han", "khong_han")]
    nhom = doan_nhom(tu_khoa)

    if dung_duoc:
        loi_khuyen = "Có ghi chú còn dùng được — đọc trường noi_dung. Không cần tra web."
    elif tim_thay:
        loi_khuyen = ("Có ghi chú nhưng ĐÃ QUÁ HẠN hoặc HẾT HIỆU LỰC. Phải tra web lại. "
                      "Giữ nội dung cũ để so sánh 'trước đây là X, nay là Y'.")
    else:
        loi_khuyen = "Chưa có ghi chú nào. Tra web rồi ghi lại bằng lệnh 'ghi'."

    return {
        "tu_khoa": tu_khoa,
        "nhom_chu_de": nhom,
        "ttl_ngay": TTL_NGAY.get(nhom, TTL_NGAY["khac"]),
        "can_tra_web": not dung_duoc,
        "loi_khuyen": loi_khuyen,
        "so_ghi_chu": len(tim_thay),
        "ghi_chu": tim_thay[:5],
    }


def lenh_ghi(home: Path, args) -> dict:
    noi_dung = args.noi_dung or ""
    if args.tep:
        noi_dung = Path(args.tep).expanduser().read_text(encoding="utf-8")
    if not noi_dung.strip():
        raise SystemExit("Cần --noi-dung hoặc --tep")

    hom_nay = date.today()
    duong_dan = home / args.loai / f"{slug(args.chu_de)}.md"

    if args.loai == "phap-ly":
        nhom = args.nhom or doan_nhom(args.chu_de)
        ttl = args.ttl if args.ttl else TTL_NGAY.get(nhom, TTL_NGAY["khac"])
        meta = {
            "chu_de": args.chu_de,
            "nhom": nhom,
            "van_ban": args.van_ban or [],
            "hieu_luc_tu": args.hieu_luc_tu,
            "tra_cuu_ngay": hom_nay.isoformat(),
            "het_han": (hom_nay + timedelta(days=ttl)).isoformat(),
            "thay_the_boi": args.thay_the_boi,
            "tinh_trang": "het_hieu_luc" if args.thay_the_boi else "con_hieu_luc",
            "nguon": args.nguon or [],
            "do_tin_cay": args.do_tin_cay,
        }
        if not args.nguon:
            print("⚠️  Ghi chú pháp lý không có nguồn — nên có ít nhất một link .gov.vn",
                  file=sys.stderr)
    else:
        meta = {
            "chu_de": args.chu_de,
            "cap_nhat_ngay": hom_nay.isoformat(),
            "nguon_quan_sat": args.nguon_quan_sat or "người dùng cung cấp",
        }

    # Không ghi đè im lặng: giữ bản cũ lại để người dùng đối chiếu
    # ("trước đây là 500 triệu, nay là 1 tỷ" hữu ích khi rà soát kỳ trước).
    luu = None
    if duong_dan.exists():
        cu = doc_ghi_chu(duong_dan)
        luu = duong_dan.with_name(f"{duong_dan.stem}.cu-{hom_nay.isoformat()}.md")
        ghi_ghi_chu(luu, cu["meta"], cu["noi_dung"])

    ghi_ghi_chu(duong_dan, meta, noi_dung)
    lenh_muc_luc(home)

    return {
        "da_ghi": str(duong_dan),
        "loai": args.loai,
        "het_han": meta.get("het_han"),
        "ban_cu_luu_tai": str(luu) if luu else None,
        "nhac": "Hãy nói cho người dùng biết bạn vừa ghi nhớ điều gì — một dòng là đủ.",
    }


def lenh_kiem_han(home: Path) -> dict:
    van_de = []
    for tep in sorted((home / "phap-ly").glob("*.md")) if (home / "phap-ly").is_dir() else []:
        if ".cu-" in tep.name:
            continue
        gc = doc_ghi_chu(tep)
        tt, giai_thich = tinh_trang_ghi_chu(gc["meta"])
        if tt in ("qua_han", "het_hieu_luc"):
            van_de.append({
                "tep": str(tep),
                "chu_de": gc["meta"].get("chu_de", tep.stem),
                "tinh_trang": tt,
                "giai_thich": giai_thich,
                "van_ban": gc["meta"].get("van_ban"),
            })
    return {
        "so_van_de": len(van_de),
        "can_tra_lai": van_de,
        "loi_khuyen": ("Tra web lại các chủ đề này trước khi dùng."
                       if van_de else "Mọi ghi chú pháp lý đều còn hạn."),
    }


def lenh_nhat_ky(home: Path, noi_dung: str) -> dict:
    tep = home / "nhat-ky.md"
    cu = tep.read_text(encoding="utf-8") if tep.exists() else "# Nhật ký\n\nMới nhất lên đầu.\n"
    dau = "# Nhật ký\n\nMới nhất lên đầu.\n"
    con_lai = cu[len(dau):] if cu.startswith(dau) else cu
    moi = f"{dau}\n- **{datetime.now():%Y-%m-%d %H:%M}** — {noi_dung}\n{con_lai}"
    tep.write_text(moi, encoding="utf-8")
    return {"da_ghi": str(tep)}


def lenh_muc_luc(home: Path) -> dict:
    dong = ["# Mục lục bộ nhớ", "",
            f"*Tự sinh lúc {datetime.now():%Y-%m-%d %H:%M}. Đừng sửa tay file này.*", ""]

    dong += ["## Pháp lý (có hạn dùng)", "",
             "| Chủ đề | Văn bản | Hiệu lực từ | Hết hạn | Tình trạng |",
             "|---|---|---|---|---|"]
    goc = home / "phap-ly"
    co = False
    if goc.is_dir():
        for tep in sorted(goc.glob("*.md")):
            if ".cu-" in tep.name:
                continue
            gc = doc_ghi_chu(tep)
            m = gc["meta"]
            tt, _ = tinh_trang_ghi_chu(m)
            bieu_tuong = {"con_han": "✅", "qua_han": "⏰", "het_hieu_luc": "❌",
                          "khong_han": "∞"}.get(tt, "?")
            vb = m.get("van_ban")
            vb = ", ".join(vb) if isinstance(vb, list) else (vb or "")
            dong.append(f"| [{m.get('chu_de', tep.stem)}]({tep.name}) | {vb} | "
                        f"{m.get('hieu_luc_tu') or ''} | {m.get('het_han') or ''} | "
                        f"{bieu_tuong} {tt} |")
            co = True
    if not co:
        dong.append("| *(chưa có)* | | | | |")

    dong += ["", "## Quy ước riêng (không hết hạn)", "",
             "| Chủ đề | Cập nhật |", "|---|---|"]
    goc = home / "quy-uoc"
    co = False
    if goc.is_dir():
        for tep in sorted(goc.glob("*.md")):
            if ".cu-" in tep.name:
                continue
            m = doc_ghi_chu(tep)["meta"]
            dong.append(f"| [{m.get('chu_de', tep.stem)}]({tep.name}) | "
                        f"{m.get('cap_nhat_ngay') or ''} |")
            co = True
    if not co:
        dong.append("| *(chưa có)* | |")

    dong.append("")
    (home / "INDEX.md").write_text("\n".join(dong), encoding="utf-8")
    return {"da_ghi": str(home / "INDEX.md")}


def main() -> int:
    p = argparse.ArgumentParser(description="Bộ nhớ cục bộ của skill ke-toan-vn.")
    sub = p.add_subparsers(dest="lenh", required=True)

    s = sub.add_parser("tra", help="Tìm ghi chú theo chủ đề (chạy TRƯỚC khi tra web)")
    s.add_argument("tu_khoa")

    s = sub.add_parser("ghi", help="Ghi ghi chú mới")
    s.add_argument("--loai", choices=["phap-ly", "quy-uoc"], required=True)
    s.add_argument("--chu-de", required=True)
    s.add_argument("--noi-dung")
    s.add_argument("--tep", help="Đọc nội dung từ file markdown")
    s.add_argument("--van-ban", action="append", help="Số hiệu văn bản (lặp lại được)")
    s.add_argument("--hieu-luc-tu", help="YYYY-MM-DD")
    s.add_argument("--nguon", action="append", help="Link nguồn (lặp lại được)")
    s.add_argument("--do-tin-cay", choices=["cao", "trung_binh"], default="trung_binh",
                   help="cao = đối chiếu được nguồn .gov.vn")
    s.add_argument("--thay-the-boi", help="Số hiệu văn bản đã thay văn bản này")
    s.add_argument("--nhom", choices=list(TTL_NGAY), help="Ép nhóm chủ đề (quyết định TTL)")
    s.add_argument("--ttl", type=int, help="Ép số ngày hết hạn")
    s.add_argument("--nguon-quan-sat", help="Quan sát từ đâu (cho quy-uoc)")

    s = sub.add_parser("kiem-han", help="Liệt kê ghi chú quá hạn / hết hiệu lực")
    s = sub.add_parser("nhat-ky", help="Ghi nhật ký việc đã làm")
    s.add_argument("noi_dung")
    s = sub.add_parser("muc-luc", help="Sinh lại INDEX.md")

    args = p.parse_args()
    home = tim_home()
    home.mkdir(parents=True, exist_ok=True)
    (home / "phap-ly").mkdir(exist_ok=True)
    (home / "quy-uoc").mkdir(exist_ok=True)

    if args.lenh == "tra":
        in_json(lenh_tra(home, args.tu_khoa))
    elif args.lenh == "ghi":
        in_json(lenh_ghi(home, args))
    elif args.lenh == "kiem-han":
        in_json(lenh_kiem_han(home))
    elif args.lenh == "nhat-ky":
        in_json(lenh_nhat_ky(home, args.noi_dung))
    elif args.lenh == "muc-luc":
        in_json(lenh_muc_luc(home))
    return 0


if __name__ == "__main__":
    sys.exit(main())
