from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# ==========================================
# PHẦN 1: SCHEMA DÀNH CHO TRÍ TUỆ NHÂN TẠO (GEMINI)
# Ép buộc Gemini API phải trả về chính xác cấu trúc này
# ==========================================

class AssetItem(BaseModel):
    original_name: str = Field(description="Tên gốc của tài sản hoặc điểm chạm từ dữ liệu thô")
    slug: str = Field(description="Chuỗi định danh chuẩn SEO, viết thường, không dấu, nối bằng dấu gạch ngang")
    description: Optional[str] = Field(None, description="Mô tả ngắn gọn về chức năng của tài sản này (nếu suy luận được)")

class CategoryItem(BaseModel):
    category_name: str = Field(description="Tên nhóm khu vực phân loại hợp lý (ví dụ: Khu kỹ thuật, Hành lang)")
    slug: str = Field(description="Chuỗi định danh chuẩn SEO của nhóm")
    assets: List[AssetItem] = Field(description="Danh sách các tài sản thuộc nhóm này")

class MetadataSummary(BaseModel):
    total_assets: int = Field(description="Tổng số lượng tài sản được tìm thấy")
    total_categories: int = Field(description="Tổng số lượng danh mục được phân loại")
    insights: Optional[str] = Field(None, description="Đánh giá ngắn gọn về cấu trúc không gian của dự án")

class AIProjectAnalysis(BaseModel):
    """
    Đây là Master Schema truyền vào response_schema của Gemini.
    Nó bao gồm cả dữ liệu tài sản để lưu vào bảng 'categories', 'assets' 
    và các đánh giá để lưu vào bảng 'projects'.
    """
    metadata_summary: MetadataSummary
    ai_suggestions: List[str] = Field(description="Đề xuất 2-3 cách cải thiện tổ chức hoặc đặt tên tài sản")
    categories: List[CategoryItem]


# ==========================================
# PHẦN 2: SCHEMA DÀNH CHO FASTAPI (API REQUEST/RESPONSE)
# Giao tiếp giữa Frontend (React) và Backend
# ==========================================

class OrganizeRequest(BaseModel):
    """Định dạng dữ liệu Frontend gửi lên Backend"""
    project_name: str = Field(..., min_length=1, description="Tên dự án số hóa")
    raw_text: str = Field(..., min_length=10, description="Danh sách tài sản 3D thô cần phân loại")

class OrganizeResponse(BaseModel):
    """Định dạng dữ liệu Backend trả về cho Frontend hiển thị"""
    project_id: str = Field(description="UUID của project lưu trong Supabase")
    status: str = Field(default="success")
    data: AIProjectAnalysis