# Bộ nhớ cục bộ

Bộ nhớ nằm ở `.ke-toan-vn/`, **cạnh** thư mục dự án chứ không nằm trong thư mục skill. Lý do:
cập nhật hay cài lại skill sẽ không xoá mất kiến thức đã tích luỹ.

```
.ke-toan-vn/
├── INDEX.md          # mục lục tự sinh: chủ đề | ngày tra | hết hạn | tình trạng
├── phap-ly/          # cache quy định — CÓ hạn dùng
├── quy-uoc/          # quy ước riêng của người dùng — KHÔNG hết hạn
└── nhat-ky.md        # nhật ký việc đã làm, mới nhất lên đầu
```

Script tự tìm thư mục này theo thứ tự: biến môi trường `KE_TOAN_VN_HOME` → đi ngược lên từ vị trí
script tìm thư mục cha đầu tiên có chứa `.ke-toan-vn/` → cuối cùng fallback `~/.ke-toan-vn`.
Cơ chế này cần thiết vì skill được Codex gọi qua symlink, đường dẫn tương đối sẽ khác.

## Bộ nhớ là của từng nơi triển khai, không phải của skill

Skill này dùng chung cho nhiều người, nên phải phân biệt rõ hai loại nội dung:

| | Đi kèm skill được? | Vì sao |
|---|---|---|
| `phap-ly/` | **Được** | Văn bản pháp luật áp dụng cho mọi người dùng, lại có hạn dùng nên không thể âm thầm cũ đi |
| `quy-uoc/` | **KHÔNG** | Là quy ước của một đơn vị cụ thể. Giao kèm sang nơi khác là đưa thông tin sai |

Ví dụ vì sao điều thứ hai quan trọng: nếu `quy-uoc/` đi kèm một ghi chú kiểu "đơn vị của người dùng
có MST X", thì với đơn vị khác, skill sẽ báo động ở **mọi** hóa đơn vì MST bên mua không khớp — và
người dùng không biết con số đó ở đâu ra để mà sửa. **Khi triển khai cho một đơn vị mới, `quy-uoc/`
phải trống.**

Khi chạy thử hoặc chạy eval, đặt `KE_TOAN_VN_HOME` trỏ sang thư mục tạm để không làm bẩn bộ nhớ
thật:

```bash
KE_TOAN_VN_HOME=/tmp/kt-thu bo_nho.py tra "..."
```

## Bản lưu trữ khi ghi đè

Ghi đè một ghi chú không xoá bản cũ — nó được lưu thành `<tên>.cu-YYYY-MM-DD.md` để đối chiếu
lịch sử ("trước đây là 500 triệu, nay là 1 tỷ" rất hữu ích khi rà soát kỳ trước). Nhưng lệnh `tra`
**bỏ qua** các bản `.cu-`: trả chúng về trong kết quả tra cứu thì người đọc có thể lấy nhầm con số
đã bị thay — đúng cái sai mà cả bộ nhớ này sinh ra để chống.

## Hai loại kiến thức, xử lý khác nhau

### `phap-ly/` — cache quy định, có hạn dùng

Một cache luật không hết hạn thì **tệ hơn là không có cache**: nó biến một câu trả lời sai thành
câu trả lời sai *có vẻ đáng tin*, được lặp lại tự tin qua nhiều tháng. Nên mọi ghi chú pháp lý
đều có `het_han`.

Frontmatter bắt buộc:

```yaml
---
chu_de: nguong doanh thu khong chiu thue GTGT ho kinh doanh
van_ban: ["Luật 149/2025/QH15"]
hieu_luc_tu: 2026-01-01
tra_cuu_ngay: 2026-09-10
het_han: 2026-11-09
thay_the_boi: null          # điền số hiệu nếu văn bản này đã bị thay
tinh_trang: con_hieu_luc    # con_hieu_luc | het_hieu_luc | qua_han
nguon:
  - https://vanban.chinhphu.vn/...
do_tin_cay: cao             # cao = đối chiếu được .gov.vn | trung_binh = chỉ có nguồn thứ cấp
---
```

**TTL theo mức độ biến động** — không dùng một hạn chung, vì các mảng biến động rất khác nhau:

| Loại kiến thức | TTL | Vì sao |
|---|---|---|
| Đấu thầu (NĐ 214/2025, TT 79+80/2025) | **45 ngày** | NĐ 214/2025 mới hiệu lực 8/2025 và **đã có dự thảo sửa** |
| Thuế suất, ngưỡng, hạn nộp, mẫu tờ khai | 60 ngày | Đổi 3 lần trong 18 tháng |
| Quy định hóa đơn (NĐ 254/2026, TT 91/2026) | 90 ngày | Đổi theo nghị định — NĐ 254/2026 vừa thay NĐ 123/2020 và NĐ 70/2025 từ 01/7/2026 |
| Hệ thống tài khoản (TT 200, TT 133) | 365 ngày | Ổn định từ 2014 |

**Ghi chú hết hạn không bị xoá.** Nó được đánh dấu `qua_han` trong INDEX. Trước khi dùng phải tra
lại và ghi đè, nhưng giữ nội dung cũ lại rất có ích: kế toán thường xuyên phải rà soát kỳ trước,
và câu "trước đây là 200 triệu, từ 01/01/2026 là 500 triệu" hữu ích hơn nhiều so với chỉ biết
con số hiện tại.

Khi phát hiện một văn bản đã bị thay, điền `thay_the_boi` và đổi `tinh_trang: het_hieu_luc`.
Đây là hàng rào chống cái bẫy "công cụ tìm kiếm đẩy văn bản cũ lên đầu" mô tả trong
`references/phap-ly.md`.

### `quy-uoc/` — phần học thật sự

Đây mới là thứ khiến skill tốt lên theo thời gian. Cache luật chỉ tiết kiệm thời gian tra cứu;
quy ước mới là thứ giúp skill hiểu **công việc cụ thể của đơn vị đang dùng nó**. Cũng vì vậy mà
nó không được đi kèm khi giao skill sang nơi khác — xem mục trên.

Nên ghi những gì quan sát được từ file thật:

| File | Nội dung |
|---|---|
| `quy-uoc/cong-ty.md` | Các công ty/khách hàng hay gặp và MST của họ, nhà cung cấp quen |
| `quy-uoc/cot-excel.md` | Cách người dùng đặt tên cột ("Tiền hàng" hay "Thành tiền"?), thứ tự cột quen thuộc, bố cục sheet |
| `quy-uoc/tai-khoan.md` | Tài khoản cấp 2/3 người dùng tự mở ngoài TT 200 và ý nghĩa của chúng |
| `quy-uoc/phan-mem.md` | Phần mềm đang dùng (HTKK/MISA/Fast/Bravo), phiên bản, định dạng xuất nhập |
| `quy-uoc/dau-thau.md` | Cấu trúc tiêu chuẩn đánh giá cơ quan hay dùng: các đầu mục HSMT, ngưỡng doanh thu bình quân, số hợp đồng tương tự yêu cầu, cách chấm đạt/không đạt |

**Quy tắc ghi:**

- Chỉ ghi khi **quan sát được từ file thật**. Không suy đoán, không ghi thứ người dùng chưa từng làm.
- Khi thông tin mới mâu thuẫn với ghi chú cũ, **ghi cả hai kèm ngày** và để người dùng quyết định.
  Đừng tự ghi đè — có thể họ đang làm cho hai công ty khác nhau với hai quy ước khác nhau.
- **Không lưu dữ liệu HSDT** (tên nhà thầu, giá dự thầu, nội dung hồ sơ). Bộ nhớ tồn tại lâu dài và
  dùng chung nhiều gói thầu; dữ liệu dự thầu gắn với một gói và phải giữ kín. Chỉ lưu *cấu trúc*
  tiêu chuẩn đánh giá, không lưu *nội dung* hồ sơ.

## Minh bạch với người dùng

Mỗi khi ghi vào bộ nhớ, **nói ra một dòng**: "Đã ghi nhớ: công ty ABC dùng tài khoản 6421 chi tiết
theo phòng ban." Người dùng phải biết skill đang nhớ gì về công việc của họ, và sửa được — file
markdown thuần, mở ra sửa tay lúc nào cũng được.

Một bộ nhớ âm thầm lớn lên là bộ nhớ không ai tin được, vì không ai biết trong đó có gì sai.

## Lệnh

```bash
bo_nho.py tra "<chủ đề>"     # tìm ghi chú; báo rõ còn hạn hay đã quá hạn
bo_nho.py ghi --loai phap-ly --chu-de "..." --tep <file.md>
bo_nho.py ghi --loai quy-uoc --chu-de "..." --noi-dung "..."
bo_nho.py kiem-han           # liệt kê ghi chú quá hạn hoặc hết hiệu lực
bo_nho.py nhat-ky "<việc đã làm>"
bo_nho.py muc-luc            # sinh lại INDEX.md
```

`tra` là lệnh nên chạy **trước** khi tra web. Nó trả về JSON có trường `can_tra_web: true/false`
để bạn quyết định nhanh.
