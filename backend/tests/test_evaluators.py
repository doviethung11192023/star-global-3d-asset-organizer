import re
import pytest
from phoenix.evals import create_evaluator

# ==========================================
# KHỞI TẠO CODE EVALUATOR BẰNG REGEX
# ==========================================
@create_evaluator(name="strict-slug-format", kind="code", direction="maximize")
def evaluate_slug_format(output_slug: str) -> bool:
    """
    Hàm kiểm tra định dạng Slug.
    Yêu cầu chuẩn SEO: Chỉ chứa chữ cái viết thường, số, không khoảng trắng, nối nhau bằng dấu gạch ngang.
    """
    pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
    # Trả về True (điểm 1) nếu khớp, False (điểm 0) nếu sai
    return bool(re.match(pattern, output_slug))


# ==========================================
# PYTEST ĐỂ CHẠY KIỂM THỬ HÀM EVALUATOR NÀY
# ==========================================
def test_evaluate_slug_format_valid():
    """Kiểm tra trường hợp AI sinh slug chuẩn xác."""
    # Khi gọi evaluate_slug_format, Phoenix trả về đối tượng Score
    # Thuộc tính.score sẽ mang giá trị 1.0 (Nghĩa là Pass)
    result = evaluate_slug_format("khu-vuc-ky-thuat-01")
    print(result)
    print(type(result))
    assert result is True

def test_evaluate_slug_format_invalid_spaces():
    """Kiểm tra trường hợp AI sinh lỗi (chứa khoảng trắng hoặc viết hoa)."""
    result = evaluate_slug_format("Khu Vuc Ky Thuat")
    print(result)
    print(type(result))
    assert result is False

def test_evaluate_slug_format_invalid_special_chars():
    """Kiểm tra trường hợp AI sinh lỗi (chứa ký tự đặc biệt)."""
    result = evaluate_slug_format("may-bom_#101")
    print(result)
    print(type(result))
    assert result is False