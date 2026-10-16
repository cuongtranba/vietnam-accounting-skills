# Ma trận kiểm soát — skill ke-toan-vn

**Về cột CMKTNN.** Cột “Gợi ý từ CMKTNN” chỉ ghi nguồn cảm hứng thiết kế. Hệ thống chuẩn mực KTNN (TT 04/2026/TT-KTNN, hiệu lực 30/3/2026) quy định trách nhiệm của **kiểm toán viên nhà nước**. Nó không phải tiêu chuẩn chứng nhận phần mềm. Công cụ này **không** được KTNN hay cơ quan nào chứng nhận, và các kiểm soát dưới đây không phải điều kiện pháp lý bắt buộc với mọi công cụ hỗ trợ kế toán.

Test ID là tên phép kiểm trong `evals/kiem_soat.py` (mã trong ngoặc vuông) hoặc trong `evals/kiem_thu.py`. Bằng chứng nằm ở `docs/audit/evidence/`. Người chịu trách nhiệm (owner) hiện là người duy trì repo cho đến khi có phân công khác.

| ID | Rủi ro | Gợi ý từ CMKTNN / căn cứ | Cách làm | Test | Bằng chứng | Rủi ro còn lại |
|---|---|---|---|---|---|---|
| C-01 Chế độ kế toán theo năm tài chính | Áp nhầm TT 200 cho năm tài chính 2026, hoặc đổi chế độ giữa năm | 2250 (tuân thủ pháp luật). Điều 31 TT 99/2025, Điều 12 TT 58/2026, Điều 2 và 13 TT 24/2024 | `che_do_ke_toan.py`: chọn theo loại đơn vị + ngày bắt đầu năm tài chính, kèm trích dẫn; thiếu thông tin thì `can_xac_nhan` (mã 2) | ACC-001, ACC-002 (×2), ACC-003, ACC-004 (×2), “loại đơn vị khác”, “năm 2024 vẫn TT 200”, “DNNVV” | `evidence/03-green-kiem-soat.txt` | Bảng căn cứ cần cập nhật khi có văn bản mới; TT 133 mới kiểm gián tiếp; DN siêu nhỏ có năm tài chính vắt qua 01/7/2026 được chọn theo suy luận tương tự (`co_so: suy_luan_tuong_tu`, `can_nguoi_duyet: true`) |
| C-02 Quy định theo ngày hiệu lực | Ghi chú “còn hạn” bị dùng cho kỳ không áp dụng; văn bản hồi tố không được cảnh báo | 2250, 2230 | `bo_nho.py tra --ngay`, `lich-su`; ghi `--hieu-luc-tu/--hieu-luc-den/--ngay-ban-hanh/--dieu-khoan/--sua-doi`; cờ `hoi_to`; cờ `can_nguoi_duyet` | ACC-005 (×2), “năm thuế cũ/mới”, “chưa hiệu lực”, “không rõ hiệu lực” | như trên | Ngày hết hiệu lực của bản cũ có thể là SUY RA (`hieu_luc_den_suy_ra`); diễn giải chưa có người có chuyên môn duyệt |
| C-03 Đọc ≠ xác thực hóa đơn | XML đọc được bị coi là thật; hóa đơn thứ hai trong thông điệp biến mất | 2500 (bằng chứng), 2505 (xác nhận từ bên ngoài) | `xac_thuc_hoa_don.py`: tách 3 trạng thái `xml_schema` / `chu_ky` / `trang_thai_cqt`; chỉ `valid` khi chữ ký toàn vẹn **và** chuỗi về CA đã cung cấp; `trang_thai_cqt` luôn `not_checked`; mỗi `<HDon>` một dòng; thẻ lặp khác giá trị thì để trống | INV-001, INV-002, INV-005, “namespace”, “XML hỏng”, “chữ ký toàn vẹn chưa có CA”, “có CA → valid”, “chứng thư không khớp”, “thiếu thư viện → not_checked” | như trên; `evidence/04-kiem-soat-khong-signxml.txt` | Không có kênh tra cứu cơ quan thuế; không kèm XSD chính thức; chứng thư được đánh giá tại thời điểm chạy |
| C-04 Cổng đầy đủ | Tổng thiếu một hóa đơn trông như tổng cuối; hóa đơn trùng bị cộng đôi | 2450 (đánh giá sai sót), 2320 (trọng yếu) | `tong_da_kiem` chỉ có khi đủ dữ liệu; `trang_thai` draft/needs_review; không cộng hóa đơn trùng; `--yeu-cau-day-du` trả mã 2 | INV-003 (×3), INV-004, “điều chỉnh âm / 0 đồng” | như trên | Mã thoát mặc định vẫn là 0 (để tương thích); bên gọi phải dùng `--yeu-cau-day-du` |
| C-05 Bố cục trước khi ghi, ghi nguyên tử | Cột đổi nghĩa vẫn cho ra file; thông báo `can_hoi` sai sự thật; lô ghi dở dang | 2315 (rủi ro sai sót trọng yếu) | `kiem_bo_cuc` chạy trước khi đọc dữ liệu (`vo_hai` / `nghiem_trong`); `BoGhi` ghi file tạm rồi đổi tên, công bố cả lô hoặc không gì; `--xem-truoc`, `--chap-nhan-bo-cuc` | WF-001 (×2), WF-002 (×2), WF-003, “xem trước”, “lô không ghi dở dang” | như trên | Nếu hệ điều hành lỗi đúng lúc đang đổi tên nhiều file, lô có thể chỉ công bố được một phần (đích đã được kiểm trước) |
| C-06 Hồ sơ lần chạy + sổ cái | Không chứng minh được kết quả đến từ nguồn nào, theo quy tắc nào | 2230 (tài liệu, hồ sơ), 2500 | `_ho_so.py`: SHA-256 đầy đủ của nguồn/quy tắc/danh mục/kết quả, `ket_qua_sha256`, kiểm soát, ngoại lệ, giờ có múi giờ; sổ cái nối chuỗi mã băm; `kiem`, `kiem-so-cai`, `phat-lai`, `xuat`, `kiem-goi` | AUD (×4), AUD-001, AUD-002, “gói kiểm toán”, “kiểm độc lập”, “sửa tay hồ sơ” | như trên; `examples/goi-kiem-toan-mau/` | Sổ cái chỉ CHỐNG SỬA ÂM THẦM, không phải bất biến: ai có quyền ghi vẫn xoá được cả sổ. Nên sao lưu sổ hoặc gửi mã băm dòng cuối cho bên thứ ba |
| C-07 Ghi nhận duyệt trung thực | Cờ dòng lệnh được hiểu là phê duyệt; không biết ai duyệt cái gì | 2230; tách nhiệm | `ho_so_kiem_toan.py duyet` gắn với mã băm hồ sơ; luôn `UNVERIFIED_HUMAN_REVIEW`; tối đa `da_xem_chua_xac_thuc`; nội dung đổi → `vo_hieu`; needs_review cần `--ngoai-le`; `tach_nhiem` | G07 (×5), INV-003 (duyệt), TEN-001 (duyệt chéo) | như trên | Không có xác thực danh tính: `approved` không đạt được — có chủ ý. Cần tích hợp nhà cung cấp danh tính (`danh_tinh_host`) |
| C-08 Không phá huỷ bản đã duyệt và ghi chú cũ | Bản đã duyệt bị ghi đè; mất phiên bản ghi chú trong cùng ngày | 2230 | Kết quả đã có người đồng ý thì không ghi đè (dừng hỏi, hoặc `--ban-sua-doi` → `-SUA<n>` với `sua_doi_cho`); bản lưu trữ ghi chú `.cu-YYYY-MM-DD-NNN` | G08 (×2), AUD-003 | như trên | Trước khi duyệt vẫn ghi đè (đúng quy ước làm việc của người dùng) |
| C-09 Chấm thầu: sơ bộ khác chính thức | Bảng xếp hạng sơ bộ bị dùng như kết luận khi thiếu bước kỹ thuật | Điểm c khoản 2 Điều 31 NĐ 214/2025 | `so_sanh_thau.py --che-do chinh-thuc`: không xếp hạng khi thiếu kết luận kỹ thuật (mã 2); `trang_thai` so_bo / needs_review / cho_to_chuyen_gia_ky; chấm thầu không ghi gì vào bộ nhớ | BID-001 (×3), “sơ bộ ghi rõ trạng thái”, “không ghi vào bộ nhớ” | như trên | Chưa bắt buộc trích dẫn HSMT từng tiêu chí; NĐ 214 kiểm lại ngày 2026-10-16 (đã sửa bởi NĐ 165, 170, 349/2026, Điều 31 không đổi); lần kiểm sau: 2026-11-30 |
| C-10 Cô lập đơn vị | Danh mục/quy trình của đơn vị này áp nhầm cho đơn vị khác | Luật 91/2025 (Điều 19, 20, 26); NĐ 356/2025 (Điều 4); NĐ 174/2016 (Điều 13) | `--don-vi` → `<bộ nhớ>/don-vi/<mã>/`; chặn `../`; hồ sơ mang mã đơn vị; không script nào gọi mạng | TEN-001 (×4), “mã đơn vị ../”, “không gọi mạng” | như trên | Chưa có legal hold; chưa mã hoá khi lưu. Đưa dữ liệu dòng vào trợ lý AI ở nước ngoài có thể là chuyển dữ liệu xuyên biên giới — việc của đơn vị (LEGAL-CITATIONS điểm 4b) |
| C-11 Bất biến kế toán | So khớp file mẫu giữ lại chính lỗi của file mẫu (cộng trùng dòng tổng) | 2450 | `loc`: bảo toàn dòng và tiền, đọc lại file tạm trước khi công bố; `tach`: nguồn = nhóm + ngoài nhóm; phát hiện dòng tổng hoặc công thức cộng dồn; cấm STT làm khoá | G11 (×5) | như trên | `tach` giữ công thức nên không đọc lại được số (cần LibreOffice tính lại); nhận diện dòng tổng theo nhãn có thể bỏ sót cách ghi lạ |
| C-12 Đầu vào không tin cậy | XML độc, file khổng lồ, chuỗi thành công thức khi mở file | — | Từ chối DOCTYPE/ENTITY; giới hạn 20 MB (XML) và 50 MB (PDF); `o_an_toan` cho CSV/XLSX; `giu_chu` khi chép ô; CI ghim phiên bản, chạy trên Ubuntu và macOS | SEC-001 (×3), “XML > 20 MB” | như trên | Chưa giới hạn khi đọc XLSX (zip bomb); chưa có CI Windows |

## Ánh xạ gap → kiểm soát → test

| Gap | Kiểm soát | Kịch bản trong handoff |
|---|---|---|
| G01 | C-01 | ACC-001, ACC-002, ACC-003, ACC-004 |
| G02 | C-02 | ACC-005 |
| G03 | C-03 | INV-001, INV-002, INV-005 |
| G04 | C-04 | INV-003, INV-004 |
| G05 | C-05 | WF-001, WF-002, WF-003 |
| G06 | C-06 | AUD-001, AUD-002 |
| G07 | C-07 | AUD-001, TEN-001 |
| G08 | C-08 | AUD-003 |
| G09 | C-09 | BID-001 |
| G10 | C-10 | TEN-001 |
| G11 | C-11 | WF-003, INV-004 |
| G12 | C-12 | SEC-001 |
