# Bóc tách hóa đơn điện tử

> **Khung pháp lý hiện hành: NĐ 254/2026/NĐ-CP + TT 91/2026/TT-BTC**, hiệu lực 01/7/2026, chi tiết
> Luật Quản lý thuế 108/2025/QH15. Hai văn bản này đã **thay thế NĐ 123/2020 và NĐ 70/2025** —
> đừng dẫn hai văn bản cũ làm căn cứ đang áp dụng. Tra `bo_nho.py tra "hoa don"` trước khi trích
> điều khoản cụ thể.

## Nguyên tắc đầu tiên: XML thắng PDF

**Bản XML là bản gốc có giá trị pháp lý; PDF chỉ là "bản thể hiện"**. Bản giấy chuyển đổi chỉ có
giá trị lưu giữ để ghi sổ, không có hiệu lực giao dịch. Khi có cả hai, luôn đọc XML; PDF chỉ dùng
khi không có XML.

Khác biệt thực tế rất lớn:

| | XML | PDF |
|---|---|---|
| Độ tin cậy | Trường có nhãn rõ ràng, đọc chắc chắn | Phải suy từ vị trí chữ, dễ sai |
| Thuế suất từng dòng | Có sẵn | Thường phải suy ngược từ tiền thuế |
| Hàng nhiều dòng | Đầy đủ | Hay bị cắt khi bảng qua trang |
| Chữ ký số | Kiểm được | Không |

⇒ Trong bảng kết quả **luôn có cột `nguon` ghi `XML` hay `PDF`**. Kế toán cần biết dòng nào chắc
chắn, dòng nào phải kiểm lại. Đây là ứng dụng cụ thể của nguyên tắc "không bịa số".

## Cấu trúc XML theo QĐ 1450/QĐ-TCT

Chuẩn dữ liệu do Tổng cục Thuế quy định tại **QĐ 1450/QĐ-TCT** (có các quyết định sửa đổi, ví dụ
1510/QĐ-TCT). Khung cơ bản:

```
<HDon>
  <DLHDon>                          Dữ liệu hóa đơn
    <TTChung>                       Thông tin chung
      <KHMSHDon>1</KHMSHDon>        Ký hiệu mẫu số (1=GTGT, 2=bán hàng, 3=tài sản công, 4=dự trữ QG)
      <KHHDon>C25TAA</KHHDon>       Ký hiệu hóa đơn
      <SHDon>00000123</SHDon>       Số hóa đơn — 8 chữ số (khoản 3 Điều 10 NĐ 123/2020)
      <NLap>2026-07-15</NLap>       Ngày lập
      <DVTTe>VND</DVTTe>            Đơn vị tiền tệ
      <TGia>1</TGia>                Tỷ giá
    </TTChung>
    <NDHDon>                        Nội dung hóa đơn
      <NBan>                        Người bán
        <Ten>...</Ten>
        <MST>0100109106</MST>
        <DChi>...</DChi>
      </NBan>
      <NMua>                        Người mua
        <Ten>...</Ten>
        <MST>...</MST>
        <CCCDan>...</CCCDan>        Số định danh cá nhân (dùng thay MST với cá nhân)
      </NMua>
      <DSHHDVu>                     Danh sách hàng hóa dịch vụ
        <HHDVu>
          <STT>1</STT>
          <THHDVu>Tên hàng</THHDVu>
          <DVTinh>Cái</DVTinh>
          <SLuong>10</SLuong>
          <DGia>100000</DGia>
          <ThTien>1000000</ThTien>  Thành tiền chưa thuế
          <TSuat>10%</TSuat>        Thuế suất — CÓ THỂ là "KCT", "KKKNT", "\\" (xem dưới)
        </HHDVu>
      </DSHHDVu>
      <TToan>                       Tổng thanh toán
        <THTTLTSuat>                Tổng hợp theo từng loại thuế suất
          <LTSuat>
            <TSuat>10%</TSuat>
            <ThTien>1000000</ThTien>
            <TThue>100000</TThue>
          </LTSuat>
        </THTTLTSuat>
        <TgTCThue>1000000</TgTCThue>   Tổng tiền chưa thuế
        <TgTThue>100000</TgTThue>      Tổng tiền thuế
        <TgTTTBSo>1100000</TgTTTBSo>   Tổng tiền thanh toán bằng số
      </TToan>
    </NDHDon>
  </DLHDon>
  <DSCKS>...</DSCKS>                Danh sách chữ ký số
</HDon>
```

**Cảnh báo về tên thẻ:** nhà cung cấp hóa đơn khác nhau đôi khi lệch chút ít, và có bản bọc thêm
lớp `<TDiep>` (thông điệp) bên ngoài `<HDon>`. Nên **tìm thẻ theo tên bất kể độ sâu**
(`.//THHDVu`) thay vì đi theo đường dẫn tuyệt đối. `doc_hoa_don.py` đã làm vậy.

**Thuế suất không phải lúc nào cũng là số.** Các giá trị hay gặp:

| Giá trị | Nghĩa | Xử lý |
|---|---|---|
| `0%`, `5%`, `8%`, `10%` | Thuế suất thường | Chuyển thành số |
| `KCT` | Không chịu thuế | Giữ nguyên chuỗi, tiền thuế = 0 |
| `KKKNT` | Không kê khai, nộp thuế | Giữ nguyên chuỗi |
| `\` hoặc `KHAC` | Khác | Giữ nguyên, cảnh báo cho người dùng |

Đừng ép về 0 — kế toán phân biệt rõ "thuế suất 0%" (hàng xuất khẩu, được khấu trừ đầu vào) và
"không chịu thuế" (không được khấu trừ). Ép sai làm hỏng tờ khai.

Mức **8%** xuất hiện nhiều do các đợt giảm thuế GTGT — hoàn toàn hợp lệ, đừng coi là lỗi.

## Đọc từ PDF khi không có XML

Dùng `pdfplumber` (skill `pdf` có sẵn hướng dẫn). Chiến lược:

1. `extract_text()` trước, tìm theo **nhãn tiếng Việt** — các nhãn phổ biến, không phân biệt hoa
   thường và có/không dấu: `Mã số thuế` / `MST`, `Số hóa đơn` / `Số HĐ`, `Ký hiệu`, `Ngày`,
   `Cộng tiền hàng` / `Tổng tiền chưa thuế`, `Tiền thuế GTGT`, `Tổng cộng tiền thanh toán`.
2. `extract_tables()` cho phần danh mục hàng hóa.
3. Nếu `extract_text()` trả về gần như rỗng → PDF là ảnh scan → cần OCR. Dùng `tesseract` với
   **`-l vie`**. Không có gói ngôn ngữ `vie` thì kết quả là rác — chạy `bootstrap.sh` để cài
   `tesseract-lang`.

**Số tiền kiểu Việt Nam**: `1.234.567` là một triệu hai, không phải 1.234567. Dấu chấm là phân cách
nghìn, dấu phẩy là thập phân. `chuan_hoa.py` xử lý việc này — đừng tự parse bằng `float()`.

**Ngày**: `dd/mm/yyyy`. `15/07/2026` là 15 tháng 7, không phải tháng 15.

## Tự kiểm trước khi giao

Sau khi bóc tách, kiểm ba điều — rẻ và bắt được hầu hết lỗi:

1. **Cân đối từng hóa đơn**: `tiền hàng + tiền thuế = tổng thanh toán` (cho phép lệch ±1đ do làm tròn).
2. **Thuế suất khớp**: `tiền hàng × thuế suất ≈ tiền thuế`. Lệch nhiều → đọc sai một trong hai.
3. **MST hợp lệ**: chạy `kiem_tra_mst.py`. Sai checksum thường là do OCR nhầm số, không hẳn hóa đơn giả.

Ngoài ra báo ngay nếu thấy: **hóa đơn trùng số**, **ngày ngoài kỳ đang làm**, **MST bên mua không
phải công ty của người dùng**. Đây là những thứ kế toán muốn biết nhất và thường không nghĩ để hỏi.

## Lệnh

```bash
doc_hoa_don.py <thư mục hoặc file> --ra ket_qua.csv
doc_hoa_don.py <thư mục> --ra ket_qua.json --dinh-dang json
```

Kết quả gồm các cột: `nguon`, `tep`, `ky_hieu`, `so_hd`, `ngay`, `mst_ban`, `ten_ban`, `mst_mua`,
`ten_mua`, `tien_hang`, `thue_suat`, `tien_thue`, `tong_cong`, `canh_bao`.

Cột `canh_bao` là nơi ghi mọi thứ đáng ngờ. **Đọc nó trước khi báo cáo kết quả cho người dùng.**
