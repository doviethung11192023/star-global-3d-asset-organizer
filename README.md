# AI 3D Asset Organizer 🏗️🤖

Hệ thống AI tự động bóc tách, phân loại tài sản 3D từ dữ liệu văn bản thô (raw text) — sử dụng **Gemini 2.5 Flash Lite** + **Structured Outputs** để sinh danh mục, slug, metadata chuẩn hóa.

---

## 📋 Mục lục

- [Tech Stack](#tech-stack)
- [Yêu cầu hệ thống (Prerequisites)](#yêu-cầu-hệ-thống-prerequisites)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Hướng dẫn chạy Backend (FastAPI)](#hướng-dẫn-chạy-backend-fastapi)
- [Hướng dẫn chạy Frontend (ReactJS)](#hướng-dẫn-chạy-frontend-reactjs)
- [Chạy Tests](#chạy-tests)
- [Chạy Evaluation Pipeline (Phoenix)](#chạy-evaluation-pipeline-phoenix)
- [API Endpoints](#api-endpoints)
- [Biến môi trường](#biến-môi-trường)
- [Xử lý sự cố thường gặp](#xử-lý-sự-cố-thường-gặp)

---

## 🛠 Tech Stack

| Layer | Công nghệ | Mục đích |
|-------|-----------|----------|
| **Backend** | Python 3.12 + FastAPI | API server tốc độ cao, async |
| **Frontend** | React 19 + Vite 8 + Tailwind CSS 3 | Giao diện người dùng |
| **Database** | Supabase (PostgreSQL) | Lưu trữ project, categories, assets |
| **AI / LLM** | Google Gemini 2.5 Flash Lite + GenAI SDK | Phân loại tài sản bằng Structured Outputs |
| **Observability** | Arize Phoenix 14.6 + OpenTelemetry | Tracing Gemini + đánh giá chất lượng |
| **Deployment** | Railway (Docker + Nginx) | Triển khai production |

---

## ⚙️ Yêu cầu hệ thống (Prerequisites)

- **Python** 3.11+
- **Node.js** 22+
- **npm** 10+
- **Git**
- **Tài khoản Supabase** (miễn phí tại [supabase.com](https://supabase.com))
- **API Key Gemini** (miễn phí tại [aistudio.google.com](https://aistudio.google.com))

---

## 📁 Cấu trúc dự án

```
star-global-3d-asset-organizer/
├── backend/                          # FastAPI Backend
│   ├── main.py                       # Entry point (uvicorn)
│   ├── requirements.txt              # Python dependencies
│   ├── Dockerfile                    # Build production
│   ├── Dockerfile.phoenix            # Build Phoenix Collector
│   ├── .env                          # Biến môi trường (KHÔNG push lên Git)
│   ├── app/
│   │   ├── api/
│   │   │   └── organize.py           # POST /api/v1/organize-assets
│   │   ├── core/
│   │   │   └── database.py           # Supabase client (singleton)
│   │   ├── models/
│   │   │   └── schemas.py            # Pydantic schemas (Gemini + API)
│   │   └── services/
│   │       ├── ai_service.py         # Gọi Gemini 2.5 Flash Lite
│   │       └── db_service.py         # Lưu vào Supabase
│   ├── eval/
│   │   ├── run_eval.py               # Evaluation pipeline
│   │   ├── golden_data.csv           # 5 test cases mẫu
│   │   ├── results.csv               # Kết quả eval (được sinh ra)
│   │   ├── Asset_Count_Accuracy.py
│   │   ├── Category_Count_Accuracy.py
│   │   ├── Asset_Extraction_F1.py
│   │   ├── Asset_Slug_Accuracy.py
│   │   ├── Category_Classification_Accuracy.py
│   │   └── Category_Slug_Accuracy.py
│   ├── supabase/
│   │   └── schema.sql                # SQL tạo bảng (projects, categories, assets)
│   └── tests/
│       ├── test_ai_service.py        # Test AI service (mock Gemini)
│       ├── test_api.py               # Test API endpoint
│       ├── test_data.py              # Test lưu database thật
│       ├── test_database_connection.py
│       └── test_evaluators.py
│
└── frontend-app/                     # React Frontend
    ├── package.json
    ├── vite.config.js                # Vite config + proxy /api
    ├── Dockerfile                    # Build production (multi-stage)
    ├── nginx.conf                    # Nginx config cho Railway
    └── src/
        ├── main.jsx                  # Entry point
        ├── App.jsx                   # Component chính (2 cột)
        ├── index.css                 # Tailwind directives
        ├── services/
        │   └── apiClient.js          # Axios API client
        ├── hooks/
        │   └── useAutoSave.js        # Auto-save localStorage
        ├── components/
        │   ├── AssetForm.jsx         # Form nhập liệu
        │   ├── ResultView.jsx        # Hiển thị kết quả
        │   └── ui/
        │       ├── Spinner.jsx       # Loading spinner
        │       └── SkeletonLoader.jsx
        └── utils/
            └── exportHelper.js
```

---

## 🚀 Hướng dẫn chạy Backend (FastAPI)

### 1. Tạo virtual environment

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Tạo database trên Supabase

1. Đăng nhập [Supabase](https://supabase.com) → **New Project**
2. Vào **SQL Editor** → paste nội dung file `backend/supabase/schema.sql` → **Run**
3. Vào **Project Settings** → **API** → copy `Project URL` (SUPABASE_URL) và `anon public key` (SUPABASE_KEY)

### 4. Tạo file `.env`

Tạo file `backend/.env` với nội dung:

```env
GEMINI_API_KEY=AIzaSy...                    # Key từ Google AI Studio
SUPABASE_URL=https://xxxx.supabase.co       # URL dự án Supabase
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIs...        # anon public key từ Supabase
ENV=development
DEBUG=True
PHOENIX_COLLECTOR_ENDPOINT="http://localhost:6006/v1/traces"
PHOENIX_PROJECT_NAME="star-global-3d-asset-organizer"
```

### 5. Chạy server

```bash
# Terminal 1 - Backend (cần activate venv trước)
cd backend
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

→ Backend chạy tại: **http://localhost:8000**
→ Docs (Swagger UI): **http://localhost:8000/docs**

Kiểm tra nhanh:

```bash
curl http://localhost:8000/
# → {"message": "AI Asset Organizer API is running!"}
```

---

## 🎨 Hướng dẫn chạy Frontend (ReactJS)

### 1. Cài đặt dependencies

```bash
cd frontend-app
npm install
```

### 2. Chạy dev server

```bash
npm run dev
```

→ Frontend chạy tại: **http://localhost:3000**

> **Lưu ý:** Vite dev server tự động proxy tất cả request `/api/*` tới `http://127.0.0.1:8000` (backend). Không cần CORS phức tạp khi chạy local.

### 3. Build production (khi cần)

```bash
npm run build
# Output: frontend-app/dist/
```

---

## 🧪 Chạy Tests

Tất cả test đều chạy từ thư mục `backend/` (đã activate venv):

```bash
cd backend

# Test AI Service (mock Gemini API)
pytest tests/test_ai_service.py -v

# Test API Endpoint (mock toàn bộ)
pytest tests/test_api.py -v

# Test database connection
pytest tests/test_database_connection.py -v

# Test evaluator slug format
pytest tests/test_evaluators.py -v

# Test lưu database thật (cần Supabase đã cấu hình)
pytest tests/test_data.py -v

# Chạy tất cả tests
pytest tests/ -v
```

---

## 📊 Chạy Evaluation Pipeline (Phoenix)

Hệ thống có 6 evaluator tự động đánh giá chất lượng output của Gemini dựa trên 5 test cases mẫu.

### 1. Cài đặt Phoenix (đã có trong requirements.txt)

### 2. Chạy Phoenix Dashboard (tùy chọn, để xem trace)

```bash
cd backend
venv\Scripts\activate
phoenix serve
# → Dashboard: http://localhost:6060
```

### 3. Chạy evaluation pipeline

```bash
cd backend
venv\Scripts\activate
python eval/run_eval.py
```

Pipeline sẽ:
1. Load 5 test cases từ `golden_data.csv`
2. Gọi Gemini để phân loại từng test case
3. Chạy cả 6 evaluators qua Phoenix
4. Tính điểm trung bình từng metric
5. Lưu kết quả chi tiết vào `eval/results.csv`

### 6 Evaluators:

| Evaluator | Đo lường | Cách tính |
|-----------|----------|-----------|
| `asset-count-accuracy` | Đếm asset | 1 nếu tổng asset khớp, 0 nếu không |
| `category-count-accuracy` | Đếm category | 1 nếu tổng category khớp |
| `asset-extraction-f1` | Chất lượng trích xuất | F1-score: precision & recall của danh sách asset |
| `asset-slug-accuracy` | Slug asset | Tỷ lệ slug asset đúng |
| `category-classification` | Phân loại category | Tỷ lệ giao giữa category dự đoán và thực tế |
| `category-slug-accuracy` | Slug category | Tỷ lệ slug category đúng |

---

## 🌐 API Endpoints

### `POST /api/v1/organize-assets`

Endpoint chính — nhận dữ liệu thô, phân loại bằng Gemini, lưu vào Supabase.

**Request body:**

```json
{
  "project_name": "Nhà máy Ajinomoto Việt Nam",
  "raw_text": "máy bơm ly tâm số 1, van xả áp 01 nằm ở khu vực trạm bơm chính..."
}
```

**Success response (200):**

```json
{
  "project_id": "uuid-string",
  "status": "success",
  "data": {
    "metadata_summary": {
      "total_assets": 10,
      "total_categories": 4,
      "insights": "Dự án có cấu trúc không gian đa dạng..."
    },
    "ai_suggestions": [
      "Nên thêm tiền tố khu vực vào tên asset để dễ tra cứu",
      "Cân nhắc chuẩn hóa slug theo định dạng: {khu-vực}_{thiết-bị}_{số-thứ-tự}"
    ],
    "categories": [
      {
        "category_name": "Trạm bơm chính",
        "slug": "tram-bom-chinh",
        "assets": [
          { "original_name": "máy bơm ly tâm số 1", "slug": "may-bom-ly-tam-01", "description": "..." }
        ]
      }
    ]
  }
}
```

**Error responses:**

| Status | Ý nghĩa |
|--------|---------|
| `422` | Input không hợp lệ (thiếu tên dự án, raw_text quá ngắn) |
| `503` | Lỗi Gemini API (hết token, timeout) |
| `500` | Lỗi lưu database |

---

## 🔐 Biến môi trường

| Variable | Bắt buộc | Mặc định | Mô tả |
|----------|----------|----------|-------|
| `GEMINI_API_KEY` | ✅ | — | Google Gemini API key |
| `SUPABASE_URL` | ✅ | — | URL dự án Supabase |
| `SUPABASE_KEY` | ✅ | — | Supabase anon/public key |
| `PHOENIX_COLLECTOR_ENDPOINT` | ❌ | `http://localhost:6006/v1/traces` | Endpoint Phoenix tracing |
| `PHOENIX_PROJECT_NAME` | ❌ | `star-global-3d-asset-organizer` | Tên project trên Phoenix |
| `ENV` | ❌ | `development` | Môi trường (development/production) |
| `DEBUG` | ❌ | `True` | Bật/tắt debug logging |

---

## 🔧 Xử lý sự cố thường gặp

### 1. `ModuleNotFoundError: No module named 'phoenix'`

```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Backend lỗi `ValueError: Thiếu cấu hình Supabase`

→ Kiểm tra file `backend/.env` đã có `SUPABASE_URL` và `SUPABASE_KEY` chưa.

### 3. Vite proxy lỗi `ECONNREFUSED ::1:8000`

→ Đảm bảo backend đang chạy trên cổng 8000.
→ Nếu dùng Windows, Node.js resolve `localhost` thành IPv6 `::1`. Fix: `vite.config.js` đã dùng `127.0.0.1` thay vì `localhost`.

### 4. Gemini trả về lỗi 503

→ Kiểm tra `GEMINI_API_KEY` còn hạn và còn quota.
→ Kiểm tra log: `[AI Error]: ...` trong terminal backend.

### 5. `npm run dev` lỗi

```bash
cd frontend-app
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## 🚢 Triển khai Production (Railway)

Tóm tắt:
1. Push code lên GitHub
2. Railway → New Project → Deploy from GitHub (3 services: backend, frontend, phoenix)
3. Set biến môi trường trên Railway Dashboard
4. Backend: `SUPABASE_URL`, `SUPABASE_KEY`, `GEMINI_API_KEY`
5. Frontend: `BACKEND_URL` = URL backend service
