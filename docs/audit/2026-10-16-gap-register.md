# Sổ đăng ký khoảng hở (gap register) — 2026-10-16

- **Bản được kiểm:** `main` @ `e0e6921` (release 0.4.0), worktree `feat/audit-controls-p0-p1`.
- **Baseline:** `evals/kiem_thu.py` **65/65 đạt** (khớp handoff; đếm theo dòng phép kiểm, không tính dòng tổng kết). Log: [`evidence/00-baseline-kiem-thu-e0e6921.txt`](evidence/00-baseline-kiem-thu-e0e6921.txt).
- **Bằng chứng tái hiện (đỏ trước khi sửa):** [`evidence/01-red-p0-truoc-khi-sua.txt`](evidence/01-red-p0-truoc-khi-sua.txt). Kết quả: 38 phép kiểm hỏng, 4 đạt.
  - Phép "mất cột NHOM → dừng" đạt vì hành vi đó có sẵn từ trước, nên không phải gap.
  - Phép `--yeu-cau-day-du` đạt nhầm: tham số chưa tồn tại nên argparse thoát với mã 2.
- **Cách chạy lại:**

  ```bash
  python evals/tao_fixtures.py
  KE_TOAN_VN_HOME=$(mktemp -d) python evals/kiem_thu.py
  python evals/kiem_soat.py
  ```

Mỗi giả thuyết trong handoff được kiểm lại trên mã nguồn thật, không mặc nhiên coi là đúng. Số dòng dưới đây là của bản `e0e6921`.

| Gap | Ưu tiên | Phán định | Vị trí mã (e0e6921) | Tái hiện → phép kiểm | Mức độ / tác động | Trạng thái |
|---|---|---|---|---|---|---|
| G01 | P0 | **Xác nhận** | `SKILL.md:10` (“hệ thống tài khoản TT 200”); `references/phap-ly.md:55` (chỉ có TT 200/TT 133, không có TT 99/2025, TT 58/2026, TT 24/2024); `references/bao-cao.md:72`; `README.md:42`. Không có bộ phân giải nào. | ACC-001…004, “năm tài chính 2024 vẫn TT 200”, “loại đơn vị khác → cần xác nhận” | Cao: DN có năm tài chính 2026 bị dẫn sang TT 200 dù TT 99 đã thay (Điều 31 TT 99/2025). Bệnh viện công/tư không được phân biệt. DN siêu nhỏ năm dương lịch 2026 rơi vào khoảng trống giữa TT 132 và TT 58 mà không ai được báo. | **Đã sửa, có test** |
| G02 | P0 | **Xác nhận** | `bo_nho.py:152-162` chỉ dựa `het_han` (TTL) và `thay_the_boi`; không có tra theo ngày, không có `ngay_ban_hanh`. `tra` bỏ hẳn bản lưu trữ (`:180`). | ACC-005, “năm thuế cũ lấy bản cũ”, “còn hạn nhưng chưa hiệu lực”, “không có ngày hiệu lực” | Cao: một ghi chú 2026 “còn hạn” được trả về cho câu hỏi về giao dịch 2025. Văn bản hồi tố (NĐ 141/2026 ban hành 29/4 nhưng hiệu lực từ 01/01/2026) không được cảnh báo. | **Đã sửa, có test** |
| G03 | P0 | **Xác nhận** | `doc_hoa_don.py:76` chỉ có `ET.parse`, không kiểm chữ ký hay trạng thái. `_tim` ở `:46-56` lấy kết quả khớp đầu tiên ở mọi độ sâu, nên với `<TDiep>` chứa 2 `<HDon>` chỉ ra **1 dòng**, mang số của hóa đơn đầu. | INV-001, INV-002, INV-005, “thẻ lặp khác giá trị”, “chứng thư không khớp” | Cao: hóa đơn thứ hai trong thông điệp biến mất khỏi bảng kê. XML “đọc được” dễ bị hiểu là “thật”. | **Đã sửa, có test** |
| G04 | P0 | **Xác nhận** | `doc_hoa_don.py:273-275` chỉ cộng các giá trị khác `None`. Cảnh báo chỉ ra stderr, mã thoát luôn 0 (`:327`). Hóa đơn trùng vẫn bị cộng hai lần vào tổng. | INV-003, INV-004, “điều chỉnh âm / 0 đồng” | Cao: tổng thiếu một hóa đơn trông như tổng cuối, và thuế đầu vào bị đếm đôi khi hóa đơn trùng. | **Đã sửa, có test** |
| G05 | P0 | **Xác nhận, nặng hơn giả thuyết** | `quy_trinh.py:98-114` so bố cục **sau khi** `ghi_tat_ca`/`chay` đã ghi file. Với `tach` và `doi-chieu`, `kiem_gia_tri_moi` chạy sau `m.chay` (`:101-103`) — tức là file đã ghi rồi mới dừng hỏi `can_hoi`, trong khi thông báo nói “chưa file nào được ghi”. `_xuat.py:36` ghi thẳng, không nguyên tử. Thêm một lỗi: `_loc.py:169` sập (KeyError, traceback) khi `cot_tien = "$F"`. | WF-001, WF-002, WF-003, “--xem-truoc”, “lô không ghi dở dang” | Cao: cột tiền theo vị trí đổi nghĩa vẫn cho ra file kết quả. Thông báo `can_hoi` nói sai sự thật. Lô nhiều file có thể ghi dở dang. | **Đã sửa, có test** |
| G06 | P1 | **Xác nhận một phần** | `_quy_trinh.py:312-317` băm đầu vào nhưng cắt còn 16 ký tự hex. `ghi_lich_su` (`:337`) ghi JSONL không có mã băm quy tắc, không có mã băm kết quả, không có commit/phiên bản, không có run_id, giờ không kèm múi giờ, không có chuỗi chống sửa. | AUD (hồ sơ, run_id, phát lại), AUD-001, AUD-002, gói kiểm toán, `kiem-goi` | Trung bình–cao: không chứng minh được kết quả nào đến từ nguồn nào, theo quy tắc nào. | **Đã sửa, có test** |
| G07 | P1 | **Xác nhận** | Không có khái niệm người duyệt. `--chap-nhan-gia-tri-moi` (`quy_trinh.py:151`) là một cờ boolean không danh tính. | “UNVERIFIED_HUMAN_REVIEW”, “biến môi trường không phải xác thực”, tách nhiệm, needs_review cần ngoại lệ, TEN-001 | Trung bình–cao: không biết ai đã chấp nhận ngoại lệ, chấp nhận nội dung nào. | **Đã sửa ở mức trung thực.** Không có xác thực danh tính nên trạng thái tối đa là `da_xem_chua_xac_thuc`. |
| G08 | P1 | **Xác nhận** | `bo_nho.py:268` đặt tên bản lưu `.cu-YYYY-MM-DD.md`: cập nhật lần hai trong ngày ghi đè bản lưu lần một. `SKILL.md:191` hướng dẫn luôn ghi đè kết quả, không phân biệt đã duyệt hay chưa. | AUD-003, G08 “không ghi đè bản đã duyệt”, “-SUA1” | Trung bình: mất phiên bản ghi chú, và kết quả đã duyệt có thể bị ghi đè âm thầm. | **Đã sửa, có test** |
| G09 | P1 | **Xác nhận** | `so_sanh_thau.py:276-277`: không có kết quả kỹ thuật thì coi **mọi** nhà thầu là vượt và vẫn xếp hạng. Không có chế độ chính thức. Thêm một lỗi: `:179` sập khi phiếu kỹ thuật còn ô kết luận trống (NaN). | BID-001 (3 phép), “chấm thầu không ghi vào bộ nhớ” | Trung bình: bảng xếp hạng sơ bộ có thể bị dùng như kết luận. | **Đã sửa, có test.** Chưa làm: kiểm trích dẫn HSMT từng tiêu chí (xem mục hoãn). |
| G10 | P1 | **Xác nhận (cần đánh giá áp dụng)** | `_chung.py:11` có một thư mục bộ nhớ duy nhất cho mọi đơn vị: quy trình, danh mục, quy ước, lịch sử dùng chung. | TEN-001 (4 phép), “không script nào gọi mạng” | Trung bình: chạy cho hai đơn vị trên cùng máy thì mã `KHS` của đơn vị này áp nhầm cho đơn vị kia. | **Đã sửa, có test.** Hoãn: chính sách lưu trữ theo loại dữ liệu và legal hold. |
| G11 | P1 | **Xác nhận** | Mọi phép kiểm trong `evals/kiem_thu.py` so với con số đã biết. Công thức đối chiếu trong `_loc.ghi` tính từ chính danh sách vừa phân loại (đúng theo định nghĩa). Không có phép đọc lại file đã ghi, không phát hiện dòng tổng lẫn trong dữ liệu, không chặn STT làm khoá. | G11 (5 phép) | Trung bình: lỗi cộng trùng kiểu bảng đã duyệt trước đây vẫn lọt qua so khớp file mẫu. | **Đã sửa, có test** |
| G12 | P2 | **Xác nhận một phần** | `ET.parse` không giới hạn kích thước. CSV/XLSX xuất ra giữ nguyên chuỗi `=...` (thành công thức). Thư viện không ghim phiên bản, CI chỉ chạy Ubuntu. Expat của Python 3.13 đã chặn “billion laughs”, nhưng công cụ không tự chặn. | SEC-001 (4 phép) | Thấp–trung bình | **Đã gia cố phần có tác động.** Phần còn lại hoãn (xem dưới). |

## Phát hiện thêm ngoài handoff

1. **`can_hoi` nói sai sự thật với `tach`/`doi-chieu` (G05).** File đã ghi rồi mới dừng hỏi. Test WF-003 tái hiện được.
2. **`loc` sập khi khai cột tiền theo vị trí `$F`.** Lỗi ở `_loc.py:169`. Tài liệu `quy-trinh.md` có hứa hỗ trợ cú pháp `$Z` nhưng `loc` không chạy được.
3. **`so_sanh_thau.py` sập khi phiếu kỹ thuật còn ô kết luận trống.** Đây lại chính là tình huống mà docstring hứa sẽ coi là “chưa chấm xong”.
4. **DN siêu nhỏ có năm tài chính bắt đầu trước 01/7/2026 rồi vắt qua mốc đó** (ví dụ năm dương lịch 2026) rơi vào khoảng trống văn bản:
   - TT 132/2018 hết hiệu lực từ 01/7/2026 (khoản 2 Điều 12 TT 58/2026);
   - TT 58 chỉ áp dụng cho năm tài chính bắt đầu từ 01/7/2026 (khoản 1 Điều 12).

   Ban đầu công cụ trả `can_xac_nhan` thay vì đoán. **Cập nhật sau nghiên cứu (2026-10-16):** giữ TT 132 cả năm đó, áp TT 58 từ năm sau. Căn cứ là hỏi đáp của Cục Quản lý kế toán về TT 99 (cùng cấu trúc điều khoản) và khoản 3 Điều 4 TT 58. Công cụ ghi rõ kết luận này là suy luận (`co_so: suy_luan_tuong_tu`, `can_nguoi_duyet: true`). Xem điểm 1 trong `LEGAL-CITATIONS.md`.
5. **NĐ 214/2025 đã bị sửa ba lần trong năm 2026** (NĐ 165/2026, NĐ 170/2026, NĐ 349/2026). Tài liệu cũ chưa ghi điều này. Điều 31, căn cứ của bảng giá đánh giá, không bị sửa.
6. **Quy trình làm việc dùng trợ lý AI chạy trên nền tảng ở nước ngoài** có thể là chuyển dữ liệu cá nhân xuyên biên giới (điểm c khoản 1 Điều 20 Luật 91/2025), mà dữ liệu sức khỏe lại là dữ liệu nhạy cảm (NĐ 356/2025). Đây là việc của đơn vị, không phải lỗi mã. Xem điểm 4b trong `LEGAL-CITATIONS.md`.

## Hoãn, có lý do (cần mở issue có người nhận)

| Mục | Lý do hoãn | Rủi ro còn lại |
|---|---|---|
| Xác thực danh tính người duyệt (SSO / chữ ký số) | Cần một nhà cung cấp danh tính mà đơn vị tin cậy. Mã đã có điểm cắm `_ho_so.danh_tinh_host()`. | Mọi phê duyệt là tự khai (`UNVERIFIED_HUMAN_REVIEW`). |
| Tra trạng thái hóa đơn với cơ quan thuế | Cần kênh được cấp phép. Không tra qua trang không chính thức. | `trang_thai_cqt` luôn là `not_checked`. |
| XSD chính thức QĐ 1450 / chuẩn mới theo NĐ 254 | Không kèm XSD. Người dùng có thể đưa vào qua `--xsd`. | `xml_schema` mặc định `not_checked`. |
| Danh sách CA tin cậy cho chữ ký số hóa đơn | Danh sách CA được cấp phép do đơn vị tự cung cấp (`--ca-tin-cay`). Thời điểm đánh giá chứng thư là lúc chạy, không phải lúc ký. | Không có CA thì `chu_ky` tối đa là `not_checked` (kèm `toan_ven_chu_ky`). |
| Chính sách lưu trữ theo loại dữ liệu, legal hold (G10) | Đã đọc thời hạn (khoản 5 Điều 41 Luật Kế toán; Điều 12–14 NĐ 174/2016): bảng kê, bảng tổng hợp chi tiết lưu tối thiểu 10 năm. Công cụ cố ý không xoá gì; việc dọn theo danh mục lưu trữ là của đơn vị. Chưa có tính năng legal hold. | Hồ sơ giữ vô thời hạn và người dùng tự dọn. |
| Kiểm trích dẫn HSMT/HSDT từng tiêu chí ở chế độ chính thức (G09) | Phiếu kỹ thuật có `yeu_cau_hsmt` và `nguon_trang`, nhưng chưa có quy tắc bắt buộc. | Tổ chuyên gia vẫn phải tự đối chiếu. |
| Giới hạn tài nguyên khi đọc XLSX (zip bomb) | openpyxl không có giới hạn. Đường `read_only` đọc theo luồng. | Một file XLSX độc hại có thể ngốn bộ nhớ. |
| CI Windows | Đường dẫn font và PowerShell khác. Máy chạy thật của người dùng là Windows nhưng skill chạy ở máy xử lý macOS/Linux. | Chưa kiểm trên Windows. |
| Khoá ghi đồng thời sổ cái | Một người dùng một máy. Ghi nối thêm với `O_APPEND`. | Hai lần chạy song song có thể chen dòng. Chuỗi sẽ báo hỏng, không im lặng. |
