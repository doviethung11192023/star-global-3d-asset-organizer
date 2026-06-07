Trợ Lý Tổ Chức Tài Sản 3D (AI 3D Asset Organizer)

-Đây là một bài toán khoa học dữ liệu (Data Science) và kiến trúc hệ thống (Systems Architecture) kinh điển. Yêu cầu của bài toán là tiếp nhận một danh sách hỗn loạn các tài sản (assets) hoặc các phòng ban trong một dự án 3D dưới dạng văn bản thô (raw text) hoặc JSON không cấu trúc, sau đó sử dụng khả năng phân tích ngữ nghĩa của LLM để tự động phân loại chúng vào các nhóm logic (ví dụ: khu vực kỹ thuật, phòng ngủ, không gian công cộng). Hệ thống cũng phải tự động sinh ra các chuỗi định danh chuẩn (slug/file name) cho từng tài sản, tạo một bảng tóm tắt siêu dữ liệu (metadata) theo cấu trúc JSON hoặc bảng biểu, và đưa ra 2-3 khuyến nghị chiến lược nhằm tối ưu hóa quy trình quản lý thư mục.Từ góc độ thực tiễn của Star Global 3D, Option B phản ánh trực tiếp những thách thức kỹ thuật khi triển khai các dự án số hóa quy mô công nghiệp khổng lồ. Lấy ví dụ từ dự án số hóa cấu trúc giàn khoan PTSC M&C hoặc quá trình chuyển đổi số toàn diện nhà máy Ajinomoto Việt Nam. Những siêu dự án này bao gồm hàng ngàn điểm chạm (touchpoints) đa phương tiện và các mô hình 3D linh kiện máy móc phức tạp. Việc phân loại thủ công hàng ngàn tài sản số này là bất khả thi.

- Biến dữ liệu phi cấu trúc thành dữ liệu có cấu trúc cao, sẵn sàng tích hợp vào cơ sở dữ liệu MongoDB hoặc supabase hoặc hệ thống Quản lý Tài nguyên Doanh nghiệp (ERP). Khó khăn lớn nhất của phương án này là buộc LLM phải trả về định dạng JSON thuần túy (strict JSON parsing) mà không được xen lẫn bất kỳ văn bản rác (Markdown text) nào gây phá vỡ cấu trúc giải mã (JSON.parse error).


Ngăn Xếp Công Nghệ (Tech Stack):

-Backend: Python + FastAPI. (Tốc độ cao, hỗ trợ bất đồng bộ, phù hợp với ngôn ngữ mạnh nhất về AI).

-Frontend: ReactJS + Tailwind CSS. (Đáp ứng đúng yêu cầu công nghệ của công ty, phát triển giao diện nhanh gọn).  

-Database: Supabase (PostgreSQL). (Miễn phí, hỗ trợ dữ liệu phân cấp, dễ tích hợp với FastAPI).

-AI / LLM: Google Gemini 2.5 Flash Lite API kết hợp Google GenAI SDK (Hỗ trợ Structured Outputs siêu tốc và miễn phí).

-Đảm bảo chất lượng (Observability & QA): Arize Phoenix (Nền tảng giám sát và đánh giá LLM mã nguồn mở).

-Triển khai (Deployment): Railway (Tự động deploy từ GitHub, miễn phí và dễ thiết lập).

## Cập Nhật Phát Triển

### 2026-06-06 — Database Connection Module & Tests

- **Thêm** `backend/app/core/database.py`: Module kết nối PostgreSQL qua psycopg2
  - `DatabaseConfig`: đọc biến môi trường (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_SSLMODE), sinh DSN string
  - `get_connection()`: tạo kết nối psycopg2 tới Supabase
  - `get_connection_from_config()`: tạo kết nối từ config có sẵn (dễ inject/test)
- **Thêm** `backend/tests/test_database.py`: 6 test case (3 classes)
  - `TestDatabaseConfig`: kiểm tra đọc env vars, định dạng DSN, giá trị mặc định
  - `TestDatabaseConnection`: mock `psycopg2.connect()`, kiểm tra tham số truyền vào
  - `TestInsertProject`: mock cursor, INSERT vào bảng `projects`, assert ID không rỗng
- **Cập nhật** `backend/requirements.txt`: thêm `psycopg2-binary>=2.9.9`
- ✅ **Kết quả**: 6/6 tests passed

### 2026-06-06 — AI Service Module Fix & Tests

- **Sửa** `backend/app/services/ai_service.py`: Chuyển `genai.Client()` từ module-level sang lazy-init qua `_create_client()` để tránh lỗi `ValueError: No API key was provided` khi import module trong môi trường test
- **Sửa** `backend/tests/test_ai_service.py`:
  - Thay `@patch("app.services.ai_service.client.models.generate_content")` bằng `@patch("app.services.ai_service._create_client")` để mock đúng target mới
  - Cập nhật mock chain: `_create_client()` → `client` → `client.models.generate_content()`
  - Sửa model assert từ `gemini-2.0-flash-lite` → `gemini-2.5-flash-lite` cho khớp code thật
- ✅ **Kết quả**: 3/3 tests passed