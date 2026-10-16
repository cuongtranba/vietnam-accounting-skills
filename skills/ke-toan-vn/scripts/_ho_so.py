"""Hồ sơ lần chạy (run manifest) và sổ cái nối chuỗi — bằng chứng truy được từ nguồn tới kết quả.

Mỗi lần chạy ghi một hồ sơ JSON `<bộ nhớ đơn vị>/ho-so/<run_id>.json`: mã băm SHA-256 đầy đủ
của từng file nguồn, của quy trình và danh mục đã áp, của từng file kết quả; các phép kiểm soát
(số dòng, tổng tiền, bất biến, ngoại lệ); và `ket_qua_sha256` — mã băm của KẾT QUẢ NGHIỆP VỤ (số
dòng, tổng tiền...) không kèm thời gian hay đường dẫn, để phát lại lần sau so được.

Sổ cái `ho-so/so-cai.jsonl` chỉ nối thêm. Mỗi dòng mang mã băm của dòng trước, nên sửa, xoá
hay chèn một dòng ở giữa đều làm đứt chuỗi; mỗi dòng "lan_chay" mang mã băm của file hồ sơ, nên
sửa tay hồ sơ cũng lộ. Đây là CHỐNG SỬA ÂM THẦM (tamper-evident), KHÔNG phải bất biến: ai có
quyền ghi thư mục vẫn xoá được cả sổ. Muốn bền hơn thì sao lưu sổ cái ra nơi khác (hoặc gửi mã
băm dòng cuối cho người duyệt) — xem references/kiem-soat.md.

Hồ sơ không chứa nội dung dòng dữ liệu (tên bệnh nhân, tên dịch vụ...). Các trường bắt đầu
bằng `_` (đường dẫn tuyệt đối trên máy) chỉ dùng để kiểm lại tại chỗ và bị bỏ khi xuất gói.
"""

from __future__ import annotations

import hashlib
import json
import platform
import secrets
import subprocess
import unicodedata
from datetime import datetime
from pathlib import Path

SCHEMA = "1.0"
KHONG_XAC_THUC = "UNVERIFIED_HUMAN_REVIEW"
MIEN_TRU = ("Gói này là bằng chứng kỹ thuật về một lần chạy công cụ (nguồn, quy tắc, kết quả, "
            "người xem). Nó không phải chứng nhận, ý kiến kiểm toán hay xác nhận của Kiểm toán "
            "Nhà nước hay cơ quan thuế; danh tính người duyệt là tự khai, chưa được xác thực.")
_KHOA_DUONG_DAN = {"nguon", "ra", "a", "b", "tep", "tep_ket_qua"}


def chuan_json(du_lieu) -> bytes:
    return json.dumps(du_lieu, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                      default=str).encode("utf-8")


def bam_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def bam_tep(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for khoi in iter(lambda: f.read(1 << 20), b""):
            h.update(khoi)
    return h.hexdigest()


def bo_duong_dan(x):
    """Kết quả nghiệp vụ không kèm đường dẫn: cùng số liệu ở thư mục khác vẫn cùng mã băm."""
    if isinstance(x, dict):
        return {k: bo_duong_dan(v) for k, v in x.items()
                if k not in _KHOA_DUONG_DAN and not k.startswith("_")}
    if isinstance(x, list):
        return [bo_duong_dan(v) for v in x]
    return x


def _bo_kiem_soat(x):
    if isinstance(x, dict):
        return {k: _bo_kiem_soat(v) for k, v in x.items() if k != "bat_bien"}
    if isinstance(x, list):
        return [_bo_kiem_soat(v) for v in x]
    return x


def bam_ket_qua(ket_qua) -> str:
    """Mã băm của KẾT QUẢ NGHIỆP VỤ (số dòng, tổng tiền, lý do loại...). Bỏ đường dẫn và các
    trường kiểm soát (`bat_bien`: xem trước thì không đọc lại file), để cùng nguồn + cùng quy tắc
    luôn ra cùng mã — đó là điều phát lại cần chứng minh."""
    return bam_bytes(chuan_json(_bo_kiem_soat(bo_duong_dan(ket_qua))))


def tao_run_id() -> str:
    return f"run-{datetime.now():%Y%m%dT%H%M%S}-{secrets.token_hex(4)}"


def bay_gio() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def phien_ban_skill() -> dict:
    """Phiên bản và commit của skill (nếu chạy từ một bản git). Không có thì ghi None."""
    goc = Path(__file__).resolve().parents[3]
    pb = goc / "version.txt"
    commit = None
    try:
        kq = subprocess.run(["git", "-C", str(goc), "rev-parse", "HEAD"], capture_output=True,
                            text=True, timeout=5)
        if kq.returncode == 0:
            commit = kq.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return {"phien_ban": pb.read_text().strip() if pb.exists() else None, "git_commit": commit,
            "python": platform.python_version(), "he_dieu_hanh": platform.system()}


def nguoi(ten: str | None) -> dict | None:
    """Người do người chạy tự khai. Không có cơ chế xác thực danh tính nào được tích hợp, nên
    luôn ghi KHONG_XAC_THUC. Một host có xác thực thật (SSO, chữ ký số) cắm vào `danh_tinh_host`."""
    if not ten:
        return None
    return {"ten": unicodedata.normalize("NFC", ten.strip()), "xac_thuc": KHONG_XAC_THUC,
            "nguon": "tu_khai"}


def danh_tinh_host() -> dict | None:
    """Điểm cắm cho danh tính đã xác thực do host cung cấp. Chưa có host nào → None.

    Biến môi trường, tên tài khoản máy hay tham số dòng lệnh đều KHÔNG phải xác thực — ai cũng
    gõ được. Chỉ trả về một danh tính khi có bằng chứng xác thực kiểm được (ví dụ token ký bởi
    nhà cung cấp danh tính mà đơn vị tin cậy). Cho tới lúc đó mọi phê duyệt là tự khai.
    """
    return None


# --- Lưu trữ -----------------------------------------------------------------------------

def thu_muc(home_dv: Path) -> Path:
    return home_dv / "ho-so"


def _so_cai(home_dv: Path) -> Path:
    return thu_muc(home_dv) / "so-cai.jsonl"


def doc_so_cai(home_dv: Path) -> list[dict]:
    p = _so_cai(home_dv)
    if not p.exists():
        return []
    return [json.loads(d) for d in p.read_text(encoding="utf-8").splitlines() if d.strip()]


def them_so_cai(home_dv: Path, muc: dict) -> dict:
    ds = doc_so_cai(home_dv)
    muc = {**muc, "stt": len(ds) + 1, "truoc": ds[-1]["bam"] if ds else None,
           "thoi_gian": muc.get("thoi_gian") or bay_gio()}
    muc["bam"] = bam_bytes(chuan_json({k: v for k, v in muc.items() if k != "bam"}))
    thu_muc(home_dv).mkdir(parents=True, exist_ok=True)
    with _so_cai(home_dv).open("a", encoding="utf-8") as f:
        f.write(json.dumps(muc, ensure_ascii=False, sort_keys=True) + "\n")
    return muc


def kiem_so_cai(home_dv: Path) -> dict:
    loi, truoc = [], None
    for i, muc in enumerate(doc_so_cai(home_dv), 1):
        if muc.get("truoc") != truoc:
            loi.append(f"dòng {i}: không nối với dòng trước (sổ bị sửa/xoá/chèn)")
        if bam_bytes(chuan_json({k: v for k, v in muc.items() if k != "bam"})) != muc.get("bam"):
            loi.append(f"dòng {i}: nội dung không khớp mã băm của chính nó")
        truoc = muc.get("bam")
    return {"hop_le": not loi, "loi": loi, "bam_dong_cuoi": truoc}


def ghi_ho_so(home_dv: Path, ho_so: dict) -> dict:
    d = thu_muc(home_dv)
    d.mkdir(parents=True, exist_ok=True)
    noi_dung = chuan_json(ho_so)
    p = d / f"{ho_so['run_id']}.json"
    tam = p.with_name(f".~{p.name}")
    tam.write_bytes(noi_dung)
    tam.replace(p)
    return them_so_cai(home_dv, {"loai": "lan_chay", "run_id": ho_so["run_id"],
                                 "ho_so_sha256": bam_ho_so(ho_so),
                                 "thoi_gian": ho_so["thoi_gian"]})


def bam_ho_so(ho_so: dict) -> str:
    """Mã băm của PHẦN CÔNG KHAI hồ sơ — thứ được xuất ra gói, nên người nhận gói tự tính lại
    được. Đường dẫn trên máy (`_...`) chỉ là gợi ý để kiểm lại tại chỗ, không phải bằng chứng."""
    return bam_bytes(chuan_json(cong_khai(ho_so)))


def doc_ho_so(home_dv: Path, run_id: str) -> dict:
    if not run_id.replace("-", "").isalnum():
        raise LookupError(f"run_id không hợp lệ: {run_id!r}")
    p = thu_muc(home_dv) / f"{run_id}.json"
    if not p.exists():
        raise LookupError(f"Không có lần chạy {run_id} trong {thu_muc(home_dv)}")
    return json.loads(p.read_text(encoding="utf-8"))


def ho_so_moi_nhat_co_dau_ra(home_dv: Path, sha: str) -> list[dict]:
    """Các lần chạy (đọc từ hồ sơ) đã sinh ra một file kết quả có mã băm `sha`."""
    ra = []
    for p in sorted(thu_muc(home_dv).glob("run-*.json")) if thu_muc(home_dv).exists() else []:
        try:
            hs = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if any(x.get("sha256") == sha for x in hs.get("dau_ra", [])):
            ra.append(hs)
    return ra


# --- Kiểm và trạng thái duyệt ------------------------------------------------------------

def _kiem_tep(ds: list[dict], vai: str) -> tuple[list, list]:
    doi, mat = [], []
    for x in ds:
        p = Path(x.get("_duong_dan") or "")
        if not x.get("_duong_dan") or not p.is_file():
            mat.append({"vai": vai, "nhan": x.get("nhan")})
        elif bam_tep(p) != x.get("sha256"):
            doi.append({"vai": vai, "nhan": x.get("nhan")})
    return doi, mat


def kiem_lan_chay(home_dv: Path, run_id: str) -> dict:
    """Hồ sơ còn khớp sổ cái không; nguồn, quy tắc, kết quả trên đĩa còn đúng mã băm không."""
    hs = doc_ho_so(home_dv, run_id)
    so_cai = kiem_so_cai(home_dv)
    muc = next((m for m in doc_so_cai(home_dv)
                if m.get("loai") == "lan_chay" and m.get("run_id") == run_id), None)
    khop = muc is not None and muc.get("ho_so_sha256") == bam_ho_so(hs)
    doi, mat = [], []
    for ds, vai in ((hs.get("dau_vao", []), "nguon"), (hs.get("dau_ra", []), "ket_qua"),
                    ([hs["quy_tac"]] if hs.get("quy_tac") else [], "quy_tac")):
        d, m = _kiem_tep(ds, vai)
        doi += d
        mat += m
    toan_ven = khop and so_cai["hop_le"] and not doi and not mat
    return {"run_id": run_id, "toan_ven": toan_ven, "ho_so_khop_so_cai": khop,
            "so_cai_hop_le": so_cai["hop_le"], "loi_so_cai": so_cai["loi"],
            "thay_doi": doi, "khong_tim_thay": mat,
            "trang_thai_duyet": trang_thai_duyet(home_dv, run_id, toan_ven)}


def cac_phe_duyet(home_dv: Path, run_id: str) -> list[dict]:
    return [m for m in doc_so_cai(home_dv) if m.get("loai") == "duyet" and m.get("run_id") == run_id]


def trang_thai_duyet(home_dv: Path, run_id: str, toan_ven: bool) -> str:
    """chua_duyet | da_xem_chua_xac_thuc | approved | rejected | vo_hieu.

    `approved` chỉ khi có người phê duyệt ĐÃ XÁC THỰC danh tính (qua danh_tinh_host) — không có
    host nào như vậy thì không đạt được, và đó là cố ý. Nội dung đổi sau khi duyệt → vo_hieu.
    """
    pd = cac_phe_duyet(home_dv, run_id)
    if not pd:
        return "chua_duyet"
    if not toan_ven:
        return "vo_hieu"
    if pd[-1].get("quyet_dinh") == "tu-choi":
        return "rejected"
    if any(p.get("vai_tro") == "nguoi-phe-duyet" and p.get("quyet_dinh") == "dong-y"
           and (p.get("nguoi") or {}).get("xac_thuc") == "VERIFIED" for p in pd):
        return "approved"
    return "da_xem_chua_xac_thuc"


def cong_khai(hs: dict) -> dict:
    """Bản xuất: bỏ mọi trường riêng của máy (bắt đầu bằng `_`)."""
    if isinstance(hs, dict):
        return {k: cong_khai(v) for k, v in hs.items() if not k.startswith("_")}
    if isinstance(hs, list):
        return [cong_khai(v) for v in hs]
    return hs
