-- Kích hoạt extension để sinh UUID tự động (chuẩn của Supabase)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- 1. BẢNG DỰ ÁN (PROJECTS)
-- Lưu trữ thông tin dự án, toàn bộ dữ liệu thô ban đầu và ĐÁNH GIÁ TỪ AI
-- ==========================================
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    raw_input TEXT NOT NULL, -- Dữ liệu gốc để đối chiếu và audit sau này
    metadata_summary JSONB,  -- Lưu tóm tắt metadata dạng JSON (VD: {"total_assets": 150, "categories": 5})
    ai_suggestions JSONB,    -- Lưu đề xuất cải thiện của AI dạng mảng JSON (VD: ["Đề xuất 1", "Đề xuất 2"])
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ==========================================
-- 2. BẢNG DANH MỤC / KHU VỰC (CATEGORIES)
-- Lưu trữ các nhóm khu vực do AI tự động phân loại
-- ==========================================
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL, -- Ví dụ: "Khu vực kỹ thuật"
    slug TEXT NOT NULL, -- Ví dụ: "khu-vuc-ky-thuat" (Dùng cho URL/Tên file)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ==========================================
-- 3. BẢNG TÀI SẢN 3D CHI TIẾT (ASSETS)
-- Lưu trữ từng thiết bị, điểm chạm cụ thể trong không gian
-- ==========================================
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    original_name TEXT NOT NULL, -- Tên tài sản gốc do kỹ sư nhập
    slug TEXT NOT NULL,          -- Chuỗi định danh chuẩn SEO
    description TEXT,            -- Mô tả ngắn (có thể NULL)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ==========================================
-- TẠO INDEX (CHỈ MỤC) ĐỂ TỐI ƯU HIỆU SUẤT TRUY VẤN
-- ==========================================
CREATE INDEX idx_categories_project_id ON categories(project_id);
CREATE INDEX idx_assets_category_id ON assets(category_id);

-- (Tùy chọn) Bật Row Level Security (RLS) để bảo mật API mức cơ bản
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;

-- Tạo Policy cho phép API (được xác thực ẩn danh) có quyền Thêm và Đọc dữ liệu
CREATE POLICY "Cho phép tất cả truy cập đọc" ON projects FOR SELECT USING (true);
CREATE POLICY "Cho phép tất cả thêm mới" ON projects FOR INSERT WITH CHECK (true);

CREATE POLICY "Cho phép tất cả truy cập đọc" ON categories FOR SELECT USING (true);
CREATE POLICY "Cho phép tất cả thêm mới" ON categories FOR INSERT WITH CHECK (true);

CREATE POLICY "Cho phép tất cả truy cập đọc" ON assets FOR SELECT USING (true);
CREATE POLICY "Cho phép tất cả thêm mới" ON assets FOR INSERT WITH CHECK (true);