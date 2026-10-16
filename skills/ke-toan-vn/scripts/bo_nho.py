#!/usr/bin/env python3
"""Bộ nhớ cục bộ của skill ke-toan-vn.

    bo_nho.py tra "nguong doanh thu ho kinh doanh"
    bo_nho.py ghi --loai phap-ly --chu-de "..." --tep noi_dung.md \
              --van-ban "Luật 149/2025/QH15" --hieu-luc-tu 2026-01-01 \
              --nguon https://vanban.chinhphu.vn/... --do-tin-cay cao
    bo_nho.py ghi --loai quy-uoc --chu-de "cot-excel" --noi-dung "..."
    bo_nho.py tra "nguong doanh thu ho kinh doanh" --ngay 2025-12-31   # quy định TẠI ngày đó
    bo_nho.py lich-su "nguong doanh thu ho kinh doanh"                 # mọi phiên bản
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
from _chung import home_don_vi, in_json, tim_home  # noqa: E402

# TTL theo mức độ biến động. Không dùng một hạn chung — các mảng biến động rất khác nhau.
TTL_NGAY = {
    "dau-thau": 45,    # NĐ 214/2025 mới hiệu lực 8/2025 và ĐÃ CÓ dự thảo sửa
    "thue": 60,        # thuế suất/ngưỡng đổi 3 lần trong 18 tháng
    "hoa-don": 90,     # đổi theo nghị định
    "tai-khoan": 180,  # TT 99/2025 thay TT 200 từ năm tài chính 2026, TT 58/2026 thay TT 132
    "khac": 60,
}

TU_KHOA_CHU_DE = {
    "dau-thau": ["dau thau", "thau", "hsdt", "hsmt", "nha thau", "goi thau", "214/2025",
                 "sai lech", "gia danh gia", "chi dinh thau"],
    "thue": ["thue", "gtgt", "tndn", "tncn", "to khai", "nguong", "khau tru", "thue suat",
             "quyet toan", "48/2024", "149/2025", "181/2025"],
    "hoa-don": ["hoa don", "123/2020", "70/2025", "78/2021", "254/2026", "91/2026", "1450",
                "xml", "chung tu"],
    "tai-khoan": ["tai khoan", "tt 200", "200/2014", "133/2016", "99/2025", "58/2026",
                  "24/2024", "che do ke toan", "so sach"],
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


_LUU_TRU = re.compile(r"\.cu-(\d{4}-\d{2}-\d{2})(?:-(\d+))?\.md$")


def la_luu_tru(tep: Path) -> bool:
    return ".cu-" in tep.name


def goc_chu_de(tep: Path) -> str:
    """Tên gốc của chủ đề, bỏ phần đuôi lưu trữ `.cu-...`."""
    return tep.name.split(".cu-", 1)[0].removesuffix(".md")


def thu_tu_luu_tru(tep: Path) -> tuple:
    m = _LUU_TRU.search(tep.name)
    return (m.group(1), int(m.group(2) or 0)) if m else ("", 0)


def ten_luu_tru(duong_dan: Path, hom_nay: date) -> Path:
    """Tên bản lưu trữ không bao giờ trùng: `.cu-YYYY-MM-DD-NNN.md`, NNN tăng dần trong ngày.

    Bản cũ chỉ ghi ngày, nên cập nhật hai lần trong một ngày thì bản lưu thứ hai đè mất bản thứ
    nhất — đúng loại mất dấu vết mà bản lưu trữ sinh ra để chống.
    """
    ngay = hom_nay.isoformat()
    dung = [thu_tu_luu_tru(p)[1] for p in duong_dan.parent.glob(f"{duong_dan.stem}.cu-{ngay}*.md")]
    return duong_dan.with_name(f"{duong_dan.stem}.cu-{ngay}-{max(dung, default=0) + 1:03d}.md")


def kiem_nguon(nguon: list) -> tuple[list, bool]:
    """(nguồn sai dạng, có nguồn cơ quan nhà nước). Nguồn phải là URL https có tên miền."""
    from urllib.parse import urlparse

    sai = [n for n in nguon
           if urlparse(n).scheme != "https" or "." not in (urlparse(n).hostname or "")]
    may = [(urlparse(n).hostname or "") for n in nguon]
    co_gov = any(h.endswith(".gov.vn") or h == "chinhphu.vn" or h.endswith(".chinhphu.vn")
                 for h in may)
    return sai, co_gov


def hieu_luc_tai(meta: dict, ngay: date) -> str:
    """'ap_dung' | 'chua_hieu_luc' | 'het_hieu_luc' | 'khong_ro_hieu_luc' tại một ngày."""
    tu = _ngay(meta.get("hieu_luc_tu"))
    if tu is None:
        return "khong_ro_hieu_luc"
    if ngay < tu:
        return "chua_hieu_luc"
    den = _ngay(meta.get("hieu_luc_den"))
    if den is not None and ngay >= den:
        return "het_hieu_luc"
    return "ap_dung"


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

def _mo_ta(tep: Path, gc: dict, thu_muc: str, diem: int) -> dict:
    m = gc["meta"]
    tt, giai_thich = tinh_trang_ghi_chu(m)
    return {
        "loai": thu_muc,
        "tep": str(tep),
        "chu_de": m.get("chu_de", tep.stem),
        "tinh_trang": tt,
        "giai_thich": giai_thich,
        "van_ban": m.get("van_ban"),
        "dieu_khoan": m.get("dieu_khoan"),
        "hieu_luc_tu": m.get("hieu_luc_tu"),
        "hieu_luc_den": m.get("hieu_luc_den"),
        "ngay_ban_hanh": m.get("ngay_ban_hanh"),
        "het_han": m.get("het_han"),
        "thay_the_boi": m.get("thay_the_boi"),
        "sua_doi": m.get("sua_doi"),
        "do_tin_cay": m.get("do_tin_cay"),
        "can_nguoi_duyet": m.get("can_nguoi_duyet"),
        "nguon": m.get("nguon"),
        "ban_luu_tru": la_luu_tru(tep),
        "diem_khop": diem,
        "noi_dung": gc["noi_dung"].strip(),
    }


def _quet(home: Path, tu_khoa: str, ca_luu_tru: bool, home_dv: Path | None = None) -> list[dict]:
    can = khong_dau(tu_khoa)
    tu = [t for t in can.split() if len(t) > 2]
    tim_thay = []
    for thu_muc in ("phap-ly", "quy-uoc"):
        goc = ((home_dv or home) if thu_muc == "quy-uoc" else home) / thu_muc
        if not goc.is_dir():
            continue
        for tep in sorted(goc.glob("*.md")):
            # Bản lưu trữ .cu-* chỉ dùng khi tra theo một ngày trong quá khứ (hồi đó quy định
            # là gì) hoặc khi xem lịch sử. Trả chúng về ở tra cứu hiện hành thì người đọc có thể
            # lấy nhầm con số ĐÃ BỊ THAY — đúng cái sai mà bộ nhớ này sinh ra để chống.
            if la_luu_tru(tep) and not ca_luu_tru:
                continue
            gc = doc_ghi_chu(tep)
            noi_dung_can = khong_dau(
                f"{gc['meta'].get('chu_de', '')} {goc_chu_de(tep)} {gc['noi_dung'][:2000]}")
            diem = sum(1 for t in tu if t in noi_dung_can)
            if diem:
                tim_thay.append(_mo_ta(tep, gc, thu_muc, diem))
    tim_thay.sort(key=lambda g: -g["diem_khop"])
    return tim_thay


def _moi_truoc(ds: list[dict]) -> list[dict]:
    """Bản hiện hành trước, rồi bản lưu trữ từ mới đến cũ."""
    return sorted(ds, key=lambda g: (not g["ban_luu_tru"], thu_tu_luu_tru(Path(g["tep"]))),
                  reverse=True)


def tra_theo_ngay(home: Path, tu_khoa: str, ngay: date, home_dv: Path | None = None) -> dict:
    """Quy định áp dụng TẠI MỘT NGÀY, không phải bản mới nhất.

    Ghi chú còn hạn chỉ nói "điều mình biết còn mới"; nó không nói quy định đó áp dụng cho giao
    dịch năm ngoái. Chọn trong mọi phiên bản (kể cả bản lưu trữ) bản có hiệu lực tại `ngay`;
    nhiều bản cùng phủ ngày đó (sửa đổi hồi tố) thì bản ghi sau thắng.
    """
    tim_thay = _quet(home, tu_khoa, ca_luu_tru=True, home_dv=home_dv)
    cao_nhat = tim_thay[0]["diem_khop"] if tim_thay else 0
    theo_chu_de: dict[tuple, list] = {}
    for g in tim_thay:
        if g["diem_khop"] == cao_nhat:
            theo_chu_de.setdefault((g["loai"], goc_chu_de(Path(g["tep"]))), []).append(g)

    ap_dung, lich_su, ly_do = None, [], []
    for ds in theo_chu_de.values():
        ds = _moi_truoc(ds)
        chon = next((g for g in ds if hieu_luc_tai(g, ngay) == "ap_dung"), None)
        if chon and ap_dung is None:
            ap_dung, lich_su = chon, [g for g in ds if g is not chon]
        else:
            ly_do += [f"{Path(g['tep']).name}: {hieu_luc_tai(g, ngay)}" for g in ds]

    canh_bao = []
    if ap_dung:
        bh, hl = _ngay(ap_dung.get("ngay_ban_hanh")), _ngay(ap_dung.get("hieu_luc_tu"))
        ap_dung["hoi_to"] = bool(bh and hl and bh > hl)
        if ap_dung["hoi_to"]:
            canh_bao.append(
                f"Văn bản ban hành {bh} nhưng hiệu lực hồi tố từ {hl}: tờ khai, báo cáo, quyết "
                f"định lập trước {bh} có thể đã dùng quy định cũ — cần rà soát lại.")
        if ap_dung["ban_luu_tru"]:
            canh_bao.append("Đang dùng bản lưu trữ (quy định của thời điểm đó). Kiểm lại xem có "
                            "văn bản sửa đổi hồi tố nào ban hành sau không.")
        if ap_dung.get("can_nguoi_duyet") == "true":
            canh_bao.append("Diễn giải chưa được người có chuyên môn duyệt — dùng làm căn cứ tra "
                            "cứu, không phải kết luận pháp lý.")
    con_dung = ap_dung is not None and (
        ap_dung["ban_luu_tru"] or ap_dung["tinh_trang"] in ("con_han", "khong_han"))
    return {"ngay": ngay.isoformat(), "ap_dung": ap_dung, "lich_su": lich_su,
            "canh_bao": canh_bao, "can_tra_web": not con_dung,
            "ly_do_khong_ap_dung": ly_do if not ap_dung else []}


def lenh_lich_su(home: Path, tu_khoa: str, home_dv: Path | None = None) -> dict:
    """Mọi phiên bản của một chủ đề, từ cũ đến mới — để truy nguồn gốc một con số đã dùng."""
    tim_thay = _quet(home, tu_khoa, ca_luu_tru=True, home_dv=home_dv)
    if not tim_thay:
        return {"chu_de": None, "phien_ban": []}
    goc = (tim_thay[0]["loai"], goc_chu_de(Path(tim_thay[0]["tep"])))
    ds = [g for g in tim_thay if (g["loai"], goc_chu_de(Path(g["tep"]))) == goc]
    return {"chu_de": tim_thay[0]["chu_de"], "phien_ban": list(reversed(_moi_truoc(ds)))}


def lenh_tra(home: Path, tu_khoa: str, ngay: date | None = None,
             home_dv: Path | None = None) -> dict:
    tim_thay = _quet(home, tu_khoa, ca_luu_tru=False, home_dv=home_dv)
    dung_duoc = [g for g in tim_thay if g["tinh_trang"] in ("con_han", "khong_han")]
    nhom = doan_nhom(tu_khoa)

    if dung_duoc:
        loi_khuyen = "Có ghi chú còn dùng được — đọc trường noi_dung. Không cần tra web."
    elif tim_thay:
        loi_khuyen = ("Có ghi chú nhưng ĐÃ QUÁ HẠN hoặc HẾT HIỆU LỰC. Phải tra web lại. "
                      "Giữ nội dung cũ để so sánh 'trước đây là X, nay là Y'.")
    else:
        loi_khuyen = "Chưa có ghi chú nào. Tra web rồi ghi lại bằng lệnh 'ghi'."

    kq = {
        "tu_khoa": tu_khoa,
        "nhom_chu_de": nhom,
        "ttl_ngay": TTL_NGAY.get(nhom, TTL_NGAY["khac"]),
        "can_tra_web": not dung_duoc,
        "loi_khuyen": loi_khuyen,
        "so_ghi_chu": len(tim_thay),
        "ghi_chu": tim_thay[:5],
    }
    if ngay is not None:
        theo_ngay = tra_theo_ngay(home, tu_khoa, ngay, home_dv)
        kq.update(theo_ngay)
        if theo_ngay["ap_dung"] is None:
            kq["loi_khuyen"] = (f"Không có ghi chú nào có hiệu lực tại {ngay} (ghi chú còn hạn "
                                "chưa chắc áp dụng cho ngày đó). Tra văn bản áp dụng cho kỳ này.")
    return kq


def lenh_ghi(home: Path, args, home_dv: Path | None = None) -> dict:
    noi_dung = args.noi_dung or ""
    if args.tep:
        noi_dung = Path(args.tep).expanduser().read_text(encoding="utf-8")
    if not noi_dung.strip():
        raise SystemExit("Cần --noi-dung hoặc --tep")

    hom_nay = date.today()
    # Quy ước là của từng đơn vị; ghi chú pháp lý dùng chung.
    duong_dan = ((home_dv or home) if args.loai == "quy-uoc" else home) / args.loai / \
        f"{slug(args.chu_de)}.md"

    if args.loai == "phap-ly":
        for truong in ("hieu_luc_tu", "hieu_luc_den", "ngay_ban_hanh"):
            gt = getattr(args, truong)
            if gt and _ngay(gt) is None:
                raise SystemExit(f"--{truong.replace('_', '-')} phải có dạng YYYY-MM-DD: {gt!r}")
        sai, co_gov = kiem_nguon(args.nguon or [])
        if sai:
            raise SystemExit(f"Nguồn phải là URL https đầy đủ: {sai}")
        do_tin_cay = args.do_tin_cay
        if do_tin_cay == "cao" and not co_gov:
            do_tin_cay = "trung_binh"
            print("⚠️  Độ tin cậy 'cao' cần ít nhất một nguồn cơ quan nhà nước (.gov.vn, "
                  "chinhphu.vn) — đã hạ xuống trung_binh", file=sys.stderr)
        nhom = args.nhom or doan_nhom(args.chu_de)
        ttl = args.ttl if args.ttl else TTL_NGAY.get(nhom, TTL_NGAY["khac"])
        meta = {
            "chu_de": args.chu_de,
            "nhom": nhom,
            "van_ban": args.van_ban or [],
            "dieu_khoan": args.dieu_khoan,
            "ngay_ban_hanh": args.ngay_ban_hanh,
            "hieu_luc_tu": args.hieu_luc_tu,
            "hieu_luc_den": args.hieu_luc_den,
            "sua_doi": args.sua_doi or [],
            "thay_the": args.thay_the or [],
            "pham_vi_don_vi": args.pham_vi_don_vi,
            "pham_vi_nam_tai_chinh": args.pham_vi_nam_tai_chinh,
            "tra_cuu_ngay": hom_nay.isoformat(),
            "het_han": (hom_nay + timedelta(days=ttl)).isoformat(),
            "thay_the_boi": args.thay_the_boi,
            "tinh_trang": "het_hieu_luc" if args.thay_the_boi else "con_hieu_luc",
            "nguon": args.nguon or [],
            "do_tin_cay": do_tin_cay,
            # Tra web xong KHÔNG có nghĩa là diễn giải đã được duyệt. Chỉ người có chuyên môn
            # mới gỡ cờ này, bằng cách sửa tay ghi chú.
            "can_nguoi_duyet": "true",
        }
        if not args.nguon:
            print("⚠️  Ghi chú pháp lý không có nguồn — nên có ít nhất một link .gov.vn",
                  file=sys.stderr)
        if not args.hieu_luc_tu:
            print("⚠️  Không có --hieu-luc-tu: ghi chú này sẽ không được dùng khi tra theo ngày "
                  "(--ngay)", file=sys.stderr)
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
        # Bản mới có hiệu lực muộn hơn thì bản cũ hết áp dụng từ ngày đó. Ghi rõ đây là suy ra
        # (không phải đọc từ văn bản), để tra theo ngày vẫn lấy đúng bản cũ cho kỳ cũ.
        tu_cu, tu_moi = _ngay(cu["meta"].get("hieu_luc_tu")), _ngay(meta.get("hieu_luc_tu"))
        if tu_cu and tu_moi and tu_moi > tu_cu and not cu["meta"].get("hieu_luc_den"):
            cu["meta"]["hieu_luc_den"] = tu_moi.isoformat()
            cu["meta"]["hieu_luc_den_suy_ra"] = "true"
        luu = ten_luu_tru(duong_dan, hom_nay)
        ghi_ghi_chu(luu, cu["meta"], cu["noi_dung"])

    ghi_ghi_chu(duong_dan, meta, noi_dung)
    lenh_muc_luc(home, home_dv)

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


def lenh_muc_luc(home: Path, home_dv: Path | None = None) -> dict:
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
    goc = (home_dv or home) / "quy-uoc"
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
    (home_dv or home).mkdir(parents=True, exist_ok=True)
    (home_dv or home).joinpath("INDEX.md").write_text("\n".join(dong), encoding="utf-8")
    return {"da_ghi": str((home_dv or home) / "INDEX.md")}


def main() -> int:
    p = argparse.ArgumentParser(description="Bộ nhớ cục bộ của skill ke-toan-vn.")
    p.add_argument("--don-vi", help="Mã đơn vị: quy ước riêng nằm ở <bộ nhớ>/don-vi/<mã>/ "
                                    "(mặc định KE_TOAN_VN_DON_VI); ghi chú pháp lý dùng chung")
    sub = p.add_subparsers(dest="lenh", required=True)

    s = sub.add_parser("tra", help="Tìm ghi chú theo chủ đề (chạy TRƯỚC khi tra web)")
    s.add_argument("tu_khoa")
    s.add_argument("--ngay", help="Quy định áp dụng TẠI ngày này (YYYY-MM-DD), kể cả bản lưu trữ")
    s = sub.add_parser("lich-su", help="Mọi phiên bản của một chủ đề, kể cả bản lưu trữ")
    s.add_argument("tu_khoa")

    s = sub.add_parser("ghi", help="Ghi ghi chú mới")
    s.add_argument("--loai", choices=["phap-ly", "quy-uoc"], required=True)
    s.add_argument("--chu-de", required=True)
    s.add_argument("--noi-dung")
    s.add_argument("--tep", help="Đọc nội dung từ file markdown")
    s.add_argument("--van-ban", action="append", help="Số hiệu văn bản (lặp lại được)")
    s.add_argument("--hieu-luc-tu", help="Ngày văn bản bắt đầu có hiệu lực, YYYY-MM-DD")
    s.add_argument("--hieu-luc-den", help="Ngày hết hiệu lực (nếu đã biết), YYYY-MM-DD")
    s.add_argument("--ngay-ban-hanh", help="Ngày ban hành — khác ngày hiệu lực khi hồi tố")
    s.add_argument("--dieu-khoan", help="Điều/khoản nêu quy định, vd \"Điều 31 khoản 1\"")
    s.add_argument("--sua-doi", action="append", help="Văn bản mà văn bản này sửa đổi")
    s.add_argument("--thay-the", action="append", help="Văn bản mà văn bản này thay thế")
    s.add_argument("--pham-vi-don-vi", help="Loại đơn vị áp dụng (vd doanh-nghiep, su-nghiep-cong-lap)")
    s.add_argument("--pham-vi-nam-tai-chinh",
                   help="Điều kiện năm tài chính, vd \"bắt đầu từ hoặc sau 2026-01-01\"")
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
    try:
        home_dv, _ = home_don_vi(home, args.don_vi)
    except ValueError as e:
        raise SystemExit(str(e))
    home.mkdir(parents=True, exist_ok=True)
    (home / "phap-ly").mkdir(exist_ok=True)
    (home_dv / "quy-uoc").mkdir(parents=True, exist_ok=True)

    if args.lenh == "tra":
        ngay = None
        if args.ngay:
            ngay = _ngay(args.ngay)
            if ngay is None:
                raise SystemExit(f"--ngay phải có dạng YYYY-MM-DD: {args.ngay!r}")
        in_json(lenh_tra(home, args.tu_khoa, ngay, home_dv))
    elif args.lenh == "lich-su":
        in_json(lenh_lich_su(home, args.tu_khoa, home_dv))
    elif args.lenh == "ghi":
        in_json(lenh_ghi(home, args, home_dv))
    elif args.lenh == "kiem-han":
        in_json(lenh_kiem_han(home))
    elif args.lenh == "nhat-ky":
        in_json(lenh_nhat_ky(home, args.noi_dung))
    elif args.lenh == "muc-luc":
        in_json(lenh_muc_luc(home, home_dv))
    return 0


if __name__ == "__main__":
    sys.exit(main())
