from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import organize

# Khởi tạo FastAPI
app = FastAPI(
    title="Star Global 3D - AI Asset Organizer",
    description="API hệ thống bóc tách và phân loại tài sản 3D tự động bằng Gemini 2.0",
    version="1.0.0"
)

# Cấu hình CORS để ReactJS (chạy ở cổng khác) có thể gọi API này
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Trong thực tế sẽ đổi thành URL Frontend của bạn
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký Endpoint API
app.include_router(organize.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "AI Asset Organizer API is running!"}