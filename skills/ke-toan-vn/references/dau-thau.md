# Chấm thầu — gói mua sắm hàng hóa

> **Kiểm hiệu lực văn bản trước khi tin file này.** Chạy `bo_nho.py tra "dau thau"`. Nội dung dưới
> đây cập nhật ngày 2026-09-13 theo NĐ 214/2025/NĐ-CP và Luật Đấu thầu (bản hợp nhất
> 74/VBHN-VPQH), và **đã có dự thảo viết lại toàn diện Luật Đấu thầu** (xem cảnh báo bên dưới) —
> nên TTL bộ nhớ cho mảng đấu thầu chỉ 45 ngày.

## Khung pháp lý hiện hành

| Văn bản | Vai trò |
|---|---|
| Luật Đấu thầu 22/2023/QH15, sửa bởi Luật 57/2024/QH15, Luật 90/2025/QH15 (hiệu lực 01/7/2025), Luật Phục hồi, phá sản 142/2025/QH15 (01/3/2026), Luật An ninh mạng 116/2025/QH15 và Luật Công nghệ cao 133/2025/QH15 (cả hai 01/7/2026) | Luật Đấu thầu — **cả 5 lần sửa đều đã có hiệu lực** |
| **Văn bản hợp nhất số 74/VBHN-VPQH (2026)** | Bản hợp nhất đủ 5 lần sửa trên vào một văn bản — **tra số điều ở đây**, đừng tự cộng dồn các luật sửa đổi |
| **NĐ 214/2025/NĐ-CP** (hiệu lực 04/8/2025) | Chi tiết lựa chọn nhà thầu — **văn bản đang áp dụng** |
| TT 79/2025/TT-BTC | Mẫu HSMT, đăng tải thông tin |
| TT 80/2025/TT-BTC | Mẫu HSYC, **báo cáo đánh giá**, báo cáo thẩm định |

❌ **Không dùng NĐ 63/2014 và NĐ 24/2024** — đã hết hiệu lực. Đây là lỗi rất dễ mắc vì hai văn bản
này vẫn xếp đầu kết quả tìm kiếm và vẫn được nhiều blog trích dẫn. Nếu bạn thấy mình sắp viết
"theo Nghị định 63/2014" hay "theo Nghị định 24/2024", dừng lại và tra lại.

⚠️ **Có dự thảo viết lại toàn diện Luật Đấu thầu, đề ngày 28/7/2026** (chưa có số hiệu, chưa qua
Quốc hội — **không áp dụng**). Dự thảo đánh số lại toàn bộ luật, từ 96 điều xuống còn **73 điều**
(ví dụ Điều 60 và Điều 61 hiện hành gộp làm một thành Điều 39 dự thảo). Nếu dự thảo này được thông
qua, **mọi số điều trích trong file này sẽ đổi** — trước khi trích dẫn số điều, kiểm xem luật mới
đã có hiệu lực chưa; nếu có, tra lại toàn bộ bảng ánh xạ điều khoản, đừng suy đoán điều tương ứng.

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

**Khoản 4 Điều 31 — chuẩn THỨ HAI, ngược chiều, cho riêng nhà thầu thắng.** Đây là chỗ dễ hiểu sai
tiếp theo, vì rất dễ tưởng chỉ có một đơn giá hiệu chỉnh dùng xuyên suốt. Thực ra có **hai bước**:

1. **Xếp hạng** (điểm c khoản 2, ở trên): hiệu chỉnh bằng đơn giá **CAO NHẤT** cho MỌI nhà thầu
   chào thiếu, để so sánh công bằng.
2. **Áp đơn giá cho nhà thầu xếp hạng nhất** (khoản 4): nếu sau bước 1 nhà thầu chào thiếu **vẫn
   xếp hạng nhất**, và HSDT của họ không có đơn giá cho phần chào thiếu đó, thì giá trị đưa vào
   **giá đề nghị trúng thầu** (giá sẽ ký hợp đồng) cho riêng phần đó phải tính lại bằng đơn giá
   **THẤP NHẤT** trong số các HSDT vượt kỹ thuật — cùng thứ tự ưu tiên dự toán rồi giá gói thầu,
   chỉ đảo chiều đơn giá.

⇒ Cùng một hạng mục chào thiếu có **hai giá trị khác nhau**: cao nhất khi xếp hạng, thấp nhất khi
tính tiền hợp đồng thật của người thắng. **"Giá đề nghị trúng thầu" theo định nghĩa của Luật vẫn
BAO GỒM giá trị hiệu chỉnh sai lệch** — không phải bỏ đi, chỉ là tính lại bằng đơn giá khác. Đừng
nhầm với `ΔG`/`ΔƯĐ` (mục "Giá đánh giá" bên dưới) — đó mới là phần chỉ phục vụ xếp hạng và không
cộng vào giá hợp đồng. Nêu rõ cả hai con số (giá trị hiệu chỉnh dùng để xếp hạng, và giá đề nghị
trúng thầu dự kiến theo khoản 4) khi trình tổ chuyên gia, vì rất dễ dùng nhầm chỗ.

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

**`ΔG` và `ΔƯĐ` — không phải giá trị hiệu chỉnh sai lệch — mới là phần KHÔNG cộng vào giá hợp
đồng.** Chúng chỉ là quy đổi để so sánh, xếp hạng công bằng giữa các nhà thầu (vd quy đổi chi phí
vòng đời, cộng tiền cho hàng hóa không được ưu đãi) và biến mất khỏi giá ký hợp đồng sau khi đã
chọn được người thắng. Giá trị hiệu chỉnh sai lệch (mục "Sửa lỗi ≠ hiệu chỉnh sai lệch" ở trên)
thì khác — nó **có mặt** trong giá đề nghị trúng thầu, chỉ đổi đơn giá theo khoản 4 Điều 31.

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
| `Tong hop` | Mỗi nhà thầu một dòng: giá dự thầu, sửa lỗi, hiệu chỉnh (đơn giá cao nhất, để xếp hạng), giảm giá, giá đánh giá, xếp hạng sơ bộ, và **giá đề nghị trúng thầu dự kiến** (đơn giá thấp nhất — khoản 4 Điều 31, chỉ tính cho nhà thầu xếp hạng nhất). Cột Ghi chú nêu rõ ΔG/ΔƯĐ chưa tính — chỉ tính khi HSMT có công thức |
| `Doi chieu danh muc` | Ma trận mặt hàng × nhà thầu, đánh dấu chào thiếu / chào thừa |
| `Sua loi` | Từng dòng sai số học, số cũ, số đúng, chênh lệch |
| `Canh bao` | Mọi thứ đáng ngờ: sai lệch vượt 10%, bảo lãnh hết hiệu lực, thiếu tài liệu |
| `Can cu` | **Nguồn từng con số**: file nào, trang mấy |

Ô A1 của sheet `Tong hop` ghi rõ: *"Kết quả tính toán sơ bộ. Tổ chuyên gia phải rà soát, đối chiếu
với HSMT và HSDT gốc trước khi kết luận. Tài liệu này không phải là kết quả đánh giá."*

### Tra mẫu biểu — đừng dựng theo trí nhớ

Báo cáo, hồ sơ chính thức phải theo đúng mẫu ban hành kèm thông tư — nội dung, thứ tự mục trong
mẫu có thể đổi giữa các lần sửa thông tư, nên **tra mẫu hiện hành trước khi dựng file**, đừng nhớ
lại cấu trúc mẫu cũ. Bảng dưới đây chỉ để biết **nên tìm mẫu số mấy trong thông tư nào** — không
thay cho việc mở đúng mẫu ra xem.

**TT 80/2025/TT-BTC** — báo cáo đánh giá, thẩm định, kiểm tra:

| Việc cần lập | Mẫu số |
|---|---|
| Hồ sơ yêu cầu (chỉ định thầu, chào hàng cạnh tranh...) — xây lắp / hàng hóa / phi tư vấn / tư vấn | 01A / 01B / 01C / 01D |
| Báo cáo đánh giá HSDT — 1 giai đoạn 1 túi hồ sơ (hàng hóa, xây lắp, phi tư vấn, hỗn hợp, thiết bị y tế, chào giá trực tuyến) | 02A |
| Báo cáo đánh giá HSDT — 1 giai đoạn 2 túi hồ sơ | 02B |
| Báo cáo đánh giá HSDT — gói thầu tư vấn | 02C |
| Báo cáo thẩm định HSMT / danh sách đáp ứng kỹ thuật / kết quả lựa chọn nhà thầu | 03A / 03B / 03C |
| Kế hoạch, báo cáo, kết luận kiểm tra hoạt động đấu thầu | 04.1 – 04.5 |
| Báo cáo tình hình thực hiện hoạt động đấu thầu | 05 |

**TT 79/2025/TT-BTC** — E-HSMT theo loại gói thầu (mẫu `A` = 1 túi/thông thường, `B` = 2 túi,
`C` = hồ sơ mời sơ tuyển, trừ khi ghi khác):

| Loại gói thầu | Mẫu số |
|---|---|
| Xây lắp | 3A / 3B / 3C |
| Hàng hóa | 4A / 4B / 4C |
| Phi tư vấn | 5A / 5B / 5C |
| Tư vấn (tổ chức / mời quan tâm / cá nhân) | 6A / 6B / 6C |
| Hỗn hợp EP (tư vấn + hàng hóa) | 7A / 7B / 7C |
| Hỗn hợp EC (tư vấn + xây lắp) | 8A / 8B / 8C |
| Hỗn hợp PC (hàng hóa + xây lắp) | 9A / 9B / 9C |
| Hỗn hợp EPC (tư vấn + hàng hóa + xây lắp) | 10A / 10B / 10C |
| Máy đặt máy mượn | 11A / 11B |
| Chào giá trực tuyến (thông thường / rút gọn, theo loại gói) | 12A – 12G |
| Mua sắm trực tuyến | 13 |
| Kế hoạch lựa chọn nhà thầu | 01A – 02C |

Cả hai thông tư đều còn nhiều mẫu khác (phụ lục, đề cương báo cáo...) ngoài bảng trên — nếu không
thấy việc cần làm trong hai bảng này, hỏi lại người dùng tên mẫu chính xác thay vì đoán.

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
