import os
from google import genai
from app.models.schemas import AIProjectAnalysis


def _create_client():
    """Factory function — lazy-init client để tránh lỗi khi thiếu API key lúc import."""
    return genai.Client()


def generate_structured_assets(project_name: str, raw_text: str) -> AIProjectAnalysis:
    """
    Hàm gửi dữ liệu thô tới Gemini 2.5 Flash Lite và ép kiểu trả về JSON chuẩn xác.
    """

    client = _create_client()
    prompt = f"""
    Bạn là Kỹ sư Dữ liệu 3D cấp cao tại Star Global 3D.
    Nhiệm vụ của bạn là phân tích dữ liệu khảo sát của dự án số hóa bản sao số (Digital Twin) sau:
    Tên dự án: {project_name}
    
    Dữ liệu thô cần phân loại:
    {raw_text}
    
    Yêu cầu thực thi:
    1. Gom nhóm các thiết bị, tài sản, điểm chạm (touchpoints) vào các danh mục khu vực logic.
    2. Tạo chuỗi định danh (slug) chuẩn SEO cho tất cả các danh mục và tài sản.
    3. Tự động sinh mô tả (description) ngắn gọn cho tài sản dựa trên đặc tính vật lý/kỹ thuật.
    4. Tóm tắt metadata (tổng số lượng) và đưa ra 2-3 đề xuất cải thiện cách quản lý thư mục.
    
    Tuyệt đối tuân thủ cấu trúc dữ liệu JSON đã được định nghĩa.
    """

    try:
        # 2. Gọi API với tính năng Structured Outputs
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                # ĐÂY LÀ ĐIỂM ĂN TIỀN: Ép Gemini tuân thủ tuyệt đối Pydantic Schema
                "response_schema": AIProjectAnalysis,
            },
        )
        
        # 3. Trả về dữ liệu đã được parse sẵn thành Python Object (Không cần dùng json.loads)
        return response.parsed
        
    except Exception as e:
        # Ghi log lỗi tại đây để debug (sẽ tự động được Arize Phoenix bắt lại)
        print(f"Lỗi khi gọi Gemini API: {str(e)}")
        raise e