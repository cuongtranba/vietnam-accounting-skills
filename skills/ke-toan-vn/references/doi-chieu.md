# Đối chiếu số liệu

Đối chiếu là việc kế toán làm nhiều nhất và cũng mệt nhất: bảng kê mua vào với sổ chi tiết, bảng kê
bán ra với TK 511, sao kê ngân hàng với sổ quỹ, công nợ với xác nhận của khách.

Máy làm phần so khớp; người quyết định chênh lệch nào là vấn đề. Việc của skill là **tìm đủ và
không báo giả**.

## Chọn khoá đối chiếu

Khoá sai thì mọi thứ sau đó vô nghĩa. Chọn theo bối cảnh:

| Việc | Khoá nên dùng |
|---|---|
| Hóa đơn ↔ sổ sách | `MST bên bán` + `ký hiệu` + `số hóa đơn` |
| Sao kê ngân hàng ↔ sổ quỹ | `ngày` + `số tiền` (thường không có số chứng từ chung) |
| Công nợ | `mã khách` hoặc `MST` + `số chứng từ` |

Chỉ dùng **số hóa đơn** làm khoá là sai lầm phổ biến: hai nhà cung cấp khác nhau hoàn toàn có thể
cùng phát hành số `00000123`. Phải ghép với MST.

Khi không có khoá chung (trường hợp sao kê ngân hàng), đối chiếu theo `ngày + số tiền` rồi chấp nhận
rằng kết quả là **gợi ý**, không phải kết luận — nói rõ điều này với người dùng.

## Ba nhóm kết quả

1. **Chỉ có ở bảng A** — có hóa đơn nhưng chưa vào sổ, hoặc vào sổ kỳ khác.
2. **Chỉ có ở bảng B** — đã ghi sổ nhưng thiếu hóa đơn (nghiêm trọng hơn, ảnh hưởng khấu trừ).
3. **Có ở cả hai nhưng lệch tiền** — kèm mức lệch tuyệt đối và tương đối.

Ngoài ra luôn kiểm **trùng lặp trong từng bảng**. Một hóa đơn vào sổ hai lần không xuất hiện ở ba
nhóm trên nhưng làm sai tổng — và đây là lỗi rất hay gặp khi nhập liệu thủ công.

## Ngưỡng làm tròn

Chênh 1–2 đồng do làm tròn thuế là bình thường, không phải sai sót. Báo tất cả thì người dùng phải
lọc tay hàng trăm dòng vô nghĩa và sẽ bỏ qua luôn cả những dòng thật.

Mặc định `--nguong 1` (đồng). Cho gói lớn có thể nới lên. **Nhưng luôn báo tổng số dòng bị bỏ qua
do dưới ngưỡng** — người dùng cần biết mình đang không nhìn thấy gì.

## Bẫy dữ liệu Việt Nam

Trước khi so khớp, **luôn chạy `chuan_hoa.py`** trên cả hai bảng. Ba thứ làm hỏng đối chiếu:

**Unicode NFC vs NFD.** macOS lưu `ế` thành `e` + dấu rời (NFD), Windows lưu thành một ký tự (NFC).
Hai chuỗi nhìn giống hệt nhau trên màn hình nhưng `==` trả về `False`. Đây là nguyên nhân số một
của "VLOOKUP không ra kết quả mà em nhìn rõ ràng là giống nhau". Chuẩn hoá về NFC.

**Số kiểu Việt Nam.** `1.234.567,89` — dấu chấm phân cách nghìn, dấu phẩy thập phân. `float()` của
Python đọc `1.234.567` là lỗi, và đọc `1.234` thành 1.234 (một phẩy hai) thay vì 1234.

**MST lẫn ký tự.** `MST: 0100109106 ` hay `0100109106-001` — cắt sạch trước khi so.

Ngoài ra: khoảng trắng thừa, chữ hoa/thường trong tên, và MST có thể là số hoặc chuỗi tuỳ cách
Excel lưu (MST bắt đầu bằng `0` mà lưu dạng số thì mất số 0 đầu — **luôn đọc MST dạng chuỗi**).

## Báo cáo kết quả

Người dùng cần biết ba điều, theo thứ tự:

1. **Tổng quan**: bảng A có bao nhiêu dòng, bảng B bao nhiêu, khớp bao nhiêu, lệch bao nhiêu,
   tổng tiền hai bên và chênh lệch tổng.
2. **Danh sách chênh lệch**, sắp xếp theo **số tiền giảm dần** — chênh lệch lớn quan trọng hơn,
   người dùng thường chỉ có thời gian xử lý vài dòng đầu.
3. **Nhận định**: chênh lệch tổng có giải thích được bằng các dòng đã liệt kê không? Nếu tổng lệch
   5 triệu mà các dòng tìm được chỉ cộng lại 3 triệu thì **còn 2 triệu chưa giải thích được** —
   phải nói ra, đó là dấu hiệu khoá đối chiếu chưa đúng hoặc còn lỗi chưa bắt được.

Điểm 3 là thứ phân biệt một báo cáo hữu ích với một danh sách vô hồn. Luôn tự hỏi "các chênh lệch
tôi tìm được có cộng lại thành chênh lệch tổng không?" trước khi giao việc.

## Lệnh

```bash
doi_chieu.py bang_a.xlsx bang_b.xlsx \
    --khoa "mst_ban,so_hd" \
    --so-sanh "tong_cong" \
    --nguong 1 \
    --ra ket_qua.xlsx
```

Nếu tên cột hai bảng khác nhau, dùng `--khoa-a` và `--khoa-b` để ánh xạ.
