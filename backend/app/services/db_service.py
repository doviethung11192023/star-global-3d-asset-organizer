import os
from supabase import create_client, Client
from app.models.schemas import AIProjectAnalysis
from app.core.database import get_supabase

# Lấy client từ core
supabase = get_supabase()

def save_ai_result_to_db(project_name: str, raw_text: str, ai_data: AIProjectAnalysis) -> str:
    """
    Hàm lưu trữ dữ liệu vào 3 bảng: projects, categories, và assets
    """
    # 1. Lưu dự án mới vào bảng `projects` (Kèm theo đánh giá của AI)
    project_response = supabase.table("projects").insert({
        "name": project_name,
        "raw_input": raw_text,
        "metadata_summary": ai_data.metadata_summary.model_dump(), # Ép Pydantic về dict
        "ai_suggestions": ai_data.ai_suggestions
    }).execute()
    
    project_id = project_response.data[0]["id"]

    # 2. Lưu từng Danh mục và Tài sản tương ứng
    for category in ai_data.categories:
        # Thêm Category
        cat_response = supabase.table("categories").insert({
            "project_id": project_id,
            "name": category.category_name,
            "slug": category.slug
        }).execute()
        
        category_id = cat_response.data[0]["id"]
        
        # Tạo danh sách tài sản (Assets) để insert hàng loạt (Bulk Insert)
        assets_to_insert = [
            {
                "category_id": category_id,
                "original_name": asset.original_name,
                "slug": asset.slug,
                "description": asset.description
            }
            for asset in category.assets
        ]
        
        # Thêm Assets vào database
        if assets_to_insert:
            supabase.table("assets").insert(assets_to_insert).execute()

    return project_id