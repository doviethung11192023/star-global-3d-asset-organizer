import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import organize

# --- KHỞI TẠO ARIZE PHOENIX (FAIL GRACEFULLY) ---
_PHOENIX_ENABLED = False
try:
    from phoenix.otel import register
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor

    register(
        project_name=os.getenv("PHOENIX_PROJECT_NAME", "star-global-3d-asset-organizer"),
        endpoint=os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces")
    )
    _PHOENIX_ENABLED = True
    print("[Phoenix] OpenTelemetry tracing đã được khởi tạo.")
except Exception as e:
    print(f"[Phoenix] Không thể kết nối Phoenix collector: {e}")
    print("[Phoenix] App vẫn chạy bình thường (không tracing).")

# Khởi tạo FastAPI
app = FastAPI(
    title="Star Global 3D - AI Asset Organizer",
    description="API hệ thống bóc tách và phân loại tài sản 3D tự động bằng Gemini 2.0",
    version="1.0.0"
)

# Kích hoạt Instrumentor (chỉ khi Phoenix đã kết nối thành công)
if _PHOENIX_ENABLED:
    try:
        FastAPIInstrumentor().instrument_app(app)
        GoogleGenAIInstrumentor().instrument()
        print("[Phoenix] Đã instrument FastAPI và Google GenAI.")
    except Exception as e:
        print(f"[Phoenix] Lỗi instrument: {e}")

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
@app.middleware("http")
async def debug_requests(request, call_next):
    print(
        f"METHOD={request.method} "
        f"PATH={request.url.path}"
    )

    response = await call_next(request)

    print(
        f"STATUS={response.status_code}"
    )

    return response
@app.get("/")
def read_root():
    return {"message": "AI Asset Organizer API is running!"}
