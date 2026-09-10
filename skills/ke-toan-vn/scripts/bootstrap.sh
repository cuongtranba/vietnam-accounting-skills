#!/usr/bin/env bash
# Cài đặt môi trường cho skill ke-toan-vn.
#
# Máy macOS thường chỉ có /usr/bin/python3 (bản hệ thống) không kèm thư viện nào,
# và cài đè vào đó vừa cần quyền admin vừa dễ hỏng hệ thống. Nên skill dùng venv riêng
# đặt cạnh bộ nhớ, trong .ke-toan-vn/venv.
#
#   bootstrap.sh                    cài đầy đủ (hỏi trước khi cài LibreOffice)
#   bootstrap.sh --kiem-tra         chỉ kiểm tra, không cài gì
#   bootstrap.sh --duong-dan-python in đường dẫn python của venv rồi thoát
#   bootstrap.sh --khong-hoi        cài tất cả, không hỏi (kể cả LibreOffice)

set -uo pipefail

GOI_PY="openpyxl pandas pdfplumber pypdf lxml python-dateutil XlsxWriter"

# --- Tìm thư mục bộ nhớ ------------------------------------------------------
# Thứ tự: KE_TOAN_VN_HOME -> thư mục cha đầu tiên có .ke-toan-vn/ -> ~/.ke-toan-vn
tim_home() {
    if [[ -n "${KE_TOAN_VN_HOME:-}" ]]; then
        printf '%s\n' "$KE_TOAN_VN_HOME"; return
    fi
    local d
    d="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
    while [[ "$d" != "/" ]]; do
        if [[ -d "$d/.ke-toan-vn" ]]; then
            printf '%s\n' "$d/.ke-toan-vn"; return
        fi
        d="$(dirname "$d")"
    done
    printf '%s\n' "$HOME/.ke-toan-vn"
}

HOME_KT="$(tim_home)"
VENV="$HOME_KT/venv"
PY_VENV="$VENV/bin/python"

# Chọn Python để dựng venv. macOS chỉ có sẵn /usr/bin/python3 = 3.9, mà script recalc.py của
# skill `xlsx` cần 3.10+ (dùng tempfile ignore_cleanup_errors). Dựng venv bằng 3.9 thì mọi việc
# của ke-toan-vn vẫn chạy, nhưng hễ cần tính lại công thức Excel là hỏng — nên ưu tiên bản mới.
chon_python() {
    local ung_vien p
    for p in python3.14 python3.13 python3.12 python3.11 python3.10; do
        ung_vien="$(command -v "$p" 2>/dev/null)" && { printf '%s\n' "$ung_vien"; return; }
    done
    command -v python3
}

# --- --duong-dan-python: im lặng, chỉ in đường dẫn ---------------------------
if [[ "${1:-}" == "--duong-dan-python" ]]; then
    if [[ -x "$PY_VENV" ]]; then
        printf '%s\n' "$PY_VENV"
        exit 0
    fi
    # Chưa có venv: trả về python hệ thống để script còn báo lỗi tử tế cho người dùng
    command -v python3
    exit 0
fi

KIEM_TRA=0
KHONG_HOI=0
for arg in "$@"; do
    case "$arg" in
        --kiem-tra)  KIEM_TRA=1 ;;
        --khong-hoi) KHONG_HOI=1 ;;
        -h|--help)   sed -n '2,14p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) echo "Không hiểu tham số: $arg" >&2; exit 2 ;;
    esac
done

ok()   { printf '  ✅ %s\n' "$1"; }
loi()  { printf '  ❌ %s\n' "$1"; }
canh() { printf '  ⚠️  %s\n' "$1"; }

echo "Thư mục bộ nhớ : $HOME_KT"
echo "Môi trường Python: $VENV"
echo

# --- 1. venv -----------------------------------------------------------------
echo "1. Môi trường Python"
if [[ ! -x "$PY_VENV" ]]; then
    if [[ $KIEM_TRA -eq 1 ]]; then
        loi "Chưa có venv — chạy 'bootstrap.sh' để tạo"
    else
        PY_GOC="$(chon_python)"
        echo "   Đang tạo venv bằng $PY_GOC ($("$PY_GOC" -V 2>&1))..."
        mkdir -p "$HOME_KT"
        if "$PY_GOC" -m venv "$VENV"; then
            ok "Đã tạo venv"
        else
            loi "Không tạo được venv. Kiểm tra python3 đã cài chưa."
            exit 1
        fi
    fi
fi

if [[ -x "$PY_VENV" ]]; then
    PY_MINOR="$("$PY_VENV" -c 'import sys; print(sys.version_info[1])' 2>/dev/null || echo 0)"
    if [[ "$PY_MINOR" -lt 10 ]]; then
        canh "venv đang dùng Python 3.$PY_MINOR — script recalc.py của skill xlsx cần 3.10 trở lên."
        if command -v brew >/dev/null 2>&1 && [[ $KIEM_TRA -eq 0 ]]; then
            canh "Cài bản mới:  brew install python@3.13  rồi xoá $VENV và chạy lại bootstrap."
        fi
    fi
fi

if [[ -x "$PY_VENV" ]]; then
    if [[ $KIEM_TRA -eq 0 ]]; then
        echo "   Đang cài thư viện (lần đầu mất vài phút)..."
        "$PY_VENV" -m pip install --quiet --upgrade pip >/dev/null 2>&1
        # shellcheck disable=SC2086
        if "$PY_VENV" -m pip install --quiet $GOI_PY; then
            ok "Đã cài thư viện"
        else
            loi "Cài thư viện thất bại — xem thông báo lỗi phía trên"
        fi
    fi
    echo "   Kiểm tra từng thư viện:"
    "$PY_VENV" - <<'PYEOF'
import importlib, sys
can = [("openpyxl","đọc/ghi Excel"), ("pandas","xử lý bảng"),
       ("pdfplumber","đọc PDF"), ("pypdf","thao tác PDF"),
       ("lxml","đọc XML hóa đơn"), ("dateutil","xử lý ngày"),
       ("xlsxwriter","ghi Excel nhiều sheet")]
thieu = []
for mod, mota in can:
    try:
        importlib.import_module(mod)
        print(f"     ✅ {mod:<12} {mota}")
    except Exception:
        print(f"     ❌ {mod:<12} {mota}")
        thieu.append(mod)
sys.exit(1 if thieu else 0)
PYEOF
fi
echo

# --- 2. Công cụ dòng lệnh ----------------------------------------------------
echo "2. Công cụ dòng lệnh"
CAN_BREW=()

kiem_lenh() { # tên_lệnh  gói_brew  mô_tả
    if command -v "$1" >/dev/null 2>&1; then
        ok "$1 — $3"
    else
        loi "$1 — $3 (thiếu)"
        CAN_BREW+=("$2")
    fi
}

kiem_lenh pdftotext poppler       "đọc chữ trong PDF nhanh"
kiem_lenh qpdf      qpdf          "sửa/kiểm PDF hỏng"
kiem_lenh tesseract tesseract     "OCR hóa đơn scan"

# tesseract có nhưng thiếu tiếng Việt thì OCR ra rác — phải kiểm riêng.
# Gói 'tesseract' của Homebrew chỉ kèm eng/osd/snum, KHÔNG có vie; nên nếu tesseract còn
# thiếu thì chắc chắn cũng cần tesseract-lang, cài luôn một lượt thay vì bắt chạy hai lần.
if ! command -v tesseract >/dev/null 2>&1; then
    CAN_BREW+=("tesseract-lang")
elif tesseract --list-langs 2>/dev/null | grep -qx "vie"; then
    ok "tesseract có gói tiếng Việt (vie)"
else
    loi "tesseract THIẾU gói tiếng Việt — OCR hóa đơn sẽ ra rác"
    CAN_BREW+=("tesseract-lang")
fi

if command -v soffice >/dev/null 2>&1 || [[ -x /Applications/LibreOffice.app/Contents/MacOS/soffice ]]; then
    ok "LibreOffice — tính lại công thức Excel"
    CO_LIBRE=1
else
    canh "LibreOffice chưa cài — skill vẫn dùng được, nhưng không tính lại được công thức Excel"
    CO_LIBRE=0
fi
echo

# --- 3. Cài phần còn thiếu ---------------------------------------------------
if [[ $KIEM_TRA -eq 1 ]]; then
    echo "Chế độ kiểm tra — không cài gì cả."
    echo "Chạy 'bootstrap.sh' (không tham số) để cài phần còn thiếu."
    exit 0
fi

if ! command -v brew >/dev/null 2>&1; then
    if [[ ${#CAN_BREW[@]} -gt 0 ]]; then
        canh "Thiếu ${CAN_BREW[*]} nhưng máy chưa có Homebrew."
        canh "Cài Homebrew tại https://brew.sh rồi chạy lại."
    fi
    exit 0
fi

if [[ ${#CAN_BREW[@]} -gt 0 ]]; then
    echo "3. Cài công cụ còn thiếu qua Homebrew: ${CAN_BREW[*]}"
    brew install "${CAN_BREW[@]}" && ok "Xong" || loi "Có gói cài không thành công"
    echo
fi

if [[ $CO_LIBRE -eq 0 ]]; then
    echo "4. LibreOffice"
    echo "   Dùng để tính lại công thức trong file Excel trước khi giao (skill xlsx cần)."
    echo "   Dung lượng khoảng 700MB."
    CAI=0
    if [[ $KHONG_HOI -eq 1 ]]; then
        CAI=1
    elif [[ -t 0 ]]; then
        read -r -p "   Cài LibreOffice bây giờ? [c/K] " tl
        [[ "$tl" =~ ^[cCyY]$ ]] && CAI=1
    else
        canh "Bỏ qua (không ở chế độ tương tác). Chạy 'bootstrap.sh --khong-hoi' để cài."
    fi
    if [[ $CAI -eq 1 ]]; then
        brew install --cask libreoffice && ok "Đã cài LibreOffice" || loi "Cài LibreOffice thất bại"
    fi
    echo
fi

# --- 5. Ghi chú pháp lý mẫu -------------------------------------------------
# Đóng gói theo repo nhưng KHÔNG tự chép: người dùng phải biết bộ nhớ của mình đang có gì
# và nội dung đó được tra cứu từ khi nào. Bộ nhớ âm thầm có sẵn nội dung là bộ nhớ không tin được.
MAU="$(cd "$(dirname "${BASH_SOURCE[0]}")/../assets/bo-nho-mau" 2>/dev/null && pwd -P || true)"
if [[ -n "$MAU" && -d "$MAU/phap-ly" ]]; then
    CHUA_CO=0
    for f in "$MAU"/phap-ly/*.md; do
        [[ -e "$HOME_KT/phap-ly/$(basename "$f")" ]] || CHUA_CO=$((CHUA_CO + 1))
    done
    if [[ $CHUA_CO -gt 0 ]]; then
        echo "5. Ghi chú pháp lý mẫu"
        echo "   Repo có sẵn $CHUA_CO ghi chú đã tra cứu (ngưỡng hộ kinh doanh, giảm thuế GTGT 8%,"
        echo "   ngưỡng thanh toán không tiền mặt, đơn giá hiệu chỉnh sai lệch)."
        echo "   Chúng có ngày tra cứu và HẠN DÙNG riêng — hết hạn thì skill tự tra lại."
        CHEP=0
        if [[ $KHONG_HOI -eq 1 ]]; then
            CHEP=1
        elif [[ -t 0 ]]; then
            read -r -p "   Chép vào bộ nhớ để khỏi phải tra lần đầu? [c/K] " tl
            [[ "$tl" =~ ^[cCyY]$ ]] && CHEP=1
        else
            canh "Bỏ qua (không ở chế độ tương tác). Chép tay từ: $MAU/phap-ly/"
        fi
        if [[ $CHEP -eq 1 ]]; then
            mkdir -p "$HOME_KT/phap-ly"
            for f in "$MAU"/phap-ly/*.md; do
                [[ -e "$HOME_KT/phap-ly/$(basename "$f")" ]] || cp "$f" "$HOME_KT/phap-ly/"
            done
            ok "Đã chép $CHUA_CO ghi chú. Xem danh sách: bo_nho.py muc-luc"
            canh "Đây là ảnh chụp tại thời điểm đóng gói repo — kiểm ngày tra_cuu_ngay trước khi tin."
        fi
        echo
    fi
fi

echo "Hoàn tất. Kiểm tra lại bất cứ lúc nào bằng: bootstrap.sh --kiem-tra"
