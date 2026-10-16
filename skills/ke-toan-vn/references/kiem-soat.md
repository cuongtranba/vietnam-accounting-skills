# Kiểm soát: trạng thái kết quả, hồ sơ lần chạy, ghi nhận duyệt, đơn vị

Đọc file này khi:
- người dùng hỏi "số này lấy từ đâu", "ai đã duyệt", "chứng minh được không";
- cần đưa một kết quả vào hồ sơ;
- cần làm việc cho nhiều đơn vị trên cùng một máy.

Công cụ chia rõ ba việc:
- **máy** đọc và tính;
- **công cụ** kiểm soát và ghi lại bằng chứng;
- **người có trách nhiệm** quyết định.

Máy và công cụ không được nói thay phần của người.

## Không nói quá điều đã kiểm

Mọi trạng thái đều nói đúng điều đã kiểm được, không hơn:

| Câu hỏi | Trạng thái | Không bao giờ |
|---|---|---|
| File XML có đúng cấu trúc không? | `xml_schema`: `pass` (chỉ khi người dùng đưa XSD qua `--xsd`) · `fail` (hỏng) · `unsupported` (PDF) · `not_checked` | Coi "đọc được" là "hợp lệ" |
| Chữ ký số người bán có hợp lệ không? | `chu_ky`: `valid` (toàn vẹn **và** chuỗi về CA do người dùng đưa qua `--ca-tin-cay`) · `invalid` · `absent` · `not_checked`. Kèm `toan_ven_chu_ky` để biết dữ liệu có bị sửa sau khi ký hay không. | Nói `valid` khi chưa kiểm chuỗi tin cậy |
| Hóa đơn còn hiệu lực trên hệ thống của cơ quan thuế? | `trang_thai_cqt`: luôn `not_checked`. Công cụ không có kênh tra cứu được cấp phép. | Suy từ nội dung file, hoặc tra qua trang không chính thức |
| Lô số liệu dùng được chưa? | `draft` (đủ điều kiện để người có trách nhiệm xem) · `needs_review` (thiếu số, trùng, lệch, ngoại lệ...) | Tự ghi "đã duyệt" |
| Ai đã duyệt? | `UNVERIFIED_HUMAN_REVIEW` (danh tính tự khai) · trạng thái duyệt tối đa `da_xem_chua_xac_thuc` | Ghi `approved` khi chưa có danh tính được xác thực |

Báo kết quả cho người dùng theo đúng các chữ này. Ví dụ: "chữ ký toàn vẹn nhưng chưa kiểm chuỗi tin cậy", không viết "chữ ký hợp lệ".

**Tổng quan sát và tổng đã kiểm.** `tong_tien_hang` là tổng quan sát: nó chỉ cộng các số đọc được, và hóa đơn trùng chỉ cộng một lần. `tong_da_kiem` chỉ có khi mọi hóa đơn đều đủ dữ liệu. Thiếu một số thì nói rõ là tổng **chưa đủ**, đừng báo tổng như số cuối.

## Hồ sơ lần chạy

`quy_trinh.py chay` luôn ghi hồ sơ; `doc_hoa_don.py --ghi-ho-so` ghi khi được yêu cầu. Hồ sơ nằm ở `<bộ nhớ đơn vị>/ho-so/<run_id>.json` và gồm:
- SHA-256 đầy đủ của từng file nguồn, của quy trình, của danh mục đã áp và của từng file kết quả;
- số dòng, tổng tiền, bất biến và ngoại lệ;
- người lập (tự khai) và giờ có múi giờ;
- `ket_qua_sha256`: mã băm của kết quả nghiệp vụ, không gồm thời gian và đường dẫn. Cùng nguồn và cùng quy tắc thì cùng mã.

Hồ sơ **không** chứa nội dung dòng dữ liệu (tên bệnh nhân, tên dịch vụ...).

Sổ cái `ho-so/so-cai.jsonl` chỉ nối thêm. Mỗi dòng mang mã băm của dòng trước, nên sửa, xoá hay chèn đều làm đứt chuỗi. Đây là **chống sửa âm thầm**, không phải bất biến: ai có quyền ghi thư mục vẫn xoá được cả sổ. Muốn chắc hơn thì sao lưu sổ cái ra nơi khác, hoặc gửi mã băm dòng cuối (`kiem-so-cai`) cho người duyệt qua kênh riêng.

```bash
ho_so_kiem_toan.py danh-sach
ho_so_kiem_toan.py kiem <run_id>         # nguồn/quy tắc/kết quả còn đúng mã băm?
ho_so_kiem_toan.py phat-lai <run_id>     # chạy lại ở chế độ xem trước, so kết quả nghiệp vụ
ho_so_kiem_toan.py xuat <run_id> --ra goi/      # gói JSON + Markdown để nộp hồ sơ
ho_so_kiem_toan.py kiem-goi goi/<run_id>.json --thu-muc-tep <thư mục file nguồn>
```

Gói xuất ra bỏ mọi đường dẫn trên máy và có câu miễn trừ: gói **không** phải chứng nhận hay ý kiến kiểm toán. Nếu không được phép chuyển file nguồn thì đừng gửi kèm. Người nhận chỉ cần mã băm trong gói để đối chiếu với bản họ đang giữ.

## Ghi nhận duyệt

```bash
ho_so_kiem_toan.py duyet <run_id> --vai-tro nguoi-kiem-tra|nguoi-phe-duyet \
    --quyet-dinh dong-y|tu-choi --nguoi "Họ tên" [--ghi-chu ...] [--ngoai-le "lý do"]
```

- Lần duyệt gắn với mã băm hồ sơ. Nguồn, quy tắc hay kết quả đổi sau đó thì lần duyệt `vo_hieu`.
- Lần chạy `needs_review` chỉ ghi nhận "đồng ý" khi có `--ngoai-le` nêu lý do chấp nhận.
- Bật `[phan_quyen] tach_nhiem = true` trong `<bộ nhớ đơn vị>/don-vi.toml` thì người lập không tự duyệt được, và một người không giữ hai vai.
- Công cụ không có cơ chế xác thực danh tính. Biến môi trường, tài khoản máy hay tham số dòng lệnh đều **không** phải xác thực. Vì vậy trạng thái tối đa là `da_xem_chua_xac_thuc`, và đó là cố ý.

## Kết quả đã duyệt thì không ghi đè

Trước khi duyệt, sửa lại là ghi đè đúng file cũ, không đẻ `_v2`.

Sau khi có người đồng ý, `quy_trinh.py` từ chối ghi đè file kết quả đó. Muốn sửa thì chạy lại với `--ban-sua-doi`: bản mới ghi thành `-SUA1`, `-SUA2`..., và hồ sơ của nó có `sua_doi_cho` trỏ về lần chạy đã duyệt.

## Nhiều đơn vị trên một máy

Truyền `--don-vi <mã>` (hoặc đặt `KE_TOAN_VN_DON_VI`). Quy trình, danh mục, quy ước và hồ sơ của đơn vị đó nằm ở `<bộ nhớ>/don-vi/<mã>/`, và không đơn vị nào thấy của đơn vị khác. Ghi chú pháp lý thì dùng chung.

Mã đơn vị chỉ gồm `a-z`, `0-9` và `-`. Không có mã thì dùng thẳng `<bộ nhớ>/`, như trước.

Có thể khai hồ sơ đơn vị trong `don-vi.toml`:

```toml
ma_phap_nhan = "pn-01"          # ghi vào hồ sơ lần chạy
[phan_quyen]
tach_nhiem = true
```

## Bất biến kế toán

So khớp với file mẫu chỉ chứng minh "giống lần trước". Nếu lần trước sai thì bài kiểm vẫn đạt. Vì vậy các động cơ tự kiểm thêm:

- **`loc`:**
  - dòng gốc = giữ + loại, và tổng tiền gốc = giữ + loại (cả dòng âm);
  - đọc lại chính file vừa ghi (file tạm, trước khi công bố), phải khớp đúng các số đó.
- **`tach`:** tổng nguồn = các nhóm + phần ngoài nhóm.
- **Dòng tổng lẫn trong dữ liệu:** dòng mang nhãn đúng là "Tổng cộng", "Cộng"..., hoặc ô tiền là `SUM`/`SUBTOTAL` trên nhiều dòng, sẽ bị cộng trùng. Công cụ liệt kê số dòng và để lần chạy ở `needs_review`. "Tổng phân tích tế bào máu" là tên dịch vụ, không phải nhãn tổng.
- **Khoá:** cột STT không được làm khoá tách (STT đánh lại mỗi kỳ). Khi đối chiếu dùng khoá STT thì có cảnh báo.

Hỏng bảo toàn là lỗi của công cụ: dừng và không công bố file nào.

## Lưu trữ và dữ liệu cá nhân

- **Không tự xoá.** Công cụ không xoá hồ sơ hay kết quả nào. Bảng kê, bảng tổng hợp chi tiết dùng
  để ghi sổ là tài liệu kế toán lưu **tối thiểu 10 năm** (khoản 1 Điều 13 NĐ 174/2016); giữ hồ sơ
  kiểm toán của nó cùng thời hạn. Dọn dẹp là quyết định của đơn vị, theo danh mục lưu trữ của họ.
- **Hồ sơ không chứa dữ liệu dòng** — chỉ mã băm, số dòng, tổng tiền, tên file. Tên file có tên
  người (vd "LUONG - NGUYEN VAN A.xlsx") thì nhãn trong hồ sơ cũng có — đặt tên file theo mã.
- **Xử lý tại chỗ, đưa ra ngoài phần tối thiểu.** Dữ liệu sức khỏe là dữ liệu nhạy cảm (NĐ
  356/2025). Khi trợ lý AI chạy trên nền tảng ở nước ngoài, mọi nội dung đưa vào cuộc trò chuyện có
  thể là chuyển dữ liệu xuyên biên giới (Điều 20 Luật 91/2025): chỉ đưa số tổng hợp hoặc dữ liệu đã
  khử nhận dạng; việc lập hồ sơ đánh giá tác động là trách nhiệm của đơn vị (bên kiểm soát dữ liệu).
