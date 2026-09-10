# Chấm thầu — gói mua sắm hàng hóa

> **Kiểm hiệu lực văn bản trước khi tin file này.** Chạy `bo_nho.py tra "dau thau"`. Nội dung dưới
> đây lập ngày 2026-09-10 theo NĐ 214/2025/NĐ-CP, và **đã có dự thảo sửa nghị định này** — nên TTL
> bộ nhớ cho mảng đấu thầu chỉ 45 ngày.

## Khung pháp lý hiện hành

| Văn bản | Vai trò |
|---|---|
| Luật 22/2023/QH15, sửa bởi Luật 57/2024/QH15 và Luật 90/2025/QH15 (hiệu lực 01/7/2025) | Luật Đấu thầu |
| **NĐ 214/2025/NĐ-CP** (hiệu lực 04/8/2025) | Chi tiết lựa chọn nhà thầu — **văn bản đang áp dụng** |
| TT 79/2025/TT-BTC | Mẫu HSMT, đăng tải thông tin |
| TT 80/2025/TT-BTC | Mẫu HSYC, **báo cáo đánh giá**, báo cáo thẩm định |

❌ **Không dùng NĐ 63/2014 và NĐ 24/2024** — đã hết hiệu lực. Đây là lỗi rất dễ mắc vì hai văn bản
này vẫn xếp đầu kết quả tìm kiếm và vẫn được nhiều blog trích dẫn. Nếu bạn thấy mình sắp viết
"theo Nghị định 63/2014" hay "theo Nghị định 24/2024", dừng lại và tra lại.

## Nguyên tắc chi phối mọi việc ở đây

**Skill tính toán, tổ chuyên gia quyết định.**

Không bao giờ tự kết luận nhà thầu "đạt", "không đạt", hay "trúng thầu". Việc của skill là lập
bảng tính sơ bộ và chỉ ra chỗ cần xem xét; việc của tổ chuyên gia là đối chiếu và quyết định.

Với mỗi nhận định, phải dẫn được:
- **điều khoản trong HSMT** làm căn cứ yêu cầu, và
- **số trang trong HSDT** nơi tìm thấy (hoặc không tìm thấy) thông tin.

Chỗ nào không có căn cứ thì ghi `chưa xác định — cần kiểm tra trang X`, không đoán.

Lý do không phải là sự thận trọng hình thức: chấm thầu là hành vi pháp lý có hậu quả. Một dòng
"không đạt" sai dẫn tới kiến nghị, hủy thầu, và quy trách nhiệm cá nhân cho người ký biên bản.
Người ký chịu trách nhiệm đó, không phải bạn — nên hãy đưa họ dữ liệu tốt kèm đường dẫn tới bằng
chứng, đừng đưa họ kết luận để ký mà không kiểm được.

**Và: không đưa nội dung HSDT ra ngoài.** Không tra web với tên nhà thầu, giá dự thầu, hay tên gói
thầu. Muốn tra quy định thì hỏi trừu tượng.

## Quy trình 1 giai đoạn 1 túi hồ sơ — mua sắm hàng hóa

Thứ tự đánh giá là bắt buộc; **không nhảy bước**, vì hồ sơ bị loại ở bước trước thì không xét bước sau.

1. **Tính hợp lệ** — đơn dự thầu hợp lệ, có chữ ký, hiệu lực HSDT đủ, bảo đảm dự thầu hợp lệ
   (đúng số tiền, đúng hình thức, **còn hiệu lực đủ dài**), không thuộc trường hợp bị cấm, bảo đảm
   cạnh tranh (Điều 4 NĐ 214/2025 — nhà thầu phải độc lập với đơn vị lập/thẩm định HSMT và đơn vị
   đánh giá HSDT).
2. **Năng lực và kinh nghiệm** — doanh thu bình quân, hợp đồng tương tự, nguồn lực tài chính,
   thường chấm đạt/không đạt.
3. **Kỹ thuật** — theo HSMT, **chấm điểm** hoặc **đạt/không đạt**. Nhà thầu đáp ứng yêu cầu về đấu
   thầu bền vững được tiếp tục xem xét. Xem mục riêng bên dưới.
4. **Tài chính** — sửa lỗi, hiệu chỉnh sai lệch, tính giá đánh giá.
5. **Xếp hạng**, rồi đánh giá nhân sự chủ chốt / thiết bị của nhà thầu xếp hạng nhất.

## Đánh giá kỹ thuật — và vì sao nó phải chạy TRƯỚC bước tài chính

Bước 3 không chỉ để loại hồ sơ. Kết quả của nó là **đầu vào bắt buộc** của bước 4: đơn giá dùng để
hiệu chỉnh phần chào thiếu phải lấy "trong số các HSDT khác **vượt qua bước đánh giá về kỹ thuật**"
(điểm c khoản 2 Điều 31). Lấy trên tất cả nhà thầu — kể cả bên đã trượt kỹ thuật — là sai luật và
ra số khác. Trên bộ dữ liệu thử, loại một nhà thầu khỏi nhóm này làm giá trị hiệu chỉnh đổi từ
73.542.000 xuống 70.686.000 và mất một vị trí trong bảng xếp hạng.

⇒ Quy trình hai pha, không gộp làm một:

```bash
# Pha 1 — lập phiếu đối chiếu kỹ thuật
cham_ky_thuat.py <thư mục HSDT> --yeu-cau yeu_cau_ky_thuat.csv --ra phieu_cham.xlsx
#   → tổ chuyên gia mở file, điền cột ket_luan (Đạt / Không đạt / Cần làm rõ)

# Pha 2 — tính tài chính với nhóm vượt kỹ thuật đã xác định
so_sanh_thau.py hsdt.json --danh-muc danh_muc.csv \
    --ket-qua-ky-thuat phieu_cham.xlsx --ra so_sanh.xlsx
```

Chạy `so_sanh_thau.py` mà **không** có `--ket-qua-ky-thuat` vẫn được, nhưng nó sẽ cảnh báo rõ rằng
giá trị hiệu chỉnh có thể sai. Đừng bỏ qua cảnh báo đó.

### Script chấm kỹ thuật KHÔNG kết luận đạt/không đạt

Đây là chỗ nguyên tắc "skill tính toán, tổ chuyên gia quyết định" phải giữ chặt nhất. Đánh giá kỹ
thuật là nơi tập trung nhiều nhận định chuyên môn nhất: "tương đương", "đáp ứng về cơ bản",
"xuất xứ chấp nhận được" đều là phán đoán của người chịu trách nhiệm pháp lý, không phải phép so
chuỗi. Script chỉ xếp yêu cầu và chào cạnh nhau kèm số trang, rồi đối chiếu những gì **khách quan**
đối chiếu được:

| `doi_chieu_may` | Nghĩa | Máy có được kết luận không? |
|---|---|---|
| `khop` | Số liệu đáp ứng ngưỡng | Không — vẫn cần người xác nhận |
| `thap_hon` | Chào NHỎ HƠN ngưỡng số học, và HSMT ghi rõ "trở lên"/"tối thiểu" | Nêu sự kiện, không tuyên bố loại |
| `thieu_du_lieu` | Không tìm thấy tiêu chí trong HSDT | Không |
| `can_nguoi_xem` | Khác loại, không so được bằng máy | Không |

Ví dụ phân biệt: "RAM 8 GB" so với "16 GB trở lên" là **`thap_hon`** — số học, khách quan.
"Xuất xứ Trung Quốc" so với "G7 hoặc EU" là **`can_nguoi_xem`** — cần người đọc HSMT để biết yêu cầu
đó có tuyệt đối không, có điều khoản tương đương không. Đừng để script tự loại nhà thầu ở loại
tiêu chí thứ hai.

Nếu HSMT dùng **phương pháp chấm điểm** thay vì đạt/không đạt, cột `ket_luan` vẫn dùng được để ghi
điểm; nhưng phải kiểm mức điểm tối thiểu từng nội dung theo HSMT — script không tự tính tổng điểm.

**Ô trống trong cột `ket_luan` không được suy thành "Đạt".** Nhà thầu còn ô trống bị xếp vào
`chua_co_ket_luan` và **không** được tính vào nhóm lấy đơn giá hiệu chỉnh — vì suy diễn ở đây sẽ âm
thầm làm đổi con số và đổi thứ hạng.

## Sửa lỗi ≠ hiệu chỉnh sai lệch

Đây là chỗ hay lẫn nhất, và lẫn thì ra số sai. Hai thao tác khác nhau:

| | **Sửa lỗi** | **Hiệu chỉnh sai lệch** |
|---|---|---|
| Chữa cái gì | Lỗi số học và lỗi khác *trong* HSDT | Phần chào **thiếu** hoặc **thừa** so với HSMT |
| Ví dụ | `10 cái × 100.000 = 1.500.000` (sai phép nhân) | HSMT có 8 mặt hàng, HSDT chỉ chào 7 |
| Cách xử lý | Sửa lại cho đúng theo nguyên tắc quy định | Chào thiếu thì **cộng thêm**, chào thừa thì **trừ đi**, theo đơn giá tương ứng trong HSDT |

**Hạng mục bỏ sót**: hạng mục nêu trong HSMT nhưng **không được liệt kê** trong bảng giá dự thầu
được coi là **phần chào thiếu** và phải hiệu chỉnh sai lệch để so sánh, xếp hạng. Nó không tự động
làm nhà thầu bị loại.

**Đơn giá dùng để hiệu chỉnh phần chào thiếu** — điểm c khoản 2 Điều 31 NĐ 214/2025, **thứ tự ưu tiên**:

1. đơn giá chào **CAO NHẤT** đối với hạng mục đó trong số các **HSDT khác đã vượt qua bước
   đánh giá về kỹ thuật**;
2. đơn giá trong **dự toán** gói thầu (nếu các HSDT vượt kỹ thuật đều không có đơn giá);
3. đơn giá hình thành **giá gói thầu** (nếu không có dự toán).

> ⚠️ **CAO NHẤT, không phải thấp nhất.** Đây là chỗ sai phổ biến nhất, vì rất nhiều tài liệu, blog
> và cả mẫu biên bản đang lưu hành vẫn chép theo NĐ 63/2014 đã hết hiệu lực. Dùng nhầm chiều là
> **đảo thứ hạng nhà thầu** — hậu quả trực tiếp lên kết quả gói thầu. Logic của quy định: hiệu chỉnh
> theo mức cao nhất để nhà thầu chào thiếu không được lợi thế giá so với nhà thầu chào đủ.

**Và: giá trị hiệu chỉnh chỉ dùng để so sánh, xếp hạng.** Nếu sau hiệu chỉnh nhà thầu vẫn xếp thứ
nhất thì **giá đề nghị trúng thầu KHÔNG bao gồm giá trị hiệu chỉnh sai lệch**. Nói cách khác: cộng
thêm để xếp hạng, nhưng không cộng vào giá ký hợp đồng. Nêu rõ điều này khi trình tổ chuyên gia,
vì hai con số khác nhau và rất dễ bị dùng nhầm chỗ.

## Ba cái bẫy số học

**Bẫy 1 — thư giảm giá.** Sửa lỗi và hiệu chỉnh sai lệch thực hiện trên **giá dự thầu CHƯA trừ
giá trị giảm giá**. Trừ giảm giá là bước sau cùng. Trừ sớm thì tỷ lệ sai lệch tính ra sai.
Tỷ lệ % sai lệch thiếu cũng xác định so với **giá dự thầu ghi trong đơn dự thầu**, không phải giá
sau giảm.

Thư giảm giá **không được công khai trong biên bản mở thầu thì không được xem xét**.

**Bẫy 2 — thuế, phí.** Chào thiếu thuế, phí, lệ phí phải nộp theo yêu cầu HSMT **không** bị tính
vào sai lệch thiếu.

**Bẫy 3 — ngưỡng 10%.** Sai lệch thiếu **không quá 10% giá dự thầu** là một **điều kiện xét duyệt
trúng thầu** (điểm d khoản 1 Điều 61 Luật Đấu thầu 22/2023), **không phải tiêu chí đánh giá** —
nghĩa là nó được xét ở bước cuối, không phải bước loại hồ sơ. Vượt ngưỡng thì cảnh báo rõ, nhưng
vẫn **không tự tuyên bố loại**, chỉ nêu sự kiện kèm căn cứ.

Lưu ý: ngưỡng này nay nằm ở **cấp luật**, không còn trong nghị định như trước.

## Giá đánh giá

```
G = (giá dự thầu ± giá trị sửa lỗi ± giá trị hiệu chỉnh sai lệch)
    − giá trị giảm giá (nếu có)
    + ΔG        các yếu tố quy về một mặt bằng cho cả vòng đời
    + ΔƯĐ       giá trị phải cộng thêm với đối tượng KHÔNG được hưởng ưu đãi
```

`ΔG` gồm các yếu tố như tiến độ, chi phí vòng đời, chi phí lãi vay, yếu tố đấu thầu bền vững,
kết quả thực hiện hợp đồng trước đây — **chỉ tính những gì HSMT quy định**, và phải nêu rõ đang
dùng công thức nào của HSMT. Nếu HSMT không quy định thì `ΔG = 0`, đừng tự nghĩ ra.

Phương pháp xếp hạng tuỳ HSMT: **giá thấp nhất** (xếp theo giá sau sửa lỗi, hiệu chỉnh, trừ giảm
giá) hoặc **giá đánh giá** (xếp theo `G`). Đọc HSMT để biết đang dùng cái nào — đừng mặc định.

Nếu chỉ có **một** nhà thầu đạt yêu cầu kỹ thuật thì không phải xác định danh sách xếp hạng.

## Sản phẩm giao ra

⚠️ **Phân công:** file Excel do `so_sanh_thau.py` xuất ra là **bản trung gian** — nó ghi giá trị
chết, không có công thức. Đừng giao thẳng bản đó cho tổ chuyên gia. Dùng nó làm dữ liệu đã kiểm,
rồi dựng workbook cuối bằng skill `xlsx` với **công thức thật** (`=B5*C5`, `=SUM(...)`), và chạy
`recalc.py` trước khi giao.

Lý do không phải hình thức: người chấm thầu sẽ bị hỏi "số này ở đâu ra?" khi trình và khi bị
thanh tra. Một ô chứa `=D8-E8+F8` trả lời được câu đó; một ô chứa `1.149.342.000` thì không.
Cùng lý do với `references/bao-cao.md`.

Các sheet `so_sanh_thau.py` sinh ra:

| Sheet | Nội dung |
|---|---|
| `Tong hop` | Mỗi nhà thầu một dòng: giá dự thầu, sửa lỗi, hiệu chỉnh, giảm giá, ΔG, ΔƯĐ, giá đánh giá, xếp hạng sơ bộ |
| `Doi chieu danh muc` | Ma trận mặt hàng × nhà thầu, đánh dấu chào thiếu / chào thừa |
| `Sua loi` | Từng dòng sai số học, số cũ, số đúng, chênh lệch |
| `Canh bao` | Mọi thứ đáng ngờ: sai lệch vượt 10%, bảo lãnh hết hiệu lực, thiếu tài liệu |
| `Can cu` | **Nguồn từng con số**: file nào, trang mấy |

Ô A1 của sheet `Tong hop` ghi rõ: *"Kết quả tính toán sơ bộ. Tổ chuyên gia phải rà soát, đối chiếu
với HSMT và HSDT gốc trước khi kết luận. Tài liệu này không phải là kết quả đánh giá."*

Báo cáo đánh giá chính thức theo **mẫu tại TT 80/2025/TT-BTC** — nếu người dùng cần lập, tra mẫu
hiện hành trước, đừng dựng theo trí nhớ.

## Lệnh

```bash
# 1. Bóc tách HSDT (mỗi nhà thầu một thư mục con)
doc_hsdt.py <thư mục HSDT> --ra hsdt.json

# 2. Phiếu đối chiếu kỹ thuật → tổ chuyên gia điền cột ket_luan
cham_ky_thuat.py <thư mục HSDT> --yeu-cau yeu_cau_ky_thuat.csv --ra phieu_cham.xlsx
cham_ky_thuat.py <thư mục HSDT> --hsmt hsmt.pdf --ra phieu_cham.xlsx

# 3. Tài chính, với nhóm vượt kỹ thuật đã xác định
so_sanh_thau.py hsdt.json --danh-muc danh_muc.csv \
    --ket-qua-ky-thuat phieu_cham.xlsx --ra so_sanh.xlsx
so_sanh_thau.py hsdt.json --danh-muc danh_muc.csv --du-toan 11900000 --ra so_sanh.xlsx
```

`doc_hsdt.py` gắn `nguon_trang` cho từng trường trích được. Trường không tìm thấy trả `null` kèm
lý do — **không** điền 0 hay đoán.
