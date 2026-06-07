import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

# Import instance app FastAPI từ file main.py
from main import app 
from app.models.schemas import AIProjectAnalysis, MetadataSummary, CategoryItem, AssetItem

# Khởi tạo client dùng để giả lập gửi request HTTP tới ứng dụng
client = TestClient(app)

# ==========================================
# BIẾN TOÀN CỤC: DỮ LIỆU MẪU ĐỂ TEST
# ==========================================
VALID_PAYLOAD = {
    "project_name": "Nhà máy Ajinomoto 3D",
    "raw_text": "Máy bơm P-101 nằm ở khu kỹ thuật. Camera an ninh ở hành lang."
}

def get_mock_ai_result():
    """Tạo một kết quả chuẩn từ AI để tái sử dụng trong các bài test."""
    return AIProjectAnalysis(
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

# ==========================================
# TEST CASE 1: HAPPY PATH (HOẠT ĐỘNG HOÀN HẢO TỪ A-Z)
# ==========================================
# Cần patch (chặn) cả 2 hàm: AI và DB để không gọi API thật
@patch("app.api.organize.save_ai_result_to_db")
@patch("app.api.organize.generate_structured_assets")
def test_organize_assets_success(mock_generate, mock_save):
    """Kiểm tra khi nhận đúng dữ liệu, API trả về HTTP 200 và cấu trúc chuẩn."""
    
    # 1. Thiết lập hành vi của các hàm bị patch
    mock_generate.return_value = get_mock_ai_result()
    mock_save.return_value = "d290f1ee-6c54-4b01-90e6-d701748f0851" # Giả lập 1 UUID từ Supabase

    # 2. Bắn Request POST tới Endpoint
    response = client.post("/api/v1/organize-assets", json=VALID_PAYLOAD)

    # 3. Khẳng định (Assert) kết quả
    assert response.status_code == 200
    data = response.json()
    
    # Kiểm tra cấu trúc JSON trả về có đúng như OrganizeResponse không
    assert data["status"] == "success"
    assert data["project_id"] == "d290f1ee-6c54-4b01-90e6-d701748f0851"
    assert data["data"]["metadata_summary"]["total_assets"] == 2
    assert len(data["data"]["categories"]) == 1
    
    # Xác nhận các hàm bên trong đã được hệ thống gọi tới với đúng tham số
    mock_generate.assert_called_once_with(
        project_name=VALID_PAYLOAD["project_name"], 
        raw_text=VALID_PAYLOAD["raw_text"]
    )
    mock_save.assert_called_once()

# ==========================================
# TEST CASE 2: LỖI NGƯỜI DÙNG NHẬP VĂN BẢN RỖNG HOẶC KHOẢNG TRẮNG
# ==========================================
def test_organize_assets_empty_input():
    """Kiểm tra chức năng Validate bắt buộc của bài test: Chặn rỗng."""
    
    invalid_payload = {
        "project_name": "   ",  # Cố tình truyền toàn khoảng trắng
        "raw_text": ""          # Cố tình truyền rỗng
    }

    # Bắn Request
    response = client.post("/api/v1/organize-assets", json=invalid_payload)

    # Pydantic hoặc Validation thủ công của bạn sẽ ném ra mã 422
    assert response.status_code == 422
    data = response.json()
    
    # Kiểm tra xem có chứa thông điệp lỗi cụ thể không
    assert "detail" in data

# ==========================================
# TEST CASE 3: LỖI DỊCH VỤ AI (API AI FAIL)
# ==========================================
@patch("app.api.organize.generate_structured_assets")
def test_organize_assets_ai_failure(mock_generate):
    """Kiểm tra chức năng bắt lỗi khi Gemini API quá tải hoặc sập mạng."""
    
    # Giả lập hàm gọi AI bị văng lỗi (Exception)
    mock_generate.side_effect = Exception("Google GenAI Rate Limit Exceeded")

    # Bắn Request
    response = client.post("/api/v1/organize-assets", json=VALID_PAYLOAD)

    # API của bạn phải bình tĩnh bắt lỗi và trả về HTTP 503 (Service Unavailable)
    assert response.status_code == 503
    data = response.json()
    
    # Đảm bảo frontend sẽ nhận được câu báo lỗi tử tế bằng tiếng Việt
    assert "Dịch vụ AI đang gặp gián đoạn" in data["detail"]

# ==========================================
# TEST CASE 4: LỖI LƯU DATABASE (LỖI SUPABASE)
# ==========================================
@patch("app.api.organize.save_ai_result_to_db")
@patch("app.api.organize.generate_structured_assets")
def test_organize_assets_db_failure(mock_generate, mock_save):
    """Kiểm tra kịch bản AI phân loại xong nhưng rớt mạng lúc lưu vào DB."""
    
    # AI thì chạy thành công, nhưng hàm lưu DB thì bị lỗi
    mock_generate.return_value = get_mock_ai_result()
    mock_save.side_effect = Exception("Supabase Connection Refused")

    # Bắn Request
    response = client.post("/api/v1/organize-assets", json=VALID_PAYLOAD)

    # Lỗi từ phía máy chủ khi xử lý database phải là HTTP 500
    assert response.status_code == 500
    data = response.json()
    assert "Lỗi lưu trữ dữ liệu" in data["detail"]  