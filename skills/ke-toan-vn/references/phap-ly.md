# Tra cứu văn bản pháp luật

> **Bản đồ này lập ngày 2026-09-10, phần chế độ kế toán và hóa đơn cập nhật 2026-10-16.** Nó chỉ dùng để biết *nên tra cái gì* và *văn bản nào từng
> thay văn bản nào* — **không** dùng làm căn cứ trả lời. Trước khi nói bất kỳ con số nào cho
> người dùng, kiểm qua `bo_nho.py tra <chủ đề>`, và tra web nếu ghi chú đã hết hạn.

## Vì sao phải cẩn thận đến vậy

Hai cái bẫy có thật, đã kiểm chứng:

**Bẫy 1 — trí nhớ mô hình giữ con số cũ.** Ngưỡng doanh thu không chịu thuế GTGT của hộ kinh doanh:

| Mức | Văn bản | Hiệu lực | Tình trạng |
|---|---|---|---|
| 100 triệu/năm | quy định cũ | tới hết 2025 | ❌ |
| 200 triệu/năm | Luật 48/2024/QH15 | dự kiến 01/01/2026 | ❌ bị đè trước khi kịp áp dụng |
| 500 triệu/năm | Luật 149/2025/QH15, rồi NĐ 68/2026/NĐ-CP (05/3/2026) | 01/01/2026 | ❌ đã bị sửa |
| **1 tỷ/năm** | **NĐ 141/2026/NĐ-CP (29/4/2026)** sửa NĐ 68/2026 | **01/01/2026** (hồi tố) | ✅ hiện hành |

**Bốn con số trong hai năm.** Trả lời từ trí nhớ gần như chắc chắn sai — và ngay cả bản đồ này
cũng đã từng sai: bản viết ngày 2026-09-10 ghi 500 triệu là mức hiện hành, không biết NĐ 141/2026
đã nâng lên 1 tỷ từ tháng 4. Chính quy tắc "phải hỏi thêm văn bản còn hiệu lực không" ở dưới
mới là thứ bắt được.

Lưu ý cấu trúc quan trọng: từ 2026 con số này **không còn nằm trong luật** mà được giao cho
Chính phủ quy định bằng nghị định. Nghĩa là nó có thể đổi nhanh hơn trước — theo dõi nghị định,
đừng chỉ theo dõi luật.

**Bẫy 2 — công cụ tìm kiếm đẩy văn bản hết hiệu lực lên đầu.** Tra "quy trình chấm thầu, sửa lỗi,
hiệu chỉnh sai lệch" thì kết quả hàng đầu dẫn **NĐ 63/2014** và **NĐ 24/2024** — cả hai đã bị thay
bởi NĐ 214/2025. Các trang blog thường không cập nhật, và chúng xếp hạng SEO cao hơn cổng chính phủ.

⇒ Khi tra một văn bản, **luôn hỏi thêm hai câu**: (a) văn bản này còn hiệu lực không? (b) đã bị
văn bản nào sửa hoặc thay chưa? Ghi kết quả vào trường `thay_the_boi` của ghi chú bộ nhớ.

## Thứ tự ưu tiên nguồn

1. **`vanban.chinhphu.vn`** — cổng văn bản Chính phủ, toàn văn chính thức.
2. **`gdt.gov.vn`** / **`mof.gov.vn`** — Thuế và Bộ Tài chính, có phần hỏi đáp chính sách hữu ích.
3. **`thuvienphapluat.vn`** — mạnh nhất về **bản hợp nhất** và mục "văn bản bị thay thế / sửa đổi".
   Đây thường là nơi trả lời nhanh nhất câu "còn hiệu lực không".
4. Blog nhà cung cấp (MISA, einvoice, easyinvoice, meinvoice, dauthau.asia…) — **chỉ để định hướng**.
   Chúng viết dễ hiểu và thường lên đầu kết quả, nhưng hay lạc hậu và đôi khi sai. Mọi con số lấy
   từ đây phải đối chiếu lại với văn bản gốc trước khi ghi `do_tin_cay: cao`.

Nếu không đối chiếu được với nguồn `.gov.vn`, ghi `do_tin_cay: trung_binh` và **nói thẳng với người
dùng là cần kiểm tra lại** trước khi dùng cho việc quan trọng.

## Bản đồ văn bản (tình trạng ngày 2026-09-10)

### Chế độ kế toán — chọn theo LOẠI ĐƠN VỊ và ngày BẮT ĐẦU năm tài chính

Đừng mặc định TT 200. Chạy `che_do_ke_toan.py` — nó chọn theo bảng dưới, kèm trích dẫn, và trả
`can_xac_nhan` (mã thoát 2) khi thiếu thông tin hoặc văn bản để ngỏ; khi đó HỎI người dùng.

| Văn bản | Đối tượng | Áp dụng | Căn cứ (đã đọc Công báo 2026-10-16) |
|---|---|---|---|
| **TT 99/2025/TT-BTC** | Doanh nghiệp mọi lĩnh vực, thành phần (trừ TCTD — theo NHNN) | Năm tài chính **bắt đầu từ hoặc sau 01/01/2026** | Điều 31 khoản 1; thay TT 200, 75/2015, 53/2016, 195/2012. Khoản 2: phần cổ phần hóa DNNN của TT 200 vẫn dùng. Khoản 3: DNNVV, cơ sở ngoài công lập được CHỌN TT 99 |
| TT 200/2014/TT-BTC | Doanh nghiệp | Năm tài chính bắt đầu **trước** 01/01/2026 — dùng cho CẢ năm đó (năm 01/10/2025–30/09/2026 vẫn TT 200) | Suy từ Điều 31 TT 99 |
| TT 133/2016/TT-BTC | DN nhỏ và vừa — được chọn TT 133 hoặc TT 99 | — | Không có trong danh sách TT 99 thay; TT 58 Điều 4 khoản 3 vẫn dẫn chiếu (chưa đọc văn bản gốc) |
| **TT 58/2026/TT-BTC** | DN siêu nhỏ; hộ/cá nhân kinh doanh được chọn | Năm tài chính **bắt đầu từ hoặc sau 01/7/2026** | Điều 12 khoản 1; khoản 2: TT 132/2018 hết hiệu lực từ 01/7/2026 |
| TT 132/2018/TT-BTC | DN siêu nhỏ | Năm tài chính kết thúc trước 01/7/2026 | — |
| **TT 24/2024/TT-BTC** | Cơ quan nhà nước, **đơn vị sự nghiệp công lập** (bệnh viện công) | Từ năm tài chính 2025 | Điều 2 khoản 1 điểm b: ĐVSNCL tự bảo đảm chi thường xuyên VÀ chi đầu tư **được cơ quan có thẩm quyền cho phép** thì dùng chế độ DN (vẫn lập báo cáo quyết toán kinh phí theo Phụ lục III nếu có NSNN, viện trợ, vay nợ, phí được để lại). Điều 13: thay TT 107/2017 |

Ba bẫy:

- **"Bệnh viện" không nói lên chế độ.** Bệnh viện công là ĐVSNCL (TT 24/2024, trừ ngoại lệ trên);
  bệnh viện tư là doanh nghiệp (TT 99/2025 hoặc TT 133). Hỏi loại đơn vị, mức tự chủ, và văn bản
  cho phép — đừng suy từ tên.
- **DN siêu nhỏ có năm tài chính vắt qua 01/7/2026** (vd năm dương lịch 2026): TT 132 hết hiệu lực
  giữa năm mà TT 58 chưa áp dụng cho năm đó. Văn bản không nói rõ — cần người có chuyên môn hoặc
  hướng dẫn của Bộ Tài chính.
- **Số liệu năm cũ không đổi theo luật mới.** Báo cáo năm 2025 theo TT 200 vẫn là TT 200.

TT 99 (như TT 200) cho phép doanh nghiệp **tự mở tài khoản chi tiết** và tự thiết kế mẫu sổ — nên
đừng ngạc nhiên khi sổ của người dùng không giống mẫu chuẩn. Xem `quy-uoc/` trong bộ nhớ. Với năm
áp dụng TT 99, tra hệ thống tài khoản ở Phụ lục II của TT 99 — đừng dùng danh mục tài khoản TT 200
từ trí nhớ (bảng này chưa đối chiếu hai danh mục).

Với các năm áp dụng TT 200: tài khoản đã bỏ so với QĐ 15 cũ gồm 129, 139, 142, 144, 159, 311, 315,
342, 351, 415, 431, 512, 531, 532; gộp 142+242 → **242**, 521+531+532 → **521**; thêm mới 171, 353.

| Văn bản | Nội dung | Ghi chú |
|---|---|---|
| Luật Kế toán 88/2015/QH13 | Khung gốc | Sửa đổi bởi Luật ngày 29/11/2024 (dẫn trong căn cứ của TT 99) |

### Thuế GTGT

| Văn bản | Nội dung | Hiệu lực |
|---|---|---|
| Luật 48/2024/QH15 | Luật Thuế GTGT (thay luật cũ) | 01/07/2025 |
| Luật 149/2025/QH15 | Sửa Luật GTGT, đồng bộ Luật Quản lý thuế | 01/01/2026 |
| NĐ 181/2025/NĐ-CP | Hướng dẫn Luật GTGT | |
| TT 80/2021/TT-BTC | Hướng dẫn Luật Quản lý thuế, phụ lục mẫu tờ khai | |

### Hộ, cá nhân kinh doanh (mảng biến động nhanh nhất)

| Văn bản | Nội dung | Hiệu lực |
|---|---|---|
| NĐ 68/2026/NĐ-CP (05/3/2026) | Chính sách và quản lý thuế với hộ, cá nhân kinh doanh | 05/03/2026 |
| **NĐ 141/2026/NĐ-CP (29/4/2026)** | **Sửa NĐ 68/2026: nâng ngưỡng 500 triệu → 01 tỷ đồng** ở Điều 3, 4, 8, 9, 10, 11, 12, 17, 18; đồng thời sửa NĐ 320/2025 về thuế TNDN | **01/01/2026 (hồi tố)** |

Kèm theo mức 1 tỷ: hộ có doanh thu **trên** 1 tỷ/năm bắt buộc dùng hóa đơn điện tử có mã cơ quan
thuế hoặc HĐĐT khởi tạo từ máy tính tiền; phải đăng ký trong 30 ngày kể từ ngày cuối kỳ tính thuế
có doanh thu lũy kế vượt ngưỡng. Ngưỡng chỉ được trừ **một lần** dù có nhiều địa điểm/hợp đồng.
Hộ đã kê khai nộp thuế theo mức 500 triệu được xử lý số nộp thừa theo Điều 12 NĐ 68/2026.

Điểm dễ sai nhất hiện nay: **ngưỡng thanh toán không dùng tiền mặt để được khấu trừ đã hạ từ
20 triệu xuống 5 triệu** (đã gồm thuế), theo Luật 48/2024 + NĐ 181/2025. Rất nhiều tài liệu và
thói quen nghề vẫn nói 20 triệu.

### Hóa đơn, chứng từ

| Văn bản | Nội dung | Hiệu lực | Tình trạng |
|---|---|---|---|
| **NĐ 254/2026/NĐ-CP** (30/6/2026) | Hóa đơn điện tử, chứng từ điện tử — chi tiết **Luật Quản lý thuế 108/2025/QH15** | **01/07/2026** | ✅ **hiện hành** |
| **TT 91/2026/TT-BTC** (30/6/2026) | Hướng dẫn NĐ 254/2026 (thay TT 32/2025) | 01/07/2026 | ✅ |
| ~~NĐ 123/2020/NĐ-CP~~ | | | ❌ **hết hiệu lực từ 01/7/2026** |
| ~~NĐ 70/2025/NĐ-CP~~ | | | ❌ **hết hiệu lực từ 01/7/2026** |
| QĐ 1450/QĐ-TCT | **Chuẩn dữ liệu XML** hóa đơn điện tử (XSD, kiểu và độ dài từng trường) | | có QĐ sửa đổi (vd 1510/QĐ-TCT); kiểm lại xem NĐ 254/2026 có ban hành chuẩn mới chưa |

⚠️ Cả NĐ 123/2020 và NĐ 70/2025 **đều đã hết hiệu lực** (Điều 43 NĐ 254/2026). Rất nhiều tài liệu
và cả file này (bản 2026-09-10) từng ghi hai văn bản đó là hiện hành — luôn kiểm lại trước khi trích.

Điểm mới đáng chú ý của NĐ 254/2026: lần đầu gom **8 trường hợp không phải dùng HĐĐT** vào một điều
(Điều 7); sửa nhiều quy định về **thời điểm lập hóa đơn** (đặt cọc dịch vụ chưa phải xuất hóa đơn;
dịch vụ cần đối soát được lập sau 7 ngày; cho lập hóa đơn tổng cuối ngày; giao dịch ban đêm;
cơ sở y tế được gộp hóa đơn cuối ngày); hóa đơn ủy nhiệm phải ghi đủ tên/địa chỉ/MST của **cả hai bên**.

Các quy định dưới đây đến từ NĐ 70/2025 — nay đã hết hiệu lực, nhưng nội dung phần lớn được kế thừa
trong NĐ 254/2026. **Kiểm lại điều khoản tương ứng trước khi dẫn:**

- **Bỏ quy định hủy hóa đơn lập sai.** Nay là điều chỉnh hoặc thay thế.
- Cho phép lập **01 hóa đơn thay thế/điều chỉnh cho nhiều hóa đơn sai** cùng tháng, cùng người mua.
- Thời điểm lập hóa đơn bán hàng = thời điểm **chuyển giao quyền sở hữu/sử dụng**, không phụ thuộc
  đã thu tiền hay chưa.
- Nội dung hóa đơn có thêm **số định danh cá nhân** của người mua (thay cho MST với cá nhân).
- Mở rộng ủy nhiệm lập hóa đơn cho cả **hộ kinh doanh, cá nhân kinh doanh**.

Pháp lý quan trọng khi làm việc với file: **hóa đơn điện tử là thông điệp dữ liệu (XML); PDF chỉ là
"bản thể hiện"**. Bản giấy chuyển đổi chỉ phục vụ ghi sổ, không có hiệu lực giao dịch (Điều 7
NĐ 123/2020; khoản 2 và điểm b.2 khoản 4 Điều 5 NĐ 254/2026). ⇒ Khi có cả XML và PDF, **luôn ưu
tiên đọc XML**.

**Văn bản nào áp cho hóa đơn nào — theo NGÀY LẬP.** Lập từ 01/7/2026: NĐ 254/2026 + TT 91/2026.
Lập trước đó: NĐ 123/2020 (đã sửa bởi NĐ 41/2022, NĐ 70/2025). Điều 44 NĐ 254 không có chuyển tiếp
chung cho hóa đơn đã lập — xét theo văn bản có hiệu lực tại ngày lập (cách hiểu về hiệu lực theo
thời gian; `doc_hoa_don.py` ghi cột `che_do_hoa_don` cho từng dòng).

**Chữ ký số.** NĐ 254 (Phụ lục, mục 6) yêu cầu chữ ký số người bán; có ngoại lệ — hóa đơn khởi tạo
từ máy tính tiền không bắt buộc chữ ký số (Điều 8 khoản 9 điểm b), tem/vé/thẻ... Người mua không
nhất thiết ký (Điều 10). Nên "không có chữ ký" là việc cần xem, không tự loại.

### Mã số thuế

| Văn bản | Nội dung |
|---|---|
| Luật Quản lý thuế 38/2019/QH14, Điều 30 khoản 2 | MST 10 số cho pháp nhân/hộ/cá nhân; 13 số cho đơn vị phụ thuộc |
| TT 105/2020/TT-BTC | Đăng ký thuế, cấu trúc MST |

Cấu trúc `N1N2 N3..N9 N10 - N11N12N13`: `N1N2` mã phân khoảng tỉnh, `N3–N9` số tăng dần,
**`N10` là chữ số kiểm tra**, `N11N12N13` số thứ tự đơn vị phụ thuộc (001–999).

Xu hướng: khi mã định danh cá nhân được cấp toàn dân thì **dùng mã định danh (12 số) thay cho MST**
với cá nhân — nên công cụ kiểm tra phải chấp nhận cả dạng 12 số.

### Đấu thầu

| Văn bản | Nội dung | Hiệu lực | Tình trạng |
|---|---|---|---|
| Luật 22/2023/QH15 | Luật Đấu thầu | 01/01/2024 | còn hiệu lực, **đã bị sửa 5 lần** |
| Luật 57/2024/QH15 | Sửa Luật Đấu thầu (cùng Luật Quy hoạch, Đầu tư, PPP) | 15/01/2025 | |
| Luật 90/2025/QH15 | Sửa Luật Đấu thầu (cùng PPP, Hải quan, thuế...) | 01/07/2025 | |
| Luật Phục hồi, phá sản 142/2025/QH15 | Sửa vài điều liên quan phá sản trong Luật Đấu thầu | 01/03/2026 | |
| Luật An ninh mạng 116/2025/QH15 | Sửa vài điều liên quan an ninh mạng | 01/07/2026 | |
| Luật Công nghệ cao 133/2025/QH15 | Sửa vài điều, thêm nhóm doanh nghiệp công nghệ cao | 01/07/2026 | |
| **Văn bản hợp nhất 74/VBHN-VPQH (2026)** | Hợp nhất đủ 5 lần sửa trên | | **dùng bản này để tra số điều**, đừng tự cộng dồn |
| **NĐ 214/2025/NĐ-CP** | Chi tiết Luật Đấu thầu, **lựa chọn nhà thầu** | **04/08/2025** | **văn bản đang áp dụng** |
| TT 79/2025/TT-BTC | Mẫu HSMT, đăng tải thông tin lên Hệ thống mạng đấu thầu quốc gia | | |
| TT 80/2025/TT-BTC | Mẫu HSYC, **báo cáo đánh giá**, báo cáo thẩm định | | |
| ~~NĐ 63/2014/NĐ-CP~~ | | | ❌ **hết hiệu lực** |
| ~~NĐ 24/2024/NĐ-CP~~ | | | ❌ **đã bị NĐ 214/2025 thay** |

⚠️ **Có dự thảo viết lại toàn diện Luật Đấu thầu, đề ngày 28/7/2026** — chưa có số hiệu, chưa qua
Quốc hội, **chưa áp dụng**. Không phải chỉ sửa vài điều: dự thảo đánh số lại toàn bộ luật, từ 96
điều xuống còn 73 điều (vd Điều 60 + Điều 61 hiện hành gộp thành một điều mới). Nếu văn bản này
được thông qua, toàn bộ số điều đang trích trong `references/dau-thau.md` sẽ sai — phải tra lại
bảng ánh xạ điều khoản cũ → mới, không suy đoán. Vì đang có một thay đổi lớn treo lơ lửng, TTL bộ
nhớ cho mảng đấu thầu đặt ngắn nhất — **45 ngày**. Nếu ghi chú quá 45 ngày, tra lại.

## Cách tra một quy định

1. `bo_nho.py tra "<chủ đề>"` — nếu có ghi chú còn hạn thì dùng luôn, xong. Câu hỏi về MỘT KỲ CỤ
   THỂ (giao dịch năm ngoái, tờ khai quý trước) thì thêm `--ngay <ngày giao dịch>`: nó chọn bản có
   hiệu lực tại ngày đó (kể cả bản lưu trữ) và cảnh báo văn bản hồi tố.
2. Nếu không có hoặc quá hạn: tra web. Câu truy vấn nên gồm **số hiệu văn bản + năm + từ khoá
   nội dung**, ví dụ `"Nghị định 214/2025 hiệu chỉnh sai lệch mua sắm hàng hóa"`.
   Thêm một truy vấn riêng dạng `"<số hiệu> còn hiệu lực không thay thế bởi"` để bắt bẫy 2.
3. Đối chiếu ít nhất một nguồn `.gov.vn` hoặc bản hợp nhất trên thuvienphapluat.
4. `bo_nho.py ghi` với đầy đủ `--hieu-luc-tu`, `--ngay-ban-hanh` (khác ngày hiệu lực khi hồi tố),
   `--dieu-khoan`, `--nguon` (URL https), `--do-tin-cay`, và `--sua-doi` / `--thay-the` /
   `--thay-the-boi` nếu có. Ghi chú mới luôn mang `can_nguoi_duyet: true` — tra web xong không có
   nghĩa diễn giải đã được người có chuyên môn duyệt.
5. Trả lời người dùng, **kèm số hiệu văn bản và ngày hiệu lực**. Không nói trống không
   "thuế suất là 10%" mà nói "10% theo Luật 48/2024/QH15, hiệu lực từ 01/7/2025".

> ⚠️ Nhắc lại nguyên tắc 6: nếu đang làm việc chấm thầu, **không** đưa tên nhà thầu, giá dự thầu,
> hay tên gói thầu vào câu truy vấn. Hỏi trừu tượng về quy định, không hỏi về hồ sơ cụ thể.
