# """
# Module kết nối database PostgreSQL (Supabase) dùng psycopg2.

# Sử dụng:
#     from app.core.database import get_connection, get_db

#     # Cách 1: Trực tiếp
#     conn = get_connection()
#     with conn.cursor() as cur:
#         cur.execute("SELECT ...")

#     # Cách 2: Context manager (tự động commit/rollback/close)
#     with get_db() as conn:
#         with conn.cursor() as cur:
#             cur.execute("INSERT ...")
# """

# import os

# import psycopg2
# from dotenv import load_dotenv

# load_dotenv()


# class DatabaseConfig:
#     """Đọc cấu hình kết nối database từ biến môi trường.

#     Các biến môi trường:
#         DB_HOST (str): Host Supabase (VD: aws-1-ap-southeast-2.pooler.supabase.com)
#         DB_PORT (int): Cổng kết nối (mặc định: 6543)
#         DB_NAME (str): Tên database (mặc định: postgres)
#         DB_USER (str): Username
#         DB_PASSWORD (str): Password
#         DB_SSLMODE (str): SSL mode (mặc định: require)
#     """

#     def __init__(self) -> None:
#         self.host: str = os.getenv("DB_HOST", "")
#         self.port: int = int(os.getenv("DB_PORT", "6543"))
#         self.dbname: str = os.getenv("DB_NAME", "postgres")
#         self.user: str = os.getenv("DB_USER", "")
#         self.password: str = os.getenv("DB_PASSWORD", "")
#         self.sslmode: str = os.getenv("DB_SSLMODE", "require")

#     @property
#     def dsn(self) -> str:
#         """Trả về DSN string ở định dạng key=value cho psycopg2."""
#         return (
#             f"host={self.host} port={self.port} "
#             f"dbname={self.dbname} user={self.user} "
#             f"password={self.password} sslmode={self.sslmode}"
#         )


# def get_config() -> DatabaseConfig:
#     """Factory function — dễ mock trong test."""
#     return DatabaseConfig()


# def get_connection():
#     """Tạo kết nối PostgreSQL tới Supabase qua psycopg2."""
#     config = get_config()
#     return psycopg2.connect(config.dsn)


# def get_connection_from_config(config: DatabaseConfig):
#     """Tạo kết nối từ một DatabaseConfig có sẵn (dùng khi cần tùy chỉnh)."""
#     return psycopg2.connect(config.dsn)

"""
Module kết nối database Supabase sử dụng official supabase-py client.

Sử dụng trong Services/Routers:
    from app.core.database import get_supabase
    
    # Cách dùng:
    supabase = get_supabase()
    data = supabase.table("projects").select("*").execute()
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

# Khởi tạo logger để dễ dàng truy vết (tracing) khi debug
logger = logging.getLogger(__name__)

# Load biến môi trường từ file.env
load_dotenv()

class DatabaseConfig:
    """Đọc cấu hình kết nối database từ biến môi trường."""
    
    def __init__(self) -> None:
        self.url: str = os.getenv("SUPABASE_URL", "")
        self.key: str = os.getenv("SUPABASE_KEY", "")
        
        # Validate ngay lúc khởi động server để phát hiện lỗi sớm
        if not self.url or not self.key:
            logger.error("LỖI NGHIÊM TRỌNG: Thiếu biến môi trường SUPABASE_URL hoặc SUPABASE_KEY")
            raise ValueError("Thiếu cấu hình Supabase trong file.env")

# Khởi tạo một biến global ẩn để chứa instance của client
_supabase_client: Client | None = None

def get_supabase() -> Client:
    """
    Tạo và trả về kết nối Supabase (Áp dụng Singleton Pattern).
    Đảm bảo toàn bộ ứng dụng FastAPI chỉ dùng chung 1 client, tiết kiệm bộ nhớ.
    """
    global _supabase_client
    
    if _supabase_client is None:
        try:
            config = DatabaseConfig()
            _supabase_client = create_client(config.url, config.key)
            logger.info("Đã khởi tạo thành công kết nối tới Supabase REST API.")
        except Exception as e:
            logger.error(f"Không thể kết nối tới Supabase: {str(e)}")
            raise e
            
    return _supabase_client

def get_db_dependency():
    """
    Hàm Dependency Injection dành riêng cho FastAPI Router.
    Cho phép Pytest dễ dàng mock (giả lập) database client khi test API.
    """
    return get_supabase()