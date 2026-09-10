# Excel cho kế toán Việt Nam

Phần kỹ thuật xlsx (openpyxl, công thức, recalc) đã có trong skill **`xlsx`** — đọc nó khi cần dựng
workbook. File này chỉ nói phần đặc thù Việt Nam.

## Định dạng số và ngày

| Thứ | Việt Nam | Bẫy |
|---|---|---|
| Phân cách nghìn | dấu chấm `1.234.567` | `float("1.234.567")` lỗi; `float("1.234")` ra 1.234 chứ không phải 1234 |
| Thập phân | dấu phẩy `1.234,56` | |
| Tiền tệ | `1.234.567 ₫` hoặc `đ` | |
| Ngày | `dd/mm/yyyy` | `15/07/2026` là 15 tháng 7 |
| Âm | `(1.234.567)` hoặc `-1.234.567` | Dạng ngoặc hay bị đọc thành chuỗi |

Định dạng số Excel nên dùng cho tiền VND: `#,##0` (không lấy phần lẻ — VND không có đơn vị nhỏ hơn
đồng trong sổ sách thông thường). Thuế suất lưu dạng **phân số** (0.1) với định dạng `0%`, không
lưu số 10 rồi ghi chữ "%".

**MST phải là chuỗi.** Rất nhiều MST bắt đầu bằng `0` (`0100109106`). Lưu dạng số thì Excel ăn mất
số 0 đầu và MST thành sai. Khi ghi bằng openpyxl, ép kiểu chuỗi và đặt `number_format = '@'`.
Khi đọc, đọc bằng `dtype=str`.

**Chuẩn hoá Unicode về NFC** khi gộp file từ nhiều nguồn — xem `references/doi-chieu.md`, phần bẫy.

## Nhập liệu vào HTKK

HTKK chỉ nhận bảng kê Excel **đúng mẫu của chính phiên bản HTKK đang dùng**. Mẫu nằm ở
`C:\Program Files (x86)\HTKK\InterfaceTemplates\excel\` (máy Windows). Phiên bản HTKK khác nhau
thì mẫu khác nhau — làm tờ khai bằng phiên bản nào thì lấy mẫu của phiên bản đó.

⇒ **Đừng tự dựng mẫu bảng kê từ trí nhớ.** Hỏi người dùng gửi file mẫu từ máy cài HTKK, rồi điền
vào đúng cấu trúc đó. Nếu họ đã từng gửi, cấu trúc đã được ghi trong `quy-uoc/phan-mem.md`.

Lỗi HTKK/eTax hay gặp và nguyên nhân thật:

| Lỗi | Nguyên nhân thường gặp |
|---|---|
| "Sai định dạng XML" / không kết xuất được | HTKK cũ chưa cập nhật biểu mẫu; hoặc lưu vào thư mục hệ thống bị hạn chế quyền |
| "Phiên bản XML trên tờ khai không đúng" | Dùng bản HTKK cũ |
| "Tờ khai không đúng định dạng với XSD" | Biểu mẫu cũ; với tờ khai GTGT nhiều hóa đơn thì nên kết xuất Excel, cài lại HTKK, rồi tải lại bảng kê |
| "Dữ liệu không hợp lệ" | Ký tự lạ trong ô: dấu thập phân sai, số âm sai quy ước |

Khuyến nghị nói với người dùng: lưu tờ khai ra ổ D hoặc Desktop (tránh `Program Files`), tên file
không có ký tự đặc biệt và **không dấu**, và cập nhật HTKK từ `gdt.gov.vn` trước mỗi kỳ khai.

## Nhập liệu vào MISA / Fast / Bravo

Mỗi phần mềm có mẫu nhập khẩu riêng và đổi theo phiên bản. Cách làm an toàn giống HTKK: **xin file
mẫu từ chính phần mềm người dùng đang dùng**, ghi cấu trúc vào `quy-uoc/phan-mem.md`, rồi điền theo.

Vài điểm chung đáng nhớ:
- Cột ngày phải đúng định dạng phần mềm mong đợi, thường là `dd/mm/yyyy` dạng **text** chứ không
  phải kiểu ngày của Excel.
- Mã đối tượng / mã khách hàng phải khớp **chính xác** với danh mục đã khai trong phần mềm.
  Sai một ký tự là dòng đó bị bỏ qua khi nhập.
- Không để dòng trống giữa vùng dữ liệu — nhiều trình nhập khẩu dừng ở dòng trống đầu tiên.

## Làm sạch dữ liệu lộn xộn

File kế toán thật thường không sạch: tiêu đề nằm ở dòng 5 chứ không phải dòng 1, có dòng tổng cộng
chen giữa, ô gộp (merged cells), sheet ẩn, cột trống xen kẽ.

Trình tự nên theo:

1. **Nhìn trước.** Đọc 20 dòng đầu để tìm dòng tiêu đề thật. Đừng giả định `header=0`.
2. **Bỏ dòng tổng cộng** — nhận diện qua ô đầu chứa `Tổng`, `Cộng`, `Tổng cộng`, hoặc dòng có
   ô khoá trống mà ô số có giá trị. Nếu gộp nhầm dòng tổng vào dữ liệu thì mọi con số nhân đôi.
3. **Gỡ ô gộp** — openpyxl đọc ô gộp trả giá trị ở ô trái trên, các ô còn lại là `None`. Điền
   xuống (forward fill) nếu đó là cột phân nhóm.
4. **Chuẩn hoá** bằng `chuan_hoa.py`.
5. **Kiểm lại tổng**: tổng sau khi làm sạch có khớp dòng "Tổng cộng" đã bỏ đi không? Đây là phép
   kiểm rẻ nhất và bắt được hầu hết lỗi làm sạch.

Bước 5 quan trọng: nếu tổng không khớp, nghĩa là đã bỏ sót hoặc nhân đôi dòng nào đó. Báo cho
người dùng thay vì lặng lẽ giao file sai.

## Lệnh

```bash
chuan_hoa.py <file.xlsx|csv> --ra sach.csv
chuan_hoa.py <file.xlsx> --cot-tien "tien_hang,tien_thue" --cot-ngay "ngay" --cot-mst "mst_ban"
```

`chuan_hoa.py` cũng dùng được như thư viện: `from chuan_hoa import so_vn, ngay_vn, chuan_mst, nfc`.
