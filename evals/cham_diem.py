#!/usr/bin/env python3
"""Chấm tự động các assertion kiểm được bằng máy.

    python3 cham_diem.py <thu_muc_iteration>

Chỉ chấm những assertion có thể kiểm khách quan bằng cách đọc file kết quả (con số, sự có mặt
của một chuỗi, có file .xlsx hay không). Những assertion cần phán đoán (vd 'không báo sai lệch
giả', 'không tự tuyên bố trúng thầu') để `None` cho người/grader agent quyết định — ép máy chấm
những thứ đó chỉ tạo ra điểm số trông có vẻ khách quan mà thực chất sai.

Ghi kết quả vào grading.json trong mỗi thư mục run, theo đúng schema viewer cần:
mỗi expectation có các trường text / passed / evidence.
"""
from __future__ import annotations

import json
import os
import re
import sys
import unicodedata
from pathlib import Path


def khong_dau(s: str) -> str:
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn").replace("đ", "d")


def gom_van_ban(thu_muc: Path) -> str:
    """Gộp toàn bộ nội dung đọc được trong outputs/ thành một chuỗi để tìm kiếm."""
    phan = []
    for t in sorted(thu_muc.rglob("*")):
        if not t.is_file():
            continue
        if t.suffix.lower() in (".md", ".txt", ".csv", ".json", ".py", ".log"):
            try:
                phan.append(t.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                pass
        elif t.suffix.lower() in (".xlsx", ".xlsm"):
            try:
                import openpyxl
                wb = openpyxl.load_workbook(t, data_only=True)
                for ws in wb.worksheets:
                    phan.append(f"[sheet {ws.title}]")
                    for hang in ws.iter_rows(values_only=True):
                        phan.append(" ".join(str(o) for o in hang if o is not None))
            except Exception:
                pass
    return "\n".join(phan)


def co_so(van_ban: str, *dang_viet: str) -> bool:
    """Tìm một con số bất kể cách viết: 145.180.000 / 145,180,000 / 145180000."""
    thuan = re.sub(r"[.,\s]", "", van_ban)
    return any(re.sub(r"[.,\s]", "", d) in thuan for d in dang_viet)


def co_chu(van_ban: str, *tu: str) -> bool:
    can = khong_dau(van_ban)
    return all(khong_dau(t) in can for t in tu)


def bat_ky(van_ban: str, *tu: str) -> bool:
    can = khong_dau(van_ban)
    return any(khong_dau(t) in can for t in tu)


def ket_luan_dau_bai(van_ban: str, so_ky_tu: int = 900) -> str:
    """Lấy phần kết luận — nơi bài trả lời chốt con số.

    Ưu tiên đoạn ngay sau tiêu đề kiểu 'Trả lời ngắn' / 'Tóm lại' / 'Kết luận'; nếu không có
    thì lấy phần đầu bài. Cần thiết vì tìm kiếm trên toàn bài hay dính con số của quy định khác.
    """
    can = khong_dau(van_ban)
    for moc in ("tra loi ngan", "tra loi nhanh", "ket luan", "tom lai", "tra loi:"):
        i = can.find(moc)
        if i >= 0:
            return van_ban[i:i + so_ky_tu]
    return van_ban[:so_ky_tu]


_DA_HET_HIEU_LUC = ("het hieu luc", "da bi thay", "thay the", "khong con hieu luc",
                    "da het", "bi bai bo", "khong con ap dung", "cu (", "van ban cu",
                    "truoc day", "da duoc thay")


def kiem_van_ban_cu(van_ban: str, so_hieu: tuple[str, ...]) -> tuple[bool | None, str]:
    """Mỗi lần nhắc tới văn bản hết hiệu lực có được đánh dấu là hết hiệu lực không?"""
    can = khong_dau(van_ban)
    tong, co_danh_dau = 0, 0
    for sh in so_hieu:
        vi_tri = 0
        while True:
            i = can.find(sh, vi_tri)
            if i < 0:
                break
            tong += 1
            quanh = can[max(0, i - 200): i + 200]
            if any(t in quanh for t in _DA_HET_HIEU_LUC):
                co_danh_dau += 1
            vi_tri = i + len(sh)
    if tong == 0:
        return True, "không nhắc tới NĐ 63/2014 hay NĐ 24/2024"
    if co_danh_dau == tong:
        return True, (f"nhắc {tong} lần, và cả {tong} lần đều kèm chú thích đã hết hiệu lực "
                      "— đúng cách, không phải dẫn làm căn cứ hiện hành")
    return False, (f"nhắc {tong} lần nhưng chỉ {co_danh_dau} lần kèm chú thích hết hiệu lực — "
                   f"{tong - co_danh_dau} lần có thể đang dẫn làm căn cứ đang áp dụng")


def ty_le_tieng_viet(van_ban: str) -> float:
    """Ước lượng độ 'tiếng Việt' của phần trả lời qua mật độ ký tự có dấu."""
    chu = [c for c in van_ban if c.isalpha()]
    if len(chu) < 100:
        return 0.0
    co_dau = sum(1 for c in chu if unicodedata.normalize("NFD", c) != c or c in "đĐ")
    return co_dau / len(chu)


def cham(eval_name: str, thu_muc: Path) -> dict[str, tuple[bool | None, str]]:
    out = thu_muc / "outputs"
    vb = gom_van_ban(out) if out.is_dir() else ""
    tra_loi = ""
    tl = out / "tra_loi.md"
    if tl.exists():
        tra_loi = tl.read_text(encoding="utf-8", errors="replace")

    co_xlsx = any(p.suffix.lower() in (".xlsx", ".xlsm") for p in out.rglob("*")) if out.is_dir() else False
    co_bang = co_xlsx or any(p.suffix.lower() == ".csv" for p in out.rglob("*")) if out.is_dir() else False
    tv = ty_le_tieng_viet(tra_loi or vb)
    tv_ok = tv > 0.06
    tv_bc = f"mật độ ký tự có dấu = {tv:.1%} trong phần trả lời"

    r: dict[str, tuple[bool | None, str]] = {}

    if eval_name == "boc-tach-hoa-don-hon-hop":
        r["hd-1"] = (all(co_chu(vb, s) for s in ("00000101", "00000103", "00000105",
                                                 "00000106", "00000107")),
                     "tìm các số hóa đơn 00000101/103/105/106/107 trong kết quả")
        r["hd-2"] = (co_so(vb, "145.180.000"), "tìm tổng tiền hàng 145.180.000")
        r["hd-3"] = (co_so(vb, "12.248.000"), "tìm tổng tiền thuế 12.248.000")
        r["hd-4"] = (co_chu(vb, "0100686200") and bat_ky(
            vb, "sai", "khong khop", "nghi ngo", "kiem tra", "canh bao", "bat thuong"),
            "tìm MST 0100686200 kèm dấu hiệu cảnh báo")
        r["hd-5"] = (bat_ky(vb, "8%", " 8 %") or co_so(vb, "1.480.000"),
                     "tìm thuế suất 8% hoặc tiền thuế 1.480.000 của HĐ 00000104")
        r["hd-6"] = (bat_ky(vb, "KCT", "khong chiu thue"),
                     "tìm dấu hiệu xử lý riêng hóa đơn không chịu thuế")
        r["hd-7"] = (bat_ky(vb, "XML") and bat_ky(vb, "PDF"),
                     "tìm cả hai từ XML và PDF trong kết quả")
        r["hd-8"] = (co_bang, "có file .xlsx hoặc .csv trong outputs")
        r["hd-9"] = (tv_ok, tv_bc)

    elif eval_name == "doi-chieu-ban-ra-so-511":
        r["dc-1"] = (co_chu(vb, "00000205") or co_chu(vb, "205"),
                     "tìm số hóa đơn 00000205")
        r["dc-2"] = (co_chu(vb, "207") and co_so(vb, "900.000"),
                     "tìm 00000207 kèm mức lệch 900.000")
        r["dc-3"] = (co_chu(vb, "209") and bat_ky(vb, "trung", "lap lai", "hai lan", "2 lan"),
                     "tìm 00000209 kèm dấu hiệu trùng lặp")
        r["dc-4"] = (None, "cần người/grader đánh giá: có báo sai lệch giả nào không")
        r["dc-5"] = (all(co_chu(vb, s) for s in ("205", "207", "209")),
                     "cả ba số chứng từ đều được nêu cụ thể")
        r["dc-6"] = (None, "cần người/grader đánh giá: có đối chiếu chênh lệch tổng không")
        r["dc-7"] = (tv_ok, tv_bc)

    elif eval_name == "quy-dinh-nguong-ho-kinh-doanh":
        # Mức đúng là 1 TỶ theo NĐ 141/2026 — không phải 500 triệu.
        #
        # Không tìm '1 tỷ' trên toàn bài: con số đó còn xuất hiện ở quy định KHÁC (mốc bắt buộc
        # hóa đơn điện tử cũng là 1 tỷ), nên tìm cả bài sẽ cho một bài trả lời SAI 500 triệu
        # vẫn đậu. Chỉ xét phần KẾT LUẬN — nơi bài trả lời chốt con số.
        ket_luan = ket_luan_dau_bai(tra_loi or vb)
        c_1ty = bat_ky(ket_luan, "1 ty", "1 tỷ", "01 ty", "01 tỷ", "1.000.000.000")
        c_500 = bat_ky(ket_luan, "500 trieu", "500 triệu", "500.000.000")

        # Hai tiêu chí này KHÔNG chấm tự động được, và đã thử hai lần đều sai:
        #   - tìm '1 tỷ' toàn bài  -> bài trả lời SAI 500 triệu vẫn đậu, vì 1 tỷ còn là mốc
        #     bắt buộc hóa đơn điện tử;
        #   - đòi kết luận chỉ có '1 tỷ' -> bài trả lời ĐÚNG bị trượt, vì nó nêu cả lịch sử
        #     "trước là 500 triệu, nay là 1 tỷ" — vốn là cách trả lời tốt hơn.
        # Phân biệt 'nêu 500 triệu như bối cảnh' với 'chốt 500 triệu là mức hiện hành' là việc
        # của người đọc. Đưa sẵn trích dẫn để người xem quyết trong vài giây.
        trich = " ".join(ket_luan[:260].split())
        r["qd-1"] = (None, f"[cần người xem] kết luận nhắc 1 tỷ={c_1ty}, 500 triệu={c_500} — “{trich}”")
        r["qd-2"] = (None, f"[cần người xem] có chốt 500 triệu là mức hiện hành không? — “{trich}”")
        r["qd-3"] = (bat_ky(tra_loi or vb, "141/2026", "68/2026"),
                     "tìm số hiệu NĐ 141/2026 hoặc NĐ 68/2026")
        r["qd-4"] = (bat_ky(tra_loi or vb, "01/01/2026", "1/1/2026", "01/1/2026",
                            "2026-01-01", "1-1-2026"),
                     "tìm ngày hiệu lực 01/01/2026")
        r["qd-5"] = (None, "cần đọc transcript: có gọi WebSearch/WebFetch không")
        home_bn = Path(os.environ.get("KE_TOAN_VN_HOME")
                       or Path(__file__).resolve().parent.parent / ".ke-toan-vn")
        note = [p for p in (home_bn / "phap-ly").glob("*.md") if ".cu-" not in p.name] \
            if (home_bn / "phap-ly").is_dir() else []
        note_sao = [p for p in out.rglob("*.md") if p.name != "tra_loi.md"] if out.is_dir() else []
        r["qd-6"] = (bool(note) or bool(note_sao),
                     f"ghi chú trong .ke-toan-vn/phap-ly/: {[p.name for p in note]}; "
                     f"bản sao trong outputs: {[p.name for p in note_sao]}")
        noi_dung_note = "\n".join(
            p.read_text(encoding="utf-8", errors="replace") for p in (note + note_sao))
        r["qd-7"] = (("het_han" in noi_dung_note and "nguon" in noi_dung_note)
                     if noi_dung_note else False,
                     "ghi chú có cả trường het_han và nguon")
        r["qd-8"] = (tv_ok, tv_bc)

    elif eval_name == "cham-thau-mua-sam-hang-hoa":
        r["ct-1"] = (bat_ky(vb, "may chieu", "EB-X51") and
                     bat_ky(vb, "thieu", "khong chao", "chua chao"),
                     "tìm Máy chiếu EB-X51 kèm dấu hiệu chào thiếu")
        r["ct-2"] = (co_so(vb, "101.850.000") or co_so(vb, "650.000"),
                     "tìm giá trị đúng 101.850.000 hoặc chênh lệch 650.000")
        r["ct-3"] = (co_so(vb, "35.448.180") and co_so(vb, "1.146.157.820"),
                     "tìm giảm giá 35.448.180 VÀ giá đánh giá đúng 1.146.157.820 của nhà thầu C")
        r["ct-4"] = (bat_ky(vb, "15/10/2026", "2026-10-15", "15-10-2026"),
                     "tìm ngày hết hiệu lực bảo đảm dự thầu 15/10/2026")
        r["ct-5"] = (bat_ky(vb, "214/2025"), "tìm Nghị định 214/2025")
        # Tiêu chí là 'không dẫn làm căn cứ ĐANG ÁP DỤNG', không phải 'không được nhắc tới'.
        # Nhắc NĐ 63/2014 hay 24/2024 kèm chú thích đã hết hiệu lực là hành vi ĐÚNG — thậm chí
        # đáng khen, vì nhiều mẫu biên bản đang lưu hành vẫn trích chúng. Nên xét ngữ cảnh
        # quanh mỗi lần nhắc thay vì cấm tiệt.
        r["ct-6"] = kiem_van_ban_cu(vb, ("63/2014", "24/2024"))
        r["ct-7"] = (None, "cần người/grader đánh giá: có tự tuyên bố trúng thầu không")
        r["ct-8"] = (bat_ky(vb, "tr.1", "trang 1", "ho_so_du_thau.pdf"),
                     "tìm dấu vết nguồn (số trang hoặc tên file)")
        r["ct-9"] = (None, "cần đọc transcript: truy vấn web có chứa tên nhà thầu/giá dự thầu không")
        r["ct-10"] = (co_xlsx, "có file .xlsx trong outputs")
        r["ct-11"] = (tv_ok, tv_bc)

    return r


def main() -> int:
    goc = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path(".")
    tong = {}

    for d in sorted(goc.iterdir()):
        if not d.is_dir() or not (d / "eval_metadata.json").exists():
            continue
        meta = json.loads((d / "eval_metadata.json").read_text(encoding="utf-8"))
        ten = meta["eval_name"]

        for cfg in ("with_skill", "without_skill"):
            run = d / cfg
            if not run.is_dir():
                continue
            kq = cham(ten, run)
            exps = []
            for a in meta["assertions"]:
                passed, bang_chung = kq.get(a["id"], (None, "chưa có quy tắc chấm tự động"))
                exps.append({"text": a["text"], "passed": passed, "evidence": bang_chung})

            dat = sum(1 for e in exps if e["passed"] is True)
            hong = sum(1 for e in exps if e["passed"] is False)
            cho = sum(1 for e in exps if e["passed"] is None)
            (run / "grading.json").write_text(json.dumps({
                "eval_name": ten, "configuration": cfg,
                "expectations": exps,
                "passed": dat, "failed": hong, "needs_review": cho,
                "pass_rate": dat / len(exps) if exps else 0,
            }, ensure_ascii=False, indent=2), encoding="utf-8")
            tong[f"{ten}/{cfg}"] = f"{dat} đạt / {hong} hỏng / {cho} chờ người xem"

    for k, v in tong.items():
        print(f"{k:60} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
