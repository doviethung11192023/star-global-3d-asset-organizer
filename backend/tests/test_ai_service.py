import pytest
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

from app.services.ai_service import generate_structured_assets
from app.models.schemas import AIProjectAnalysis, MetadataSummary, CategoryItem, AssetItem

# ==========================================
# TEST CASE 1: HAPPY PATH (AI TRẢ VỀ DỮ LIỆU CHUẨN XÁC)
# ==========================================
@patch("app.services.ai_service._create_client")
def test_generate_structured_assets_success(mock_create_client):
    """
    Kiểm tra luồng thành công: Hàm phải trả về đúng object AIProjectAnalysis
    khi Gemini API phản hồi hợp lệ.
    """
    # 1. Chuẩn bị dữ liệu giả lập (Mock Data) mà Gemini sẽ trả về
    mock_parsed_data = AIProjectAnalysis(
        metadata_summary=MetadataSummary(total_assets=2, total_categories=1, insights="Dự án tốt"),
        ai_suggestions=["Cải thiện cách đặt tên tài sản", "Tối ưu hóa cấu trúc danh mục"],
        categories=[
            CategoryItem(
                category_name="Khu kỹ thuật",
                slug="khu-ky-thuat",
                assets=[
                    AssetItem(original_name="Bơm P-101", slug="bom-p-101", description="Bơm nước chính"),
                    AssetItem(original_name="Tủ điện A1", slug="tu-dien-a1", description="Tủ điện khu kỹ thuật")
                ]
            )
        ]
    )

    # 2. Thiết lập mock client chain: _create_client() -> client.models.generate_content()
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.parsed = mock_parsed_data
    mock_client.models.generate_content.return_value = mock_response
    mock_create_client.return_value = mock_client

    # 3. Gọi hàm cần test (Lúc này nó sẽ không gọi API thật mà dùng dữ liệu Mock ở trên)
    result = generate_structured_assets(
        project_name="Trạm Bơm 3D",
        raw_text="Bơm P-101, Tủ điện A1 ở khu kỹ thuật"
    )

    # 4. Xác nhận kết quả (Assertions)
    assert isinstance(result, AIProjectAnalysis)
    assert result.metadata_summary.total_assets == 2
    assert len(result.categories) == 1
    assert result.categories[0].category_name == "Khu kỹ thuật"
    assert result.categories[0].assets[0].slug == "bom-p-101"

    # Kiểm tra xem API có được gọi đúng tham số không
    mock_client.models.generate_content.assert_called_once()
    args, kwargs = mock_client.models.generate_content.call_args
    assert kwargs["model"] == "gemini-2.5-flash-lite"
    assert kwargs["config"]["response_schema"] == AIProjectAnalysis


# ==========================================
# TEST CASE 2: LUỒNG LỖI API (API THẤT BẠI HOẶC QUÁ TẢI)
# ==========================================
@patch("app.services.ai_service._create_client")
def test_generate_structured_assets_api_failure(mock_create_client):
    """
    Kiểm tra luồng ngoại lệ: Hệ thống phải bắt được lỗi khi Google API bị sập
    hoặc hết hạn mức (Quota Exceeded).
    """
    # 1. Giả lập Google API ném ra lỗi
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("Google API Quota Exceeded or Timeout")
    mock_create_client.return_value = mock_client

    # 2. Gọi hàm và mong đợi nó ném ra lỗi (Raise Exception)
    with pytest.raises(Exception) as exc_info:
        generate_structured_assets("Dự án lỗi", "Văn bản rác...")

    # 3. Xác nhận lỗi chứa thông điệp chính xác
    assert "Google API Quota Exceeded" in str(exc_info.value)


# ==========================================
# TEST CASE 3: LUỒNG KIỂM ĐỊNH LỖI (PYDANTIC BẮT LỖI)
# ==========================================
def test_pydantic_schema_validation_error():
    """
    Kiểm tra độc lập "tấm khiên" Pydantic: Đảm bảo nếu AI có lỡ trả về dữ liệu
    bị thiếu trường bắt buộc (ví dụ: thiếu slug), Pydantic sẽ chặn lại ngay.
    """
    # Cố tình truyền thiếu trường 'slug' trong AssetItem
    invalid_asset_data = {
        "original_name": "Bơm P-101",
        # "slug": "bom-p-101",  <-- Cố tình bỏ quên
        "description": "Bơm nước chính"
    }

    # Mong đợi Pydantic ném ra lỗi ValidationError
    with pytest.raises(ValidationError) as exc_info:
        AssetItem(**invalid_asset_data)
    
    # Xác nhận lỗi là do thiếu trường 'slug'
    assert "slug" in str(exc_info.value)
    assert "Field required" in str(exc_info.value)