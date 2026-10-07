# Quy trình định kỳ: ghi nhớ một việc lặp lại và chạy lại nó tháng sau

Phần lớn việc của kế toán nội bộ là **cùng một thao tác mỗi tháng trên dữ liệu mới**: tách sổ
lương/hao phí/tài sản theo khoa, lọc bản kết xuất doanh thu theo bộ quy tắc đã chốt, đối chiếu
hai nguồn. Khi người dùng nói **"ghi nhớ"** (để tháng sau làm tương tự), thứ cần lưu là một
*quy trình*: một file TOML mô tả trọn việc đó, chạy bằng `scripts/quy_trinh.py`.

Skill giữ **động cơ** (dùng chung, không biết gì về đơn vị nào). Quy trình giữ **quy tắc của
đơn vị** (tên cột, danh sách khoa, mã đối tượng, ngoại lệ). Đừng viết script riêng cho một
đơn vị vào thư mục skill — đó là đúng kiểu sai mà cơ chế này sinh ra để tránh.

## Khi nào dùng

| Người dùng nói / làm | Việc của bạn |
|---|---|
| "ghi nhớ", "tháng sau làm tương tự", "áp dụng cho các tháng sau" | Viết (hoặc sửa) quy trình, chạy thử, **đọc lại cho người dùng bằng lời** rồi mới lưu |
| "làm tương tự", "như tháng trước", "như đã ghi nhớ" | `quy_trinh.py danh-sach` → chọn quy trình khớp → `chay` |
| Gửi file mà không kèm lời nào | `danh-sach` trước: tên file/bố cục thường khớp một quy trình đã có. Hỏi lại cho chắc rồi chạy |
| Yêu cầu một việc lọc/tách/đối chiếu mới | Làm bằng quy trình ngay từ lần đầu (file .toml tạm), để lúc người dùng nói "ghi nhớ" chỉ cần lưu lại |

Việc không thuộc ba động cơ dưới đây (giải thích nguyên nhân chênh lệch, đọc ảnh chụp mẫu, dò
lỗi dữ liệu) vẫn là việc của bạn — nhưng **ghi cách làm vào `quy-uoc/`** để lần sau khỏi dò lại.

## Ba động cơ

| `loai` | Làm gì | Ví dụ thật |
|---|---|---|
| `tach` | Tách dòng của một sheet ra từng sheet theo cột khoá, giữ phần đầu, công thức trong dòng, định dạng; thêm dòng tổng và sheet TÓM TẮT tự đối chiếu | Sổ lương, hao phí, sổ tài sản → từng khoa |
| `loc` | Mỗi file → GIỮ / LOẠI BỎ (có lý do) / TÓM TẮT (gốc = giữ + loại) | Bản kết xuất doanh thu khoa → DLBC |
| `doi-chieu` | Hai nguồn theo khoá: `gop` (cộng rồi so) hoặc `tung_dong` (ghép 1-1, mỗi dòng B dùng một lần) | Viện phí ↔ sổ xuất nhập tồn; bản máy làm ↔ bản kế toán làm tay |

## Lệnh

```bash
PY="$(bash "$SKILL_DIR/scripts/bootstrap.sh" --duong-dan-python)"
Q="$SKILL_DIR/scripts/quy_trinh.py"
"$PY" "$Q" danh-sach
"$PY" "$Q" xem <tên>                 # quy tắc, nhật ký, câu hỏi còn mở, lần chạy gần nhất
"$PY" "$Q" kiem <tên | file.toml>     # kiểm cú pháp, bắt khoá gõ sai
"$PY" "$Q" chay <tên> <file...> [--ky T09.2026] [--ra-thu-muc DIR]
"$PY" "$Q" chay <tên> --a <file A> --b <file B> [--ky ...]     # đối chiếu
```

Kết quả là JSON có `trang_thai`:

- `xong` — đã ghi file. Báo người dùng: file ở đâu, số dòng/tổng tiền, **mọi `canh_bao`**, và
  **nhắc lại từng câu trong `cau_hoi_mo`**.
- `can_hoi` (mã thoát 2) — có giá trị **chưa từng gặp** ở các cột `theo_doi`. Chưa file nào
  được ghi. Hỏi người dùng từng giá trị: giữ hay loại? Loại → thêm quy tắc vào quy trình. Giữ →
  chạy lại với `--chap-nhan-gia-tri-moi`. **Không tự quyết thay họ** — đây chính là chỗ một
  quy tắc cũ lặng lẽ thôi đúng.
- `loi` (mã thoát 1) — quy trình sai hoặc file không đúng bố cục. Đọc thông điệp, đừng đoán.

`bo_cuc_thay_doi` khác rỗng nghĩa là bản kết xuất có cột thêm/bớt/đổi chỗ so với lần chạy
trước. Kết quả vẫn được ghi (cột được tìm theo tên), nhưng phải báo người dùng.

## Nơi lưu

```
.ke-toan-vn/
├── danh-muc.toml          # tên gọi khoa theo từng nguồn, các tập mã dùng chung
└── quy-trinh/
    ├── <tên>.toml         # một việc định kỳ
    └── lich-su/
        ├── <tên>.jsonl    # mỗi lần chạy: file vào (kèm mã băm, tiêu đề cột), kết quả
        └── <tên>.gia-tri.json   # giá trị đã biết của các cột theo_doi
```

Giống `quy-uoc/`, mọi thứ ở đây là **của đơn vị**, không đi kèm skill. Tên file quy trình
ASCII không dấu (`tach-so-tai-san.toml`), nội dung bên trong tiếng Việt có dấu bình thường.

## Cú pháp

Chung cho mọi loại:

```toml
loai = "tach"                      # tach | loc | doi-chieu
mo_ta = "Một câu nói việc này làm gì"
theo_doi = ["MADOITUONG"]          # cột cần chặn giá trị mới (xem trên)
cau_hoi_mo = ["Câu hỏi người dùng chưa trả lời — mỗi lần chạy sẽ nhắc lại"]

[[nhat_ky]]                        # ai chốt gì, khi nào — thay cho docstring của script cũ
ngay = 2026-10-07
noi_dung = "Kế toán chốt 6 quy tắc cho tháng 09/2026"
```

**Tên cột theo tháng.** Viết `{thang}` (9), `{thang2}` (09), `{nam}` (2026); giá trị lấy từ
`--ky`. Sổ tài sản có cột "Tháng 8/2026", "Lãi tháng 08 VCB" → quy trình viết
`"Tháng {thang}/{nam}"`, `"Lãi tháng {thang2} VCB"`. `{ky}` và `{ten_file}` dùng trong tên
file kết quả.

**Tham chiếu cột** bằng tên ở dòng tiêu đề (so khớp bỏ qua hoa/thường, khoảng trắng thừa, xuống
dòng). Chỉ khi cột không có tiêu đề mới viết chữ cái kèm `$`: `"$Z"`.

### Quy tắc (dùng cho `loc` và `loai_tru` của `doi-chieu`)

```toml
[[quy_tac]]
ma = "2"
mo_ta = "tuỳ chọn — hiện trong cột lý do"
khi = { TENNHOMBHYT = { bang = ["Xét nghiệm", "Máu"] } }        # MỌI cột trong khi phải thoả
tru = [ { TENCHIDINH = { bat_dau = ["Đường máu mao mạch"] } } ]  # thoả MỘT nhóm là được miễn
```

Phép so (một cột có thể ghép nhiều phép, tất cả phải thoả):

| Phép | Nghĩa |
|---|---|
| `bang = [...]` | bằng một trong các giá trị |
| `khac = [...]` | không thuộc danh sách (danh sách trắng: `MADOITUONG = { khac = [1, 2, 8] }` loại mọi mã khác) |
| `bat_dau = [...]` | bắt đầu bằng — dùng cho tên dài có phần đuôi thay đổi ("Định nhóm máu tại giường [...]") |
| `chua = [...]` | chứa chuỗi con |
| `am = true` | là số âm |
| `rong = true/false` | ô trống / không trống |
| `thuoc_tap = "ten"`, `ngoai_tap = "ten"` | như `bang`/`khac` nhưng lấy danh sách từ `[tap]` trong `danh-muc.toml` |

So khớp chuẩn hoá NFC, gộp khoảng trắng, bỏ hoa/thường; 8 và 8.0 và "8" là một. **Không** bỏ số
0 đầu ("042" ≠ "42").

### `tach`

```toml
loai = "tach"
[nguon]
sheet = "2026"                  # khớp cả " 2026 "
dong_tieu_de = 11               # mọi dòng từ 1 tới đây được chép làm phần đầu mỗi sheet
cot_khoa = "KHOA/PHÒNG"
cot_stt = "STT"                 # đánh số lại 1, 2, 3... trong từng sheet
cot_tong = ["Tháng {thang}/{nam}"]   # dòng TỔNG CỘNG (SUBTOTAL) cuối mỗi sheet
[ten_goi]                       # tuỳ chọn: lấy giá trị nhóm từ danh mục
bang = "khoa"
nguon = "tai_san"
[ket_qua]
ra = "SO-TAI-SAN-{ky}-TACH-THEO-KHOA.xlsx"
[[nhom]]
ma = ["MAT"]                    # → danh-muc.toml [khoa.MAT] tai_san = "K. MẮT"
[[nhom]]
ten = "KVS + KVS-HIV"           # tên sheet; mặc định là giá trị đầu tiên
gia_tri = ["KVS", "KVS-HIV"]    # hoặc ghi thẳng giá trị
```

Dòng không thuộc nhóm nào thì không được chép (người dùng thường chỉ cần vài khoa trong hàng
chục); kết quả liệt kê chúng ở `dong_ngoai_cac_nhom`. Giá trị trong quy trình mà kỳ này không có
dòng nào được báo ở `canh_bao` — thường là khoa đổi tên.

Công thức chỉ đọc **chính dòng đó** được giữ và dời theo dòng mới; công thức đọc dòng khác,
sheet khác, workbook ngoài, hoặc đọc cột STT (đã đánh lại) được thay bằng giá trị đã tính.

### `loc`

```toml
loai = "loc"
theo_doi = ["TENNHOMBHYT", "TENLOAIVP", "MADOITUONG"]
[nguon]
cot_tien = "SOTIENCT"            # để TÓM TẮT đối chiếu tổng tiền
[ket_qua]
ra = "DLBC-Khoa-{ten_file}.xlsx"
sheet_giu = "DLBC"
sheet_bo = "LOẠI BỎ"
[[quy_tac]]
...
[[bien_the]]                     # một nhóm file có thêm ngoại lệ
ten = "YHCT"
ap_khi_ten_file = ["YHCT*"]
them_tru = { "3" = [ { TENLOAIVP = { bang = ["Y học cổ truyền"] } } ] }
bo_quy_tac = []                  # hoặc bỏ hẳn quy tắc nào
```

Một dòng bị loại nếu dính **bất kỳ** quy tắc nào. Sheet giữ có đúng thứ tự cột của file nguồn
(bước sau có thể trỏ cột theo chữ cái).

### `doi-chieu`

```toml
loai = "doi-chieu"
[a]
nhan = "MÁU"
tieu_de = "Số lượng MÁU {ky}"     # tiêu đề cột giá trị
sheet = "rptDscdvp"
khoa = ["TENVP"]                  # khoá so sánh
chi_tiet = ["MABN"]               # tuỳ chọn: liệt kê cặp (khoá, chi tiết) lệch cạnh dòng lệch
gia_tri = "SOLUONG"
bo_so_0_dau = []                  # cột khoá cần bỏ số 0 đầu (một bên lưu text, bên kia lưu số)
[[a.loai_tru]]
ma = "1"
mo_ta = "madoituong 8"
khi = { madoituong = { bang = [8] } }
[b]
...                               # cùng số cột khoa/chi_tiet, ghép theo thứ tự
[ket_qua]
che_do = "gop"                    # gop | tung_dong
thu_tu = ["...", "..."]           # gop, khoá một cột: thứ tự dòng cố định theo mẫu người dùng
cot_ghi_chu = "Nguyên nhân chênh lệch"
nguong = 0.5
```

`gop` ghi một sheet: khoá | A | B | chênh lệch (công thức) | ghi chú, dòng lệch tô đỏ, dòng
TỔNG CỘNG. Cột ghi chú liệt kê các cặp chi tiết lệch; **nguyên nhân** (vì sao lệch) vẫn là việc
bạn tra tiếp và viết vào, kèm nguồn.

`tung_dong` ghi các dòng không khớp (LỆCH / CHỈ CÓ A / CHỈ CÓ B) kèm số dòng gốc hai bên, và sheet
TÓM TẮT đếm theo kết quả.

## Danh mục dùng chung

Cùng một khoa, mỗi nguồn gọi một kiểu: "KHS" ở file lương, "SINH HÓA MIỄN DỊCH" ở file hao phí,
"K. SINH HÓA" ở sổ tài sản. Ghi ánh xạ một lần trong `danh-muc.toml`, mọi quy trình dùng chung:

```toml
[khoa.SH]
ten = "Khoa Sinh hóa"
luong = "KHS"
hao_phi = "SINH HÓA MIỄN DỊCH"
tai_san = "K. SINH HÓA"

[khoa.VS]
luong = ["KVS", "KVS-HIV"]       # một khoa có thể ứng nhiều giá trị ở một nguồn

[tap]
doi_tuong_dich_vu = [8, 11, 12]
```

Khoa đổi tên ở một nguồn → sửa một dòng ở đây, không phải sửa từng quy trình.

## Viết một quy trình mới — trình tự

1. Làm việc đó một lần với người dùng như bình thường, nhưng **qua một file .toml tạm**.
2. Nếu người dùng có bản làm tay của kỳ trước, chạy quy trình trên dữ liệu kỳ đó và **so từng
   dòng** với bản làm tay. Lệch nào giải thích được (quy tắc mới, dòng họ thêm tay) thì ghi vào
   `nhat_ky`/`cau_hoi_mo`; lệch nào không giải thích được thì hỏi.
3. Đọc lại quy trình cho người dùng **bằng lời** (không dán TOML): "Mỗi tháng tôi sẽ: ... loại
   các dòng ... trừ ...". Họ xác nhận thì lưu vào `.ke-toan-vn/quy-trinh/` và nói một dòng: "Đã
   ghi nhớ quy trình *tach-so-tai-san*."
4. `kiem` để bắt khoá gõ sai — TOML không báo lỗi khoá lạ, và một quy tắc gõ sai tên sẽ lặng lẽ
   không chạy.

Người dùng bổ sung quy tắc ở tháng sau ("bỏ thêm Điện giải đồ [ED]") → sửa quy trình, thêm một
dòng `nhat_ky`, chạy lại. Đừng sửa file kết quả bằng tay.
