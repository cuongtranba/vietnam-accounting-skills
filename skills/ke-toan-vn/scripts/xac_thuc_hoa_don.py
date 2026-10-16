"""Xác thực hóa đơn điện tử — tách hẳn khỏi việc ĐỌC hóa đơn.

Đọc được XML (`ET.parse` chạy qua) không có nghĩa hóa đơn là thật. Ba câu hỏi khác nhau, ba
trạng thái riêng, không bao giờ gộp làm một chữ "hợp lệ":

  xml_schema      pass | fail | unsupported | not_checked
                  fail = XML hỏng/không đọc được; pass chỉ khi có XSD do người dùng cung cấp
                  (--xsd) và file khớp. Công cụ không kèm XSD chính thức nên mặc định not_checked.
  chu_ky          valid | invalid | absent | not_applicable | not_checked
                  valid   = chữ ký XMLDSig toàn vẹn VÀ chứng thư chuỗi về CA tin cậy người dùng
                            cung cấp (--ca-tin-cay). Không có CA thì tối đa là not_checked, kèm
                            toan_ven_chu_ky = valid để biết dữ liệu chưa bị sửa sau khi ký.
                  invalid = đã kiểm và hỏng (sai digest/chữ ký, chứng thư không khớp, không
                            chuỗi về CA đã cho, thẻ Signature không theo chuẩn).
                  absent  = không có chữ ký số người bán. NĐ 254/2026 (Phụ lục, mục 6) yêu cầu
                            chữ ký số người bán nhưng có ngoại lệ (vd hóa đơn khởi tạo từ máy tính
                            tiền — khoản 9 Điều 8) — nên đây là việc cần người xem, không tự loại.
  trang_thai_cqt  confirmed | replaced | adjusted | cancelled_or_invalid | unknown | not_checked
                  Tình trạng hóa đơn trên hệ thống của cơ quan thuế. Chỉ tra được qua kênh
                  được cấp phép; công cụ này KHÔNG có kênh đó, nên luôn là not_checked. Không
                  suy ra từ nội dung file, không tra qua trang không chính thức.

Thời điểm đánh giá chứng thư là lúc chạy, không phải lúc ký — chứng thư đã hết hạn sau ngày ký
sẽ bị coi là không tin cậy. Ghi rõ trong ly_do để người duyệt biết.
"""

from __future__ import annotations

import base64
import copy

DSIG = "http://www.w3.org/2000/09/xmldsig#"


def _ten(pt) -> str:
    return pt.tag.rsplit("}", 1)[-1] if isinstance(pt.tag, str) else ""


def co_thu_vien() -> bool:
    try:
        import lxml  # noqa: F401
        import signxml  # noqa: F401
    except ImportError:
        return False
    return True


def _cac_hoa_don(goc):
    ds = [pt for pt in goc.iter() if _ten(pt) == "HDon"]
    return ds or [goc]


def _pem(the_cert) -> bytes:
    der = base64.b64decode("".join((the_cert.text or "").split()))
    return (b"-----BEGIN CERTIFICATE-----\n" + base64.encodebytes(der)
            + b"-----END CERTIFICATE-----\n")


def kiem_chu_ky(du_lieu: bytes, chi_so: int, ca_pem: str | None = None) -> dict:
    """Kiểm chữ ký người bán của hóa đơn thứ `chi_so` trong file."""
    if not co_thu_vien():
        # Không có thư viện thì không biết gì về chữ ký — nhưng vẫn phân biệt có/không có thẻ.
        import xml.etree.ElementTree as ET

        hd = _cac_hoa_don(ET.fromstring(du_lieu))[chi_so]
        co = any(_ten(pt) == "Signature" for pt in hd.iter())
        return {"chu_ky": "not_checked" if co else "absent",
                "ly_do": "Chưa cài signxml — chưa kiểm chữ ký" if co else
                "Không có thẻ chữ ký số trong hóa đơn"}

    from lxml import etree
    from signxml import SignatureConfiguration, XMLVerifier
    from signxml.exceptions import InvalidCertificate, InvalidInput, InvalidSignature

    bo_doc = etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=False)
    goc = etree.fromstring(du_lieu, parser=bo_doc)
    hd = _cac_hoa_don(goc)[chi_so]
    cac_chu_ky = [pt for pt in hd.iter() if _ten(pt) == "Signature"]
    if not cac_chu_ky:
        return {"chu_ky": "absent", "ly_do": "Không có thẻ chữ ký số trong hóa đơn"}
    ban = next((s for s in cac_chu_ky if _ten(s.getparent()) in ("NBan", "NBanHang")),
               cac_chu_ky[0])
    if ban.tag != f"{{{DSIG}}}Signature":
        return {"chu_ky": "invalid", "ly_do": "Thẻ Signature không theo chuẩn XMLDSig"}
    the_cert = ban.find(f".//{{{DSIG}}}X509Certificate")
    if the_cert is None or not (the_cert.text or "").strip():
        return {"chu_ky": "not_checked", "ly_do": "Chữ ký không kèm chứng thư số (X509Certificate)"}
    tham_chieu = [r.get("URI") for r in ban.findall(f"./{{{DSIG}}}SignedInfo/{{{DSIG}}}Reference")]
    dl = next((pt for pt in hd.iter() if _ten(pt) == "DLHDon"), None)
    if dl is None or f"#{dl.get('Id')}" not in tham_chieu:
        return {"chu_ky": "invalid",
                "ly_do": "Chữ ký người bán không phủ phần dữ liệu hóa đơn (DLHDon)"}

    # Kiểm đúng MỘT chữ ký: bỏ các chữ ký khác (người mua, cơ quan thuế) khỏi bản sao, giữ
    # nguyên phần còn lại của tài liệu để chuẩn hoá (c14n) không đổi.
    vi_tri = [pt for pt in goc.iter() if _ten(pt) == "Signature"].index(ban)
    ban_sao = copy.deepcopy(goc)
    for i, s in enumerate([pt for pt in ban_sao.iter() if _ten(pt) == "Signature"]):
        if i != vi_tri:
            s.getparent().remove(s)

    cau_hinh = SignatureConfiguration(expect_references=len(tham_chieu))
    try:
        pem = _pem(the_cert)
        XMLVerifier().verify(ban_sao, x509_cert=pem, expect_config=cau_hinh)
    except InvalidInput as e:
        return {"chu_ky": "not_checked",
                "ly_do": f"Không kiểm được (thuật toán/cấu trúc không được chấp nhận): {e}"}
    except InvalidSignature as e:
        return {"chu_ky": "invalid", "toan_ven_chu_ky": "invalid",
                "ly_do": f"Dữ liệu hoặc chữ ký không khớp: {type(e).__name__}: {e}"[:300]}
    except Exception as e:  # chứng thư hỏng, base64 sai...
        return {"chu_ky": "invalid", "ly_do": f"Chữ ký không đọc được: {type(e).__name__}"}

    if not ca_pem:
        return {"chu_ky": "not_checked", "toan_ven_chu_ky": "valid",
                "ly_do": "Toàn vẹn: dữ liệu chưa bị sửa sau khi ký. CHƯA kiểm chuỗi tin cậy của "
                         "chứng thư (cần --ca-tin-cay) — chưa được coi là chữ ký hợp lệ."}
    try:
        XMLVerifier().verify(ban_sao, ca_pem_file=ca_pem, expect_config=cau_hinh)
    except InvalidCertificate as e:
        return {"chu_ky": "invalid", "toan_ven_chu_ky": "valid",
                "ly_do": f"Chứng thư không chuỗi về CA tin cậy đã cung cấp: {e}"[:300]}
    except (InvalidInput, InvalidSignature) as e:
        return {"chu_ky": "invalid", "toan_ven_chu_ky": "valid", "ly_do": str(e)[:300]}
    return {"chu_ky": "valid", "toan_ven_chu_ky": "valid",
            "ly_do": "Toàn vẹn và chuỗi về CA đã cung cấp (đánh giá chứng thư tại thời điểm chạy)."}


def kiem_xsd(du_lieu: bytes, xsd: str | None) -> str:
    if not xsd:
        return "not_checked"
    from lxml import etree

    bo_doc = etree.XMLParser(resolve_entities=False, no_network=True)
    luoc_do = etree.XMLSchema(etree.parse(xsd, parser=bo_doc))
    return "pass" if luoc_do.validate(etree.fromstring(du_lieu, parser=bo_doc)) else "fail"
