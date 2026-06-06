from fastapi import APIRouter, HTTPException, status
from app.models.schemas import OrganizeRequest, OrganizeResponse
from app.services.ai_service import generate_structured_assets
from app.services.db_service import save_ai_result_to_db

router = APIRouter()

@router.post("/organize-assets", response_model=OrganizeResponse)
async def organize_assets(request: OrganizeRequest):
    """
    Endpoint tiếp nhận yêu cầu phân loại tài sản 3D từ Frontend.
    """
    
    # ==========================================
    # CHỐT CHẶN 1: Validate input rỗng
    # ==========================================
    if not request.project_name.strip() or not request.raw_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Tên dự án và danh sách tài sản thô không được để trống."
        )

    # ==========================================
    # CHỐT CHẶN 2: Xử lý AI & Bắt lỗi API Fail
    # ==========================================
    try:
        # Gọi Gemini để bóc tách ngữ nghĩa
        ai_result = generate_structured_assets(
            project_name=request.project_name,
            raw_text=request.raw_text
        )
    except Exception as e:
        print(f"[AI Error]: {str(e)}") # Ghi log cho Backend Developer đọc
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dịch vụ AI đang gặp gián đoạn (Hết token hoặc Timeout). Vui lòng thử lại sau."
        )

    # ==========================================
    # CHỐT CHẶN 3: Lưu Database an toàn
    # ==========================================
    try:
        project_id = save_ai_result_to_db(
            project_name=request.project_name,
            raw_text=request.raw_text,
            ai_data=ai_result
        )
    except Exception as e:
        print(f": {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi lưu trữ dữ liệu. Phân tích AI thành công nhưng không thể lưu vào Database."
        )

    # ==========================================
    # THÀNH CÔNG: Trả kết quả về Frontend
    # ==========================================
    return OrganizeResponse(
        project_id=project_id,
        status="success",
        data=ai_result
    )