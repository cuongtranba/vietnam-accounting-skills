# vietnam-accounting-skills

[![ci](https://github.com/cuongtranba/vietnam-accounting-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/cuongtranba/vietnam-accounting-skills/actions/workflows/ci.yml)

Agent Skill cho **nghiệp vụ kế toán và chấm thầu Việt Nam**. Trả lời hoàn toàn bằng tiếng Việt.

Cài được cho Claude Code, Codex, Cursor, OpenCode và các agent khác qua
[`skills`](https://github.com/vercel-labs/skills):

```bash
npx skills add cuongtranba/vietnam-accounting-skills
```

Cài cho một agent cụ thể, phạm vi toàn máy:

```bash
npx skills add cuongtranba/vietnam-accounting-skills -g -a claude-code -y
npx skills add cuongtranba/vietnam-accounting-skills -g -a codex -y
```

Sau khi cài, chạy một lần để dựng môi trường:

```bash
bash <thư-mục-skill>/scripts/bootstrap.sh
```

## Làm được gì

| Việc | Ví dụ câu hỏi |
|---|---|
| Bóc tách hóa đơn điện tử → bảng kê Excel | *"gộp mấy hóa đơn trong thư mục này thành bảng kê mua vào"* |
| Đối chiếu sổ sách, tìm chênh lệch | *"đối chiếu bảng kê bán ra với sổ 511 xem lệch chỗ nào"* |
| Làm sạch, chuẩn hoá file Excel | *"file này số liệu lộn xộn quá, chuẩn hoá lại giúp"* |
| Tra quy định thuế, kế toán | *"năm nay hộ kinh doanh doanh thu bao nhiêu thì không phải nộp thuế GTGT?"* |
| Chấm thầu, so sánh HSDT | *"chấm kỹ thuật rồi lập bảng so sánh giá đánh giá 4 bộ HSDT này"* |

Đọc hóa đơn XML theo chuẩn QĐ 1450/QĐ-TCT và hóa đơn PDF, kể cả bản scan (OCR tiếng Việt).

## Vì sao skill này tồn tại

Các skill xử lý file có sẵn (`xlsx`, `pdf`, `docx`) mạnh về **kỹ thuật file** nhưng không biết
**nghiệp vụ Việt Nam**: cấu trúc hóa đơn điện tử, mẫu bảng kê HTKK, hệ thống tài khoản TT 200,
quy trình chấm thầu theo NĐ 214/2025. Skill này là lớp nghiệp vụ đặt lên trên chúng — nó **ủy quyền**
chứ không viết lại: dựng workbook thì giao cho `xlsx`, OCR thì giao cho `pdf`.

## Sáu nguyên tắc

1. **Trả lời bằng tiếng Việt.** Tên file dùng ASCII không dấu, vì macOS lưu NFD còn Windows lưu NFC
   nên tên file có dấu hay vỡ khi gửi qua lại hoặc upload lên cổng thuế.
2. **Không bịa số.** Mọi con số truy được về ô nguồn hoặc hóa đơn gốc. Đọc không được thì để trống
   kèm cảnh báo — **không điền 0**. Ô trống có cảnh báo thì kế toán sẽ kiểm; số 0 sai thì lặng lẽ
   chảy vào tổng cộng.
3. **Không trả lời quy định từ trí nhớ.** Phải có ghi chú bộ nhớ còn hạn, hoặc tra web mới, kèm
   số hiệu văn bản và ngày hiệu lực.
4. **Quy ước của file có sẵn thắng hướng dẫn của skill.**
5. **Chấm thầu: skill tính toán, tổ chuyên gia quyết định.** Không bao giờ tự kết luận đạt/không đạt
   hay trúng thầu; mỗi số liệu dẫn được về đúng trang trong HSDT.
6. **Không đưa nội dung HSDT ra ngoài.** Chỉ tra web cho văn bản pháp luật, không bao giờ đưa tên
   nhà thầu hay giá dự thầu vào câu truy vấn.

## Bộ nhớ có hạn dùng

Skill giữ bộ nhớ cục bộ ở `.ke-toan-vn/` — file markdown thuần, sửa tay lúc nào cũng được.

```
.ke-toan-vn/
├── INDEX.md      mục lục tự sinh
├── phap-ly/      quy định đã tra — CÓ hạn dùng, hết hạn thì tự tra lại
├── quy-uoc/      quy ước riêng của đơn vị — KHÔNG hết hạn
└── nhat-ky.md    nhật ký việc đã làm
```

**Vì sao ghi chú pháp lý phải hết hạn:** luật thuế Việt Nam đổi rất nhanh. Riêng ngưỡng doanh thu
không chịu thuế GTGT của hộ kinh doanh đã đổi **bốn lần trong hai năm** — 100tr → 200tr
(Luật 48/2024) → 500tr (Luật 149/2025, rồi NĐ 68/2026) → **1 tỷ** (NĐ 141/2026, hồi tố 01/01/2026).
Một cache luật không hết hạn còn tệ hơn không có cache: nó lặp lại câu trả lời sai một cách tự tin
qua nhiều tháng.

Hạn dùng đặt theo mức độ biến động: **đấu thầu 45 ngày**, thuế 60, hóa đơn 90, hệ thống tài khoản 365.
Ngoài `het_han`, mỗi ghi chú còn có `thay_the_boi` — vì công cụ tìm kiếm thường đẩy văn bản đã hết
hiệu lực lên đầu (tra "chấm thầu" vẫn ra NĐ 63/2014 và NĐ 24/2024, cả hai đã bị thay).

**`quy-uoc/` không đóng gói theo repo.** Nó chứa quy ước của một đơn vị cụ thể; phát tán sang nơi
khác là đưa thông tin sai. `phap-ly/` thì có bản mẫu ở `skills/ke-toan-vn/assets/bo-nho-mau/`,
bootstrap sẽ **hỏi** trước khi chép — bộ nhớ âm thầm có sẵn nội dung là bộ nhớ không tin được.

## Chấm thầu — quy trình hai pha

Bước kỹ thuật phải chạy **trước** bước tài chính, không phải vì thủ tục: đơn giá dùng để hiệu chỉnh
phần chào thiếu chỉ được lấy trong các HSDT **đã vượt bước kỹ thuật**
(điểm c khoản 2 Điều 31 NĐ 214/2025).

```bash
PY=$(bash <skill>/scripts/bootstrap.sh --duong-dan-python)
S=<skill>/scripts

$PY $S/doc_hsdt.py <thư mục HSDT> --ra hsdt.json
$PY $S/cham_ky_thuat.py <thư mục HSDT> --yeu-cau yeu_cau_ky_thuat.csv --ra phieu_cham.xlsx
#   → mở phieu_cham.xlsx, điền cột ket_luan (ô vàng, có sẵn danh sách Đạt/Không đạt)
$PY $S/so_sanh_thau.py hsdt.json --danh-muc danh_muc.csv \
      --ket-qua-ky-thuat phieu_cham.xlsx --ra so_sanh.xlsx
```

Trên dữ liệu mẫu, loại một nhà thầu khỏi nhóm vượt kỹ thuật làm giá trị hiệu chỉnh đổi từ
73.542.000 xuống 70.686.000 và mất một vị trí xếp hạng.

Script chấm kỹ thuật **không kết luận đạt/không đạt**. Nó chỉ đối chiếu những gì khách quan —
`thap_hon` khi số nhỏ hơn ngưỡng (RAM 8GB < 16GB), `thieu_du_lieu` khi không tìm thấy — còn tiêu chí
cần phán đoán chuyên môn (xuất xứ, thương hiệu, "tương đương") thì đánh dấu `can_nguoi_xem` và để
tổ chuyên gia quyết.

## Cấu trúc

```
skills/ke-toan-vn/
├── SKILL.md              bộ định tuyến + 6 nguyên tắc
├── agents/openai.yaml    mô tả hiển thị cho Codex
├── assets/bo-nho-mau/    ghi chú pháp lý mẫu (bootstrap hỏi trước khi chép)
├── references/           chi tiết nghiệp vụ, nạp khi cần
│   ├── hoa-don.md        cấu trúc XML QĐ 1450, đọc PDF, tự kiểm
│   ├── doi-chieu.md      chọn khoá, ngưỡng làm tròn, bẫy Unicode NFC/NFD
│   ├── excel-vn.md       định dạng số/ngày VN, nhập HTKK/MISA
│   ├── bao-cao.md        bảng kê, tờ khai, bảng cân đối
│   ├── dau-thau.md       quy trình chấm thầu theo NĐ 214/2025
│   ├── phap-ly.md        bản đồ văn bản + cách tra
│   └── bo-nho.md         giao thức bộ nhớ
└── scripts/
    ├── bootstrap.sh      cài môi trường
    ├── doc_hoa_don.py    hóa đơn XML/PDF → bảng kê
    ├── doi_chieu.py      đối chiếu hai bảng
    ├── chuan_hoa.py      chuẩn hoá số/ngày/MST/Unicode
    ├── kiem_tra_mst.py   kiểm mã số thuế
    ├── bo_nho.py         bộ nhớ
    ├── doc_hsdt.py       bóc tách HSDT, kèm số trang nguồn
    ├── cham_ky_thuat.py  phiếu đối chiếu kỹ thuật HSMT ↔ HSDT
    └── so_sanh_thau.py   bảng so sánh giá đánh giá
```

## Yêu cầu môi trường

`bootstrap.sh` dựng venv riêng (không đụng python hệ thống) và cài qua Homebrew:

| Thành phần | Bắt buộc? | Dùng để |
|---|---|---|
| Python 3.10+ | có | script nghiệp vụ; bản 3.9 của macOS quá cũ cho `recalc.py` của skill `xlsx` |
| `poppler`, `qpdf` | có | đọc và sửa PDF |
| `tesseract` + **`tesseract-lang`** | có | OCR hóa đơn scan — thiếu gói `vie` thì kết quả ra rác |
| LibreOffice | tuỳ chọn | tính lại công thức Excel trước khi giao; bootstrap hỏi trước (~700MB) |

## Phát triển

```bash
python evals/tao_fixtures.py     # sinh dữ liệu mẫu (có cài sẵn lỗi để bắt)
python evals/kiem_thu.py         # 33 phép kiểm hồi quy
```

Mỗi phép kiểm gắn với một cái bẫy cố ý trong dữ liệu mẫu, nên khi đỏ thì biết ngay nghiệp vụ nào
vừa vỡ. `evals/evals.json` chứa 4 ca thử đầu-cuối để chạy bằng agent thật.

Đặt `KE_TOAN_VN_HOME` trỏ sang thư mục tạm khi chạy thử, để không làm bẩn bộ nhớ thật.

## Miễn trừ

Skill hỗ trợ xử lý dữ liệu, **không phải tư vấn pháp lý hay kế toán**. Mọi kết quả cần người có
chuyên môn rà soát trước khi dùng để kê khai, quyết toán hay ra quyết định lựa chọn nhà thầu.
Riêng với chấm thầu, kết quả là bảng tính sơ bộ — tổ chuyên gia chịu trách nhiệm đối chiếu và quyết định.

## Giấy phép

[MIT](LICENSE)
