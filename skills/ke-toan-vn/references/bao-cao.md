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

## Báo cáo định kỳ dựng từ mẫu kỳ trước

Việc hay gặp nhất trong kế toán quản trị: mỗi tháng lập lại đúng một bộ báo cáo, chỉ thay dữ liệu.
Đừng dựng lại từ mô tả — **nhân bản nguyên sheet của kỳ trước** (giữ cả công thức lẫn định dạng)
rồi đặt dữ liệu kỳ mới vào cùng workbook. Người dùng đã có lý do cho từng ô; xem nguyên tắc 4
trong `SKILL.md`. Script `bao_cao_khoa.py` làm việc này cho bộ báo cáo doanh thu/chia tiền công
theo khoa của bệnh viện; cách làm bên dưới áp dụng chung.

**Kiểm chứng bằng cách tái tạo kỳ trước.** Trước khi tin số kỳ mới, chạy đúng quy trình đó trên
dữ liệu của *kỳ mẫu* rồi so từng ô với file gốc. Khớp hết thì mới tin. Đây là phép thử duy nhất
phát hiện được lỗi ánh xạ cột — loại lỗi vẫn ra số trông hợp lý nên đọc bằng mắt không thấy.

Năm cái bẫy đã gặp thật khi làm việc này:

1. **Công thức nhân bản trỏ cột theo chữ cái.** `SUMIFS(DLBC!$AE:$AE; DLBC!$AP:$AP; ...)` sẽ cộng
   sai cột nếu bản kết xuất kỳ mới đổi thứ tự cột, mà vẫn ra một con số hợp lý. **So thứ tự tiêu đề
   cột của kỳ mới với kỳ mẫu và dừng nếu lệch.** Đừng cố tự ánh xạ lại.

2. **Dòng liệt kê danh mục sẽ thiếu khi kỳ mới phát sinh mục mới.** Báo cáo thường có nhóm liệt kê
   từng hạng mục (từng loại xét nghiệm, từng dịch vụ). Kỳ mới có hạng mục mà mẫu chưa có dòng thì
   tiền của nó **rơi ra ngoài dòng TỔNG CỘNG mà không ai thấy**. Luôn đối chiếu tập hạng mục có phát
   sinh với tập nhãn trong mẫu, và cảnh báo phần thiếu.

3. **Liên kết ngoài trong mẫu thường đã hỏng.** Ô kiểu `=D24-[2]BHYT!AA1` giữ giá trị cache của
   workbook khác; mở mà không có file đó bên cạnh thì cache thường bằng 0, nên dòng "chênh lệch"
   báo lệch bằng đúng cả doanh thu thay vì 0. `GETPIVOTDATA` trỏ vào pivot không mang sang cũng vậy.
   Bỏ các dòng đó và thay bằng **đối chiếu tự thân trong cùng file** (`=SUM(<sheet dữ liệu>!$AF:$AF)`
   so với dòng tổng), rồi nói rõ đã thay gì.

4. **Có khối không suy ra được từ dữ liệu.** Một số phần lấy từ sheet nhập tay (danh sách do bộ phận
   khác lập). Kiểm bằng cách thử tìm đơn giá của khối đó trong dữ liệu gốc: không có dòng nào khớp
   thì đúng là nhập tay. Khi đó **để trống hoặc 0 kèm ghi chú nhìn thấy được ngay cạnh ô** — đừng
   chép số kỳ trước sang, và đừng im lặng. Xem nguyên tắc 2 trong `SKILL.md`.

5. **Sheet trung gian có thể suy lại được — nhưng phải chứng minh.** Nhiều sheet phụ chỉ là một bộ
   lọc của dữ liệu gốc, sinh lại được để khỏi phải xin thêm file. Trước khi dựa vào đó, **đối chiếu
   bản sinh với bản người dùng tự lọc của kỳ mẫu**: khớp cả số dòng lẫn từng cặp khoá thì mới dùng.

Cuối cùng: mẫu kỳ trước có thể chứa lỗi sẵn (thiếu công thức ở một vài dòng, sót một hạng mục).
**Giữ nguyên công thức của mẫu, báo lỗi ra cho người dùng, đừng tự sửa** — nguyên tắc 4. Nhưng phải
nói, vì kỳ sau họ sẽ lại nhân bản đúng cái lỗi đó.

## Báo cáo quản trị

Không có mẫu bắt buộc — làm theo yêu cầu của người dùng. Vài điều thường được đánh giá cao:

- Số liệu kỳ này đặt cạnh kỳ trước, kèm chênh lệch tuyệt đối và %.
- Đơn vị tiền thống nhất và ghi rõ ở tiêu đề (`Đơn vị: đồng` hay `Đơn vị: triệu đồng`).
- Nguồn dữ liệu và ngày chốt số ghi ngay trên báo cáo.
- Điều bất thường được nêu bằng chữ, không chỉ để người đọc tự tìm trong bảng số.
