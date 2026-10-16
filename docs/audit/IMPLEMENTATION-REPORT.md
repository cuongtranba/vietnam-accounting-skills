# Báo cáo triển khai — kiểm soát kiểm toán được (P0/P1, gia cố P2)

**Ngày:** 2026-10-16 · **Nhánh:** `feat/audit-controls-p0-p1` · **Gốc:** `main` @ `e0e6921` (v0.4.0)

Đây **không** phải ý kiến kiểm toán, ý kiến pháp lý hay chứng nhận của Kiểm toán Nhà nước. Nó báo cáo việc đã làm, bằng chứng test, và những gì còn phải người duyệt quyết định.

## 1. HEAD và baseline

| Mục | Giá trị |
|---|---|
| Baseline | `e0e6921`. `evals/kiem_thu.py` **65/65** ([00-baseline](evidence/00-baseline-kiem-thu-e0e6921.txt)) |
| Tái hiện trước khi sửa | `evals/kiem_soat.py` phần P0: 38 hỏng / 4 đạt ([01-red](evidence/01-red-p0-truoc-khi-sua.txt)) |
| Commit P0 | `91d8c3a` |
| Commit P1 | `632ffc3` |
| Commit P2 + tài liệu | xem `git log` của PR (commit cuối cùng của nhánh) |
| Sau khi sửa | `kiem_thu.py` **65/65** ([02](evidence/02-green-kiem-thu.txt)) · `kiem_soat.py` **82/82** khi có signxml ([03](evidence/03-green-kiem-soat.txt)) · **79/79** khi không có signxml, chạy nhánh dự phòng ([04](evidence/04-kiem-soat-khong-signxml.txt)) |
| Tương thích | Cả 5 quy trình thật đang dùng (`.ke-toan-vn/quy-trinh/*.toml`) đều qua `quy_trinh.py kiem` với mã mới. Lệnh chỉ kiểm cú pháp, không đọc dữ liệu. |

Lệnh tái lập:

```bash
pip install -r evals/requirements-ci.txt
python evals/tao_fixtures.py
KE_TOAN_VN_HOME=$(mktemp -d) python evals/kiem_thu.py
python evals/kiem_soat.py
python evals/tao_goi_kiem_toan_mau.py      # gói mẫu + kiểm độc lập
```

## 2. Kết quả theo từng gap

| Gap | Phán định | Kết quả | Test |
|---|---|---|---|
| G01 Chế độ kế toán / năm tài chính | Xác nhận | **Đã sửa, có test** | ACC-001…004 và 5 phép khác |
| G02 Quy định theo ngày hiệu lực | Xác nhận | **Đã sửa, có test** | ACC-005 và 6 phép khác |
| G03 Đọc ≠ xác thực hóa đơn | Xác nhận | **Đã sửa, có test**. Chưa có kênh tra cứu cơ quan thuế (`not_checked`). | INV-001, 002, 005 và 7 phép khác |
| G04 Cổng đầy đủ | Xác nhận | **Đã sửa, có test** | INV-003, 004 và các phép khác |
| G05 Bố cục trước khi ghi | Xác nhận, nặng hơn giả thuyết | **Đã sửa, có test** | WF-001…003 và các phép khác |
| G06 Hồ sơ lần chạy | Xác nhận một phần | **Đã sửa, có test** | AUD, AUD-001, AUD-002 |
| G07 Ghi nhận duyệt | Xác nhận | **Đã sửa ở mức trung thực**. Chưa xác thực danh tính, nên tối đa `da_xem_chua_xac_thuc`. | G07 ×5, TEN-001 |
| G08 Không phá huỷ bản cũ | Xác nhận | **Đã sửa, có test** | AUD-003, G08 ×2 |
| G09 Chấm thầu chính thức | Xác nhận | **Đã sửa, có test**. Hoãn: bắt buộc trích dẫn HSMT từng tiêu chí. | BID-001 ×3 và 2 phép khác |
| G10 Cô lập đơn vị | Xác nhận | **Đã sửa, có test**. Hoãn: chính sách lưu trữ theo loại dữ liệu, legal hold. | TEN-001 ×4 và 2 phép khác |
| G11 Bất biến kế toán | Xác nhận | **Đã sửa, có test** | G11 ×6 |
| G12 Gia cố | Xác nhận một phần | **Đã gia cố phần có tác động**: DOCTYPE/ENTITY, giới hạn kích thước, công thức khi xuất, ghim phiên bản, CI Ubuntu + macOS. Hoãn: zip bomb XLSX, CI Windows. | SEC-001 ×3 và 1 phép khác |

Chi tiết từng gap, vị trí dòng mã và các phát hiện ngoài handoff: [`2026-10-16-gap-register.md`](2026-10-16-gap-register.md). Kiểm soát nào ứng với test nào: [`CONTROL-MATRIX.md`](CONTROL-MATRIX.md).

## 3. Ma trận trích dẫn pháp lý

Xem [`LEGAL-CITATIONS.md`](LEGAL-CITATIONS.md).

- **Đã đọc nguyên văn bản Công báo:** TT 99/2025 (Điều 2, 31), TT 58/2026 (Điều 2, 4, 12), TT 24/2024 (Điều 2, 13, 14), NĐ 254/2026 (Điều 5, 8, 10, 43, 44, Phụ lục mục 6).
- **Một phần:** TT 133/2016 (gián tiếp), TT 91/2026, NĐ 141/2026, TT 04/2026/TT-KTNN.
- **Chưa kiểm:** TT 103/2005, NĐ 174/2016, Luật 91/2025. NĐ 214/2025 dựa vào lần kiểm ở PR #2 và cần kiểm lại trước 2026-10-28.

## 4. File và giao diện thay đổi

**Mới:**
- `scripts/che_do_ke_toan.py`
- `scripts/xac_thuc_hoa_don.py`
- `scripts/_ho_so.py`
- `scripts/ho_so_kiem_toan.py`
- `references/kiem-soat.md`
- `evals/kiem_soat.py`
- `evals/tao_goi_kiem_toan_mau.py`
- `evals/requirements-ci.txt`
- `docs/audit/*`

**Sửa:** `doc_hoa_don.py`, `bo_nho.py`, `quy_trinh.py`, `_quy_trinh.py`, `_loc.py`, `_tach.py`, `_doi_chieu_bang.py`, `_xuat.py`, `_chung.py`, `so_sanh_thau.py`, `bootstrap.sh` (thêm `signxml`), `SKILL.md`, `references/{phap-ly,bao-cao,hoa-don,bo-nho,quy-trinh,dau-thau}.md`, `README.md`, `.github/workflows/ci.yml`.

| Lệnh | Mới / đổi |
|---|---|
| `che_do_ke_toan.py` | `--loai-don-vi`, `--dau-nam-tai-chinh` hoặc `--ngay` + `--thang-dau-nam`, `--da-chon`, `--tu-chu`, `--duoc-phep-ap-dung-che-do-dn`, `--hoa-don-ngay`. Mã thoát 0 xác định / 2 cần xác nhận / 1 lỗi. |
| `doc_hoa_don.py` | `--ca-tin-cay`, `--xsd`, `--yeu-cau-day-du` (mã 2), `--ghi-ho-so`, `--don-vi`, `--nguoi-lap`. JSON thêm `xac_thuc`, `che_do_hoa_don`, `trang_thai_dong`, `tom_tat.{tong_da_kiem, kiem_soat, trang_thai, ly_do_trang_thai}`, `run_id`. |
| `bo_nho.py` | Tuỳ chọn chung `--don-vi`. `tra --ngay`, lệnh mới `lich-su`. `ghi` thêm `--hieu-luc-den`, `--ngay-ban-hanh`, `--dieu-khoan`, `--sua-doi`, `--thay-the`, `--pham-vi-don-vi`, `--pham-vi-nam-tai-chinh`. |
| `quy_trinh.py` | Tuỳ chọn chung `--don-vi`. `chay` thêm `--xem-truoc`, `--chap-nhan-bo-cuc`, `--ban-sua-doi`, `--nguoi-lap`. JSON thêm `trang_thai_ket_qua`, `ly_do_trang_thai`, `run_id`, `sua_doi_cho`, `ngoai_le`, `bo_cuc_thay_doi[].muc_do`, `ket_qua[].bat_bien`. Trạng thái mới `xem_truoc`. |
| `ho_so_kiem_toan.py` | `danh-sach`, `xem`, `kiem`, `kiem-so-cai`, `phat-lai`, `duyet`, `xuat`, `kiem-goi` |
| `so_sanh_thau.py` | `--che-do so-bo|chinh-thuc`. `tom_tat.trang_thai`, `ly_do_trang_thai`. Mã 2 khi bản chính thức bị chặn. |

## 5. Ghi chú tương thích (đổi hành vi có chủ ý)

1. **`doc_hoa_don.py`**
   - Hóa đơn trùng (cùng MST người bán, ký hiệu, số) **không còn bị cộng hai lần** vào tổng.
   - Thông điệp chứa nhiều `<HDon>` giờ ra nhiều dòng, cột `tep` ghi `…#1`, `…#2`.
   - Một thẻ tiền lặp với giá trị khác nhau giờ bị để trống kèm cảnh báo, thay vì lấy thẻ đầu.
   - CSV/XLSX thêm 5 cột ở cuối.
   - Chuỗi mở đầu bằng `= + - @` được thêm `'` khi xuất.
   - Mã thoát mặc định vẫn là 0.
2. **`quy_trinh.py`**
   - Bố cục đổi ở cột quy trình dùng (mất cột, trùng tên, cột theo vị trí đổi tên) giờ là `can_hoi` (mã 2) và không ghi gì. Trước đây công cụ vẫn ghi rồi cảnh báo.
   - `tach` và `doi-chieu` không còn để lại file khi dừng hỏi.
   - Mỗi lần chạy ghi hồ sơ vào `<bộ nhớ>/ho-so/`; thư mục bộ nhớ đã nằm ngoài git.
   - Kết quả đã có người đồng ý thì không bị ghi đè; muốn sửa phải dùng `--ban-sua-doi`.
   - Quy trình `tach` lấy STT làm khoá giờ bị từ chối. Không quy trình thật nào bị ảnh hưởng.
   - `loc` với `cot_tien = "$F"` trước đây sập, giờ chạy được.
3. **`bo_nho.py`**
   - Bản lưu trữ có đuôi `-NNN`; bản cũ chỉ ghi ngày vẫn đọc được.
   - Nguồn không phải URL https bị từ chối.
   - Độ tin cậy `cao` mà không có nguồn .gov.vn bị hạ xuống `trung_binh`.
   - TTL của nhóm `tai-khoan` giảm từ 365 xuống 180 ngày.
4. **`so_sanh_thau.py`**
   - Mặc định không đổi, chỉ thêm `trang_thai: so_bo`.
   - Phiếu kỹ thuật có ô kết luận trống trước đây làm sập, giờ được coi là chưa chấm.
5. **Bộ nhớ theo đơn vị.** Không dùng `--don-vi` thì bố cục như cũ.

## 6. Gói kiểm toán mẫu và kết quả phát lại

[`examples/goi-kiem-toan-mau/`](examples/goi-kiem-toan-mau/) chứa:
- dữ liệu tổng hợp và quy trình lọc mẫu;
- gói xuất `run-*.json` và `run-*.md`;
- [`KET-QUA-KIEM-DOC-LAP.json`](examples/goi-kiem-toan-mau/KET-QUA-KIEM-DOC-LAP.json): `ho_so_khop: true`, `dau_vao_khop: true`.

Gói không chứa đường dẫn máy hay nội dung dòng dữ liệu (đã kiểm bằng grep, và test “gói kiểm toán” tự kiểm điều này). Phát lại (`phat-lai`) được kiểm trong `kiem_soat.py`:
- cùng nguồn và cùng quy tắc → `ket_qua_khop: true`;
- quy tắc bị sửa → `quy_tac_da_doi: true`, `ket_qua_khop: false`, mã 2, và sổ cái vẫn hợp lệ.

## 7. Rủi ro còn lại và việc cần phê duyệt bên ngoài

| Rủi ro | Cần ai |
|---|---|
| Không có xác thực danh tính người duyệt, nên `approved` không đạt được | Đơn vị chọn nhà cung cấp danh tính; lập trình cắm vào `danh_tinh_host()` |
| Không tra trạng thái hóa đơn với cơ quan thuế | Kênh tích hợp được cấp phép |
| Khoảng trống chế độ kế toán của DN siêu nhỏ có năm tài chính vắt qua 01/7/2026 | Người có chuyên môn kế toán/pháp lý, hoặc hướng dẫn của Bộ Tài chính |
| Hóa đơn trước 01/7/2026 xét theo NĐ 123/2020 (cách hiểu về hiệu lực theo thời gian) | Người có chuyên môn pháp lý ký xác nhận |
| TT 133, TT 91, NĐ 141 mới kiểm một phần; TT 103/2005, NĐ 174/2016, Luật 91/2025 chưa kiểm; NĐ 214/2025 cần kiểm lại trước 2026-10-28 | Người duy trì skill, với người có chuyên môn |
| Sổ cái chỉ chống sửa âm thầm, không phải bất biến | Sao lưu sổ cái và gửi mã băm dòng cuối ra ngoài, theo quy trình của đơn vị |
| Chưa có chính sách lưu trữ theo loại dữ liệu hay legal hold; chưa có CI Windows; chưa giới hạn khi đọc XLSX | Issue hoãn (mục “Hoãn” trong gap register) |

## 8. Hành động tiếp theo cho người duyệt

1. Đọc `LEGAL-CITATIONS.md` mục “Việc cần người có chuyên môn ký xác nhận”, rồi xác nhận hoặc sửa 5 điểm đó.
2. Review PR, đặc biệt các ghi chú tương thích ở mục 5. **Không tự merge.** Thay đổi này đụng ngữ nghĩa pháp lý và kiểm soát.
3. Sau khi merge, chạy `bash scripts/bootstrap.sh` để cài `signxml`. Lần chạy quy trình thật đầu tiên sẽ bắt đầu ghi hồ sơ vào `.ke-toan-vn/ho-so/`.
