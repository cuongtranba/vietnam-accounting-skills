# Bảng kê, tờ khai, báo cáo

> Mọi mẫu biểu và chỉ tiêu đều thay đổi theo văn bản. **Tra `bo_nho.py tra` trước khi dựng bất kỳ
> mẫu nào**, và ưu tiên xin file mẫu thật từ phần mềm người dùng đang dùng thay vì dựng lại từ mô tả.

## Nguyên tắc chung

Kế toán không cần một file đẹp — họ cần một file **nộp được** và **kiểm được**. Ba yêu cầu:

1. **Nộp được**: đúng cấu trúc phần mềm/cơ quan thuế mong đợi. Sai một cột là phải làm lại.
2. **Kiểm được**: mỗi con số tổng hợp phải lần ngược về chi tiết. Dùng **công thức Excel**, không
   dán giá trị đã tính bằng Python — người dùng cần bấm vào ô để xem nó cộng từ đâu.
3. **Có dấu vết**: một sheet phụ ghi nguồn dữ liệu, ngày lập, phạm vi kỳ, và các giả định.

Điểm 2 lấy từ skill `xlsx` và đặc biệt đúng ở đây: kế toán sẽ bị hỏi "số này ở đâu ra?" khi quyết
toán hoặc thanh tra. Một ô chứa `=SUMIFS(...)` trả lời được câu đó; một ô chứa `1234567` thì không.

Nhớ chạy `recalc.py` của skill `xlsx` sau khi ghi công thức, và tránh `XLOOKUP`/`FILTER`/`UNIQUE`
(LibreOffice không tính được, kết quả bị cắt âm thầm).

## Bảng kê mua vào / bán ra

Cấu trúc tối thiểu của một bảng kê hóa đơn — dùng làm khung khi người dùng chưa có mẫu riêng:

| Cột | Ghi chú |
|---|---|
| STT | |
| Ký hiệu hóa đơn | |
| Số hóa đơn | 8 chữ số, lưu dạng chuỗi |
| Ngày lập | `dd/mm/yyyy` |
| Tên người bán / mua | |
| MST | **dạng chuỗi**, giữ số 0 đầu |
| Doanh số / tiền hàng chưa thuế | |
| Thuế suất | Chuỗi nếu là `KCT`/`KKKNT` |
| Tiền thuế GTGT | |
| Tổng thanh toán | |
| Ghi chú | Nơi ghi cảnh báo, không để trống dữ liệu quan trọng |

Nhóm theo thuế suất khi tổng hợp — tờ khai cần số liệu tách theo từng mức (0%, 5%, 8%, 10%,
không chịu thuế). Đừng gộp chung.

Để nhập vào HTKK thì phải theo **đúng mẫu của phiên bản HTKK đang dùng**, không phải khung trên —
xem `references/excel-vn.md`.

## Tờ khai thuế GTGT (mẫu 01/GTGT)

Mẫu và chỉ tiêu theo phụ lục **TT 80/2021/TT-BTC** và các văn bản sửa đổi. **Tra lại trước khi dùng** —
Luật GTGT 48/2024 và 149/2025 đã thay đổi nhiều nội dung và mẫu biểu có thể đã cập nhật theo.

Việc skill nên làm: **chuẩn bị số liệu đầu vào** cho tờ khai (tổng hợp bảng kê theo từng mức thuế
suất, tính thuế đầu vào được khấu trừ, đối chiếu với sổ), rồi để người dùng nhập vào HTKK.
Skill **không** nên tự dựng file XML tờ khai — HTKK làm việc đó và cơ quan thuế chỉ nhận XML do
HTKK kết xuất đúng phiên bản.

Điểm dễ sai hiện nay khi rà điều kiện khấu trừ: **ngưỡng thanh toán không dùng tiền mặt đã hạ từ
20 triệu xuống 5 triệu** (Luật 48/2024 + NĐ 181/2025). Khi lọc các hóa đơn cần chứng từ thanh toán
không tiền mặt, dùng mốc 5 triệu (đã gồm thuế) — nhiều tài liệu cũ và thói quen nghề vẫn nói 20 triệu.

## Bảng cân đối phát sinh

Cấu trúc: mỗi tài khoản một dòng, các cột `Số dư đầu kỳ (Nợ/Có)`, `Phát sinh trong kỳ (Nợ/Có)`,
`Số dư cuối kỳ (Nợ/Có)`.

Hai phép kiểm bắt buộc, làm bằng công thức ngay trong file:

1. **Tổng phát sinh Nợ = Tổng phát sinh Có**
2. **Dư đầu + Phát sinh Nợ − Phát sinh Có = Dư cuối** (với tài khoản tính chất Nợ; đảo dấu với
   tài khoản tính chất Có)

Nếu không cân, **nói ngay và chỉ rõ tài khoản nào lệch** — đừng giao file không cân mà không cảnh báo.

Hệ thống tài khoản theo TT 200 (hoặc TT 133 với DNNVV). Nhớ rằng TT 200 cho phép doanh nghiệp tự mở
tài khoản cấp 2, 3 — nên tài khoản lạ trong sổ của người dùng chưa chắc là sai. Tra
`quy-uoc/tai-khoan.md` trước khi kết luận.

## Báo cáo đánh giá HSDT

Theo mẫu tại **TT 80/2025/TT-BTC**. Xem `references/dau-thau.md` — và nhớ nguyên tắc: skill chuẩn bị
số liệu và bảng so sánh, tổ chuyên gia viết kết luận và ký.

## Báo cáo quản trị

Không có mẫu bắt buộc — làm theo yêu cầu của người dùng. Vài điều thường được đánh giá cao:

- Số liệu kỳ này đặt cạnh kỳ trước, kèm chênh lệch tuyệt đối và %.
- Đơn vị tiền thống nhất và ghi rõ ở tiêu đề (`Đơn vị: đồng` hay `Đơn vị: triệu đồng`).
- Nguồn dữ liệu và ngày chốt số ghi ngay trên báo cáo.
- Điều bất thường được nêu bằng chữ, không chỉ để người đọc tự tìm trong bảng số.
