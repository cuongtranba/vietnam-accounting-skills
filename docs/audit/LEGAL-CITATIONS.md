# Ma trận trích dẫn pháp lý và phạm vi áp dụng — kiểm ngày 2026-10-16

Đây là chỉ mục tra cứu có trích dẫn, **không phải ý kiến pháp lý**. Mỗi dòng ghi rõ mức độ đã kiểm:

- **ĐÃ KIỂM:** đã đọc nguyên văn điều khoản trong bản Công báo (PDF tải từ `congbaocdn.chinhphu.vn`), qua trang văn bản trên `congbao.chinhphu.vn`.
- **MỘT PHẦN:** chỉ xác nhận được thuộc tính văn bản (số, ngày ban hành, ngày hiệu lực) trên cổng chính thức, chưa đọc điều khoản.
- **CHƯA KIỂM:** không truy cập được nguồn chính thức trong phiên này. Không được dùng làm căn cứ cho một kết luận có hệ quả.

Mã căn cứ trong máy (`che_do_ke_toan.CAN_CU`) là nơi duy nhất giữ các trích dẫn mà công cụ dùng để chọn chế độ.

| Văn bản | Ban hành | Hiệu lực | Điều khoản quyết định (trích nguyên văn ngắn) | Điều kiện năm tài chính / chuyển tiếp | Thay thế / sửa đổi | Phạm vi | Nguồn | Mức kiểm | Dùng ở đâu |
|---|---|---|---|---|---|---|---|---|---|
| TT 99/2025/TT-BTC — Chế độ kế toán doanh nghiệp | 27/10/2025 (Công báo số 1563+1564, 16/11/2025) | 01/01/2026 | Điều 31 khoản 1: “có hiệu lực thi hành kể từ ngày 01/01/2026 và áp dụng cho năm tài chính bắt đầu từ hoặc sau ngày 01/01/2026. Thông tư này thay thế cho các Thông tư số 200/2014/TT-BTC …” | Theo ngày BẮT ĐẦU năm tài chính. Năm 01/10/2025–30/09/2026 vẫn dùng TT 200; hỏi đáp CSTC của Bộ Tài chính cũng nêu ví dụ này. Khoản 2: phần kế toán cổ phần hóa DNNN của TT 200 vẫn áp dụng. Khoản 3: DNNVV, cơ sở ngoài công lập, đơn vị kế toán khác được chọn áp dụng. | Thay TT 200/2014, TT 75/2015, TT 53/2016, TT 195/2012 | Điều 2: doanh nghiệp thuộc mọi lĩnh vực, mọi thành phần kinh tế. Tổ chức tín dụng theo NHNN. | https://congbao.chinhphu.vn/van-ban/thong-tu-so-99-2025-tt-btc-46529.htm | **ĐÃ KIỂM** | `che_do_ke_toan.py` (TT99-D31, TT99-D2) |
| TT 200/2014/TT-BTC | 22/12/2014 | 01/01/2015 | (bị TT 99 thay) | Vẫn áp dụng cho năm tài chính bắt đầu trước 01/01/2026 | Đã sửa bởi TT 75/2015, TT 53/2016 | DN | Suy ra từ Điều 31 TT 99 | ĐÃ KIỂM (qua TT 99) | `che_do_ke_toan.py` |
| TT 133/2016/TT-BTC — DN nhỏ và vừa | 2016 | — | Không có trong danh sách bị TT 99 thay. TT 58/2026 Điều 4 khoản 3 vẫn dẫn chiếu “chế độ kế toán doanh nghiệp nhỏ và vừa”. | DNNVV chọn TT 133 hoặc TT 99 (khoản 3 Điều 31 TT 99) | — | DNNVV | Gián tiếp qua TT 99, TT 58 | **MỘT PHẦN** — chưa đọc văn bản gốc, chưa kiểm sửa đổi | `che_do_ke_toan.py` (`xac_minh: false`) |
| TT 58/2026/TT-BTC — DN siêu nhỏ | 25/5/2026 (Công báo số 323, 11/6/2026) | 01/7/2026 | Điều 12 khoản 1: “có hiệu lực thi hành kể từ ngày 01/7/2026 và áp dụng cho năm tài chính bắt đầu từ ngày hoặc sau ngày 01/7/2026”. Khoản 2: TT 132/2018 “hết hiệu lực kể từ ngày Thông tư này có hiệu lực thi hành”. Điều 4 khoản 3: “Việc thay đổi chế độ kế toán áp dụng chỉ được thực hiện tại ngày bắt đầu kỳ kế toán năm tiếp theo”. | Theo ngày BẮT ĐẦU năm tài chính. Năm tài chính vắt qua 01/7/2026 → **giữ TT 132 cả năm, TT 58 từ năm sau** (suy luận, xem điểm 1 bên dưới; công cụ trả `co_so: suy_luan_tuong_tu`, `can_nguoi_duyet: true`). | Thay TT 132/2018 | Điều 2: DN siêu nhỏ (tiêu chí theo pháp luật hỗ trợ DNNVV). Hộ, cá nhân kinh doanh được chọn áp dụng. Điều 4 khoản 3: được chọn chế độ DNNVV. | https://congbao.chinhphu.vn/van-ban/thong-tu-so-58-2026-tt-btc-469663.htm | **ĐÃ KIỂM** | `che_do_ke_toan.py` (TT58-D12, TT58-D2-D4, TT58-D4) |
| TT 24/2024/TT-BTC — Chế độ kế toán hành chính, sự nghiệp | 17/4/2024 (Công báo số 585+586, 06/5/2024) | 01/01/2025 | Điều 13 khoản 1: “có hiệu lực kể từ ngày 01 tháng 01 năm 2025 và áp dụng từ năm tài chính 2025”. Điều 2 khoản 1 điểm b: “Đơn vị sự nghiệp công lập (trừ các đơn vị sự nghiệp công lập tự đảm bảo chi thường xuyên và chi đầu tư được cơ quan có thẩm quyền cho phép áp dụng chế độ kế toán doanh nghiệp; … thì phải lập báo cáo quyết toán kinh phí hoạt động quy định tại Phụ lục III …)” | Từ năm tài chính 2025. Điều 14: chuyển số dư sau khi khoá sổ năm 2024. | Thay TT 107/2017, TT 108/2018, TT 76/2019, TT 79/2019 | Cơ quan nhà nước, ĐVSNCL (bệnh viện công), tổ chức dùng NSNN | https://congbao.chinhphu.vn/van-ban/thong-tu-so-24-2024-tt-btc-41775/49902.htm | **ĐÃ KIỂM** | `che_do_ke_toan.py` (TT24-D2, TT24-D13) |
| NĐ 60/2021/NĐ-CP — cơ chế tự chủ tài chính ĐVSNCL, **sửa bởi NĐ 111/2025/NĐ-CP** | NĐ 60: 21/6/2021; NĐ 111: 22/5/2025 (Công báo số 731+732, 06/6/2025) | NĐ 111: 07/7/2025, áp dụng từ năm ngân sách 2025 | Khoản 1 Điều 34 (sửa bởi khoản 22 Điều 1 NĐ 111): “Trường hợp đơn vị nhóm 1 xây dựng đề án quản lý, kế toán theo mô hình doanh nghiệp được cấp có thẩm quyền phê duyệt thì thực hiện theo chế độ kế toán doanh nghiệp (trừ đơn vị sự nghiệp công lập đang áp dụng cơ chế tài chính như doanh nghiệp không cần lập đề án được tiếp tục thực hiện chế độ kế toán doanh nghiệp)” | — | NĐ 111 sửa nhiều điều NĐ 60 | ĐVSNCL nhóm 1 (tự bảo đảm chi thường xuyên và chi đầu tư) | https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-60-2021-nd-cp-33931/36124.htm ; https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-111-2025-nd-cp-44943/56448.htm | **ĐÃ KIỂM** | `che_do_ke_toan.py` (ND60-D34) |
| NĐ 254/2026/NĐ-CP — Hóa đơn điện tử, chứng từ điện tử | 30/6/2026 (Công báo số 402, 16/7/2026) | 01/7/2026 | Điều 43: “có hiệu lực thi hành từ ngày 01 tháng 7 năm 2026 … hết hiệu lực thi hành: a) Nghị định số 123/2020/NĐ-CP …; b) Điều 1 Nghị định số 41/2022/NĐ-CP …; c) Nghị định số 70/2025/NĐ-CP”. Phụ lục, mục 6: chữ ký số người bán là chữ ký số của DN/tổ chức. Điều 8 khoản 9 điểm b: hóa đơn khởi tạo từ máy tính tiền “Không bắt buộc có chữ ký số”. Điều 10: người mua không nhất thiết phải có chữ ký số. | Điều 44 chỉ chuyển tiếp hóa đơn dự trữ quốc gia, biên lai giấy, hóa đơn đặt in. Không có chuyển tiếp chung cho hóa đơn đã lập — nhưng **khoản 2 Điều 24 TT 91/2026** gọi thẳng đó là hóa đơn “đã lập theo Nghị định số 123/2020/NĐ-CP, Nghị định số 70/2025/NĐ-CP và Thông tư số 32/2025/TT-BTC”, xử lý sai sót “theo quy định” hiện hành. | Thay NĐ 123/2020, Điều 1 NĐ 41/2022, NĐ 70/2025 | Tổ chức kinh tế, hộ/cá nhân kinh doanh … | https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-254-2026-nd-cp-469957.htm | **ĐÃ KIỂM** | `che_do_ke_toan.che_do_hoa_don`, `xac_thuc_hoa_don.py`, `doc_hoa_don.py` |
| TT 91/2026/TT-BTC — hướng dẫn NĐ 254/2026 | 30/6/2026 (Công báo số 464, 08/8/2026) | 01/7/2026 | Điều 25: hiệu lực 01/7/2026; “Thông tư số 32/2025/TT-BTC … hết hiệu lực thi hành”. Điều 24 khoản 2 (câu cuối): “Đối với hóa đơn đã lập theo Nghị định số 123/2020/NĐ-CP, Nghị định số 70/2025/NĐ-CP và Thông tư số 32/2025/TT-BTC thì thực hiện điều chỉnh hoặc thay thế theo quy định.” Điều 10: xử lý hóa đơn đã lập sai (điều chỉnh / thay thế). | Hóa đơn lập trước 01/7/2026 giữ căn cứ lập là NĐ 123/NĐ 70/TT 32; điều chỉnh/thay thế từ 01/7/2026 theo NĐ 254/TT 91 | Thay TT 32/2025 | — | https://congbao.chinhphu.vn/van-ban/thong-tu-so-91-2026-tt-btc-470171.htm | **ĐÃ KIỂM** | `che_do_ke_toan.che_do_hoa_don` (TT91, TT91-D24) |
| NĐ 141/2026/NĐ-CP — sửa NĐ 68/2026 (thuế hộ kinh doanh) | 29/4/2026 | 01/01/2026 | Thuộc tính trên chinhphu.vn: ngày ban hành 29-04-2026, ngày có hiệu lực 01-01-2026 (trước ngày ban hành) | Hồi tố: dùng làm kịch bản ACC-005 cho `bo_nho.py tra --ngay` | Sửa NĐ 68/2026, NĐ 320/2025 | Hộ, cá nhân kinh doanh | https://chinhphu.vn/?classid=0&docid=217960&pageid=27160 | **MỘT PHẦN** — chưa đọc điều khoản hiệu lực và mức ngưỡng | Kịch bản test (dữ liệu tổng hợp) |
| TT 04/2026/TT-KTNN — Hệ thống chuẩn mực KTNN | (bài đăng 03/3/2026) | 30/3/2026 | “có hiệu lực thi hành kể từ ngày 30/3/2026”; 43 chuẩn mực; “được áp dụng thống nhất trong toàn Ngành” | — | — | **Kiểm toán viên nhà nước.** Không phải tiêu chuẩn chứng nhận phần mềm. | https://sav.gov.vn/…/ban-hanh-thong-tu-so-04-2026-tt-ktnn-… | **MỘT PHẦN** (bài đăng chính thức, chưa đọc toàn văn) | CONTROL-MATRIX: chỉ là nguồn cảm hứng thiết kế (CMKTNN 2230, 2250, 2315, 2320, 2450, 2500, 2505 — tên chuẩn mực đã đối chiếu) |
| NĐ 214/2025/NĐ-CP — lựa chọn nhà thầu | 04/8/2025 (Công báo số 1063+1064, 17/8/2025) | 04/8/2025 (“kể từ ngày ký ban hành”) | Điều 31 (sửa lỗi, hiệu chỉnh sai lệch) — đọc nguyên văn bản gốc; điểm c khoản 2 và khoản 4 là nền của `so_sanh_thau.py` | — | Thay NĐ 24/2024 | Lựa chọn nhà thầu | https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-214-2025-nd-cp-45774.htm | **ĐÃ KIỂM** (2026-10-16) | `so_sanh_thau.py`, `references/dau-thau.md` |
| Sửa đổi NĐ 214: NĐ 165/2026, NĐ 170/2026 (15/5/2026, hiệu lực 01/7/2026), **NĐ 349/2026/NĐ-CP** (09/9/2026) | — | NĐ 349: “kể từ ngày ký ban hành” = 09/9/2026 (một bài báo ghi 20/10/2026 là sai) | NĐ 349 sửa Điều 18, 21, 35, 78, 79, 80, 84, 85, 98, 106, 117, 131, 132, 138, 140, 141, 146 — **không sửa Điều 31**. Văn bản hợp nhất 36/2026/VBHN-NĐ-BTC (23/9/2026): Điều 31 trùng bản gốc (so khớp sau OCR, không có đoạn khác > 6 từ) | Điều 27 NĐ 349: chuyển tiếp cho gói thầu đang làm | — | — | NĐ 349: https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/9/349_2026_nd-cp_09092026-signed.signed.pdf ; VBHN: https://xdcs.cdnchinhphu.vn/446259493575335936/2026/9/25/36-vbhn-btc-signed-1790318157417695015082.pdf | **ĐÃ KIỂM** (bản quét, đọc bằng OCR tiếng Việt); NĐ 165, NĐ 170: **MỘT PHẦN** (chỉ biết qua danh sách trong VBHN) | `references/dau-thau.md`, `references/phap-ly.md` |
| TT 103/2005/TT-BTC — tiêu chuẩn phần mềm kế toán | 2005 | — | Trang vbpl.vn tải động, không đọc được (thử 3 đường dẫn) | — | — | Phần mềm kế toán | https://vbpl.vn/bonongnghiep/Pages/vbpq-thuoctinh.aspx?ItemID=17130 | **CHƯA KIỂM** | Không dùng (xem điểm 4) |
| Luật Kế toán 88/2015/QH13 (sửa đổi 29/11/2024) | 20/11/2015 (Công báo số 1241+1242) | 01/01/2017 | Khoản 7 Điều 26: “Đơn vị kế toán được ghi sổ kế toán bằng phương tiện điện tử …” — lưu trên phương tiện điện tử “phải bảo đảm an toàn, bảo mật thông tin dữ liệu và phải bảo đảm tra cứu được trong thời hạn lưu trữ”. Khoản 5 Điều 41: lưu ít nhất 05 năm / 10 năm / vĩnh viễn. Không có điều nào riêng về “phần mềm kế toán”. | — | Sửa bởi Luật ngày 29/11/2024 (chưa đọc bản sửa) | Mọi đơn vị kế toán | https://congbao.chinhphu.vn/van-ban/luat-so-88-2015-qh13-18393.htm | **ĐÃ KIỂM** (bản gốc 2015) | `references/phap-ly.md`, `references/kiem-soat.md` |
| NĐ 174/2016/NĐ-CP — chi tiết Luật Kế toán | 30/12/2016 (Công báo số 51+52, 15/01/2017) | — | Điều 13 khoản 1: lưu **tối thiểu 10 năm** “chứng từ kế toán sử dụng trực tiếp để ghi sổ kế toán và lập báo cáo tài chính, các bảng kê, bảng tổng hợp chi tiết, các sổ kế toán chi tiết, các sổ kế toán tổng hợp, báo cáo tài chính …”. Điều 12: tối thiểu 5 năm. Điều 14: vĩnh viễn. Điều 10: tài liệu lưu trên phương tiện điện tử. | — | Chưa kiểm văn bản sửa đổi | Mọi đơn vị kế toán | https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-174-2016-nd-cp-21879.htm | **ĐÃ KIỂM** (bản gốc) | Chính sách không tự xoá hồ sơ (G10), `references/kiem-soat.md` |
| Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 | 26/6/2025 (Công báo số 971+972, 24/7/2025) | 01/01/2026 (Điều 38 khoản 1) | Điều 2 khoản 1: dữ liệu đã khử nhận dạng “không còn là dữ liệu cá nhân”. Điều 19 khoản 1: xử lý không cần đồng ý khi “c) Phục vụ hoạt động của cơ quan nhà nước…”, “đ) Trường hợp khác theo quy định của pháp luật”; khoản 2: phải có cơ chế giám sát. **Điều 20 khoản 1 điểm c:** “sử dụng nền tảng ở ngoài lãnh thổ … để xử lý dữ liệu cá nhân được thu thập tại Việt Nam” là chuyển dữ liệu xuyên biên giới → khoản 2: lập hồ sơ đánh giá tác động, gửi trong 60 ngày. Điều 21: đánh giá tác động xử lý. Điều 26: thông tin sức khỏe. | Điều 38 khoản 2–3: DN nhỏ/siêu nhỏ được miễn Điều 21, 22 có thời hạn — trừ khi trực tiếp xử lý dữ liệu nhạy cảm | Thay NĐ 13/2023 (qua NĐ 356/2025) | Mọi tổ chức, cá nhân xử lý dữ liệu cá nhân tại Việt Nam | https://congbao.chinhphu.vn/van-ban/luat-so-91-2025-qh15-45578.htm | **ĐÃ KIỂM** | SKILL.md nguyên tắc 6, `references/kiem-soat.md`, `references/phap-ly.md` |
| NĐ 356/2025/NĐ-CP — chi tiết Luật BVDLCN | 31/12/2025 (Công báo số 18, 18/01/2026) | 01/01/2026 (Điều 42 khoản 1) | Điều 4 khoản 1: danh mục dữ liệu nhạy cảm, gồm “d) Tình trạng sức khỏe”, “k) … thông tin tài chính, tín dụng …” | — | Điều 42 khoản 2: NĐ 13/2023 hết hiệu lực | — | https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-356-2025-nd-cp-468371.htm | **ĐÃ KIỂM** | như trên |
| Hỏi đáp CSTC 159102 — Cục Quản lý kế toán, Bộ Tài chính (14/01/2026) | — | — | Năm tài chính 01/10/2025–30/09/2026 “chưa áp dụng” TT 99 tại 01/01/2026, áp dụng từ năm tài chính bắt đầu 01/10/2026 | Dùng để suy cho TT 58 (cùng cách viết điều khoản hiệu lực) | — | — | https://portal.mof.gov.vn/hoidapcstc/home/cthoidap/159102 | **ĐÃ KIỂM** (trang chính thức của Bộ Tài chính; là hướng dẫn, không phải văn bản quy phạm) | `che_do_ke_toan.py` (QLKT-HD-159102) |

## Năm điểm cần người có chuyên môn xác nhận — kết quả nghiên cứu (2026-10-16)

Người nghiên cứu là trợ lý AI (Claude), làm theo yêu cầu của người dùng, dựa trên nguyên văn các văn bản trên Công báo và cổng Bộ Tài chính ghi ở bảng trên. Mỗi điểm ghi kết luận đề xuất, căn cứ, mức chắc chắn, và việc công cụ đã làm theo kết luận đó. Đây là **kết quả nghiên cứu, không phải chữ ký**. Ô ký để trống cho người có chuyên môn.

### 1. DN siêu nhỏ có năm tài chính vắt qua 01/7/2026

- **Kết luận đề xuất.** Giữ TT 132/2018 cho **cả** năm tài chính đó. Áp TT 58/2026 từ năm tài chính kế tiếp (ví dụ năm 01/4/2026–31/3/2027 dùng TT 132; năm bắt đầu 01/4/2027 dùng TT 58).
- **Căn cứ.**
  - Khoản 1 Điều 12 TT 58: chỉ áp cho năm tài chính bắt đầu từ hoặc sau 01/7/2026.
  - Khoản 3 Điều 4 TT 58: “việc thay đổi chế độ kế toán áp dụng chỉ được thực hiện tại ngày bắt đầu kỳ kế toán năm tiếp theo”.
  - Trả lời của Cục Quản lý kế toán (hỏi đáp CSTC 159102, 14/01/2026) cho TT 99, văn bản viết điều khoản hiệu lực cùng cấu trúc (hiệu lực từ một ngày, áp cho năm tài chính bắt đầu từ hoặc sau, thay văn bản cũ): năm tài chính 01/10/2025–30/09/2026 “chưa áp dụng” chế độ mới.
- **Điểm chưa chắc.** Khoản 2 Điều 12 TT 58 viết TT 132 “hết hiệu lực” từ 01/7/2026, một câu mà TT 99 không có. Chưa thấy hướng dẫn riêng của Bộ Tài chính cho TT 58. Kết luận là **suy luận tương tự**, mức chắc chắn trung bình.
- **Công cụ đã đổi.** Trả `xac_dinh` → `TT132/2018`, kèm `co_so: suy_luan_tuong_tu` và `can_nguoi_duyet: true` (test ACC-003). Trước đây trả `can_xac_nhan`.
- **Người xác nhận:** ____________ **Ngày:** ________ **Đồng ý / Sửa:** ____________

### 2. Hóa đơn lập trước 01/7/2026 xét theo NĐ 123/2020

- **Kết luận đề xuất.** Đúng. Hóa đơn lập trước 01/7/2026 là hóa đơn lập theo NĐ 123/2020, NĐ 70/2025 và TT 32/2025. Nếu điều chỉnh hay thay thế nó từ 01/7/2026 thì làm theo NĐ 254/2026 và TT 91/2026.
- **Căn cứ.**
  - Câu cuối khoản 2 Điều 24 TT 91/2026: “Đối với hóa đơn đã lập theo Nghị định số 123/2020/NĐ-CP, Nghị định số 70/2025/NĐ-CP và Thông tư số 32/2025/TT-BTC thì thực hiện điều chỉnh hoặc thay thế theo quy định.”
  - Điều 43 NĐ 254, khoản 2 Điều 25 TT 91.
- **Mức chắc chắn.** Cao. Trước đây chồng ghi đây là “cách hiểu về hiệu lực theo thời gian”; nay đã có câu chữ trực tiếp.
- **Công cụ đã đổi.** `che_do_hoa_don` dẫn thêm TT91-D24 và ghi chú phần điều chỉnh/thay thế. TT 91 nâng lên ĐÃ KIỂM.
- **Người xác nhận:** ____________ **Ngày:** ________ **Đồng ý / Sửa:** ____________

### 3. ĐVSNCL nhóm 1 dùng chế độ kế toán doanh nghiệp

- **Kết luận đề xuất (sửa lại điều đã ghi trước đây).** Chỉ đơn vị **nhóm 1** (tự bảo đảm chi thường xuyên và chi đầu tư) mới được, và phải thuộc một trong hai trường hợp:
  - (a) có **đề án quản lý, kế toán theo mô hình doanh nghiệp được cấp có thẩm quyền phê duyệt**; hoặc
  - (b) **đang áp dụng cơ chế tài chính như doanh nghiệp**: không cần lập đề án, được tiếp tục dùng chế độ kế toán doanh nghiệp.

  Các trường hợp còn lại dùng TT 24/2024. Dù dùng chế độ doanh nghiệp, đơn vị có NSNN, viện trợ, vay nợ hay phí được để lại vẫn lập báo cáo quyết toán kinh phí theo Phụ lục III TT 24.
- **Căn cứ.**
  - Khoản 1 Điều 34 NĐ 60/2021, đã sửa bởi khoản 22 Điều 1 NĐ 111/2025 (hiệu lực 07/7/2025, áp dụng từ năm ngân sách 2025).
  - Điểm b khoản 1 Điều 2 TT 24/2024.
- **Mức chắc chắn.** Cao, vì có câu chữ trực tiếp. Còn để ngỏ: “đang áp dụng cơ chế tài chính như doanh nghiệp” phải hiểu theo văn bản giao tự chủ của từng đơn vị. Đây là việc của đơn vị, công cụ không suy ra được.
- **Công cụ đã đổi.** Thêm căn cứ ND60-D34. Câu hỏi và phần trợ giúp `--duoc-phep-ap-dung-che-do-dn` nêu đủ hai trường hợp. Logic chọn chế độ giữ nguyên.
- **Người xác nhận:** ____________ **Ngày:** ________ **Đồng ý / Sửa:** ____________

### 4. Phạm vi “phần mềm kế toán” và Luật 91/2025 với dữ liệu bệnh nhân

- **4a — TT 103/2005.**
  - **Vẫn CHƯA KIỂM**: trang vbpl.vn tải nội dung động nên không đọc được.
  - Luật Kế toán 2015 không có điều riêng về “phần mềm kế toán”; khoản 7 Điều 26 chỉ quy định việc ghi sổ bằng phương tiện điện tử.
  - **Đề xuất:** công cụ không ghi sổ kế toán, không giữ sổ cái. Nó tạo bảng kê và bảng tổng hợp làm đầu vào cho phần mềm kế toán của đơn vị. Vì vậy không tự nhận là “phần mềm kế toán”, và coi tiêu chí TT 103 là thực hành tốt, không phải điều kiện bắt buộc.
  - Cần người có chuyên môn xác nhận sau khi đọc được TT 103 (và xem nó còn hiệu lực không).
- **4b — Luật 91/2025.**
  - **Có áp dụng.** File kết xuất có mã/tên bệnh nhân và dịch vụ khám chữa bệnh, tức “tình trạng sức khỏe”: dữ liệu cá nhân **nhạy cảm** (điểm d khoản 1 Điều 4 NĐ 356/2025).
  - Xử lý để làm nghĩa vụ kế toán, thuế có thể thuộc trường hợp không cần đồng ý (điểm c, điểm đ khoản 1 Điều 19 Luật 91). Đơn vị vẫn phải có cơ chế giám sát (khoản 2 Điều 19), và việc xếp vào trường hợp nào thuộc về người phụ trách bảo vệ dữ liệu của đơn vị.
  - **Điểm quan trọng nhất:**
    - Theo câu chữ của điểm c khoản 1 Điều 20, đưa nội dung dòng dữ liệu vào một trợ lý AI chạy trên nền tảng ở nước ngoài **có thể là chuyển dữ liệu cá nhân xuyên biên giới**. Khi đó phải lập hồ sơ đánh giá tác động và gửi trong 60 ngày (khoản 2).
    - Bệnh viện công là ĐVSNCL, không phải “cơ quan nhà nước có thẩm quyền”, nên có thể không thuộc miễn trừ ở điểm a khoản 6 Điều 20.
    - **Đề xuất:**
      - đơn vị (bên kiểm soát dữ liệu) xác định trường hợp này và lập hồ sơ đánh giá tác động nếu thuộc;
      - trong khi chờ, chỉ đưa vào cuộc trò chuyện số tổng hợp hoặc dữ liệu đã khử nhận dạng (dữ liệu đã khử nhận dạng không còn là dữ liệu cá nhân, khoản 1 Điều 2);
      - script vẫn đọc file tại chỗ.
- **Công cụ / tài liệu đã đổi.**
  - Nguyên tắc 6 trong SKILL.md mở rộng sang dữ liệu cá nhân.
  - `references/kiem-soat.md` và `references/phap-ly.md` có mục dữ liệu cá nhân và lưu trữ.
  - Chính sách không tự xoá hồ sơ dựa trên khoản 1 Điều 13 NĐ 174/2016: bảng kê, bảng tổng hợp chi tiết lưu tối thiểu 10 năm.
- **Người xác nhận (pháp chế / bảo vệ dữ liệu):** ____________ **Ngày:** ________ **Đồng ý / Sửa:** ____________

### 5. NĐ 214/2025 kiểm lại

- **Kết luận.**
  - NĐ 214/2025 vẫn là văn bản đang áp dụng. Nó đã bị sửa bởi:
    - NĐ 165/2026, NĐ 170/2026 (ban hành 15/5/2026, hiệu lực 01/7/2026);
    - NĐ 349/2026 (09/9/2026, hiệu lực từ ngày ký).
  - **Điều 31 không bị sửa**, nên mọi phép tính của `so_sanh_thau.py` (điểm c khoản 2 và khoản 4 Điều 31) giữ nguyên căn cứ.
  - Tra số điều theo văn bản hợp nhất 36/2026/VBHN-NĐ-BTC (23/9/2026).
- **Căn cứ.**
  - Điều 31 bản gốc (Công báo số 1063+1064).
  - Danh sách điều được sửa trong NĐ 349 (OCR toàn văn bản quét).
  - Điều 31 trong VBHN 36/2026 (OCR, so khớp với bản gốc).
  - Điều 28 NĐ 349: hiệu lực từ ngày ký.
- **Mức chắc chắn.** Cao với NĐ 349. Với NĐ 165 và NĐ 170 (nghị định hướng dẫn Luật Phòng bệnh và Luật Thi hành án hình sự, sửa NĐ 214 kèm theo) mới biết qua VBHN. Việc Điều 31 trong VBHN trùng bản gốc gián tiếp cho thấy hai nghị định này cũng không đụng Điều 31.
- **Lưu ý.**
  - Hạn kiểm lại tiếp theo là 2026-11-30 (TTL 45 ngày).
  - Theo báo chí, Bộ Tài chính dự kiến trình Luật Đấu thầu (sửa đổi) tại kỳ họp tháng 10/2026. Nếu được thông qua thì phải tra lại toàn bộ số điều.
- **Công cụ / tài liệu đã đổi.** Cập nhật `references/dau-thau.md`, `references/phap-ly.md` và chuỗi `can_cu_phap_ly` của `so_sanh_thau.py`.
- **Người xác nhận:** ____________ **Ngày:** ________ **Đồng ý / Sửa:** ____________

## Cách kiểm lại

```bash
# Tải bản Công báo và tìm điều khoản (ví dụ TT 58/2026)
curl -sL https://congbao.chinhphu.vn/van-ban/thong-tu-so-58-2026-tt-btc-469663.htm \
  | grep -oE 'https://congbaocdn[^"]+\.pdf' | head -1
# rồi đọc Điều 12 trong PDF; so với CAN_CU["TT58-D12"] trong scripts/che_do_ke_toan.py
```
