"""
Module kết nối database PostgreSQL (Supabase) dùng psycopg2.

Sử dụng:
    from app.core.database import get_connection, get_db

    # Cách 1: Trực tiếp
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT ...")

    # Cách 2: Context manager (tự động commit/rollback/close)
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT ...")
"""

import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig:
    """Đọc cấu hình kết nối database từ biến môi trường.

    Các biến môi trường:
        DB_HOST (str): Host Supabase (VD: aws-1-ap-southeast-2.pooler.supabase.com)
        DB_PORT (int): Cổng kết nối (mặc định: 6543)
        DB_NAME (str): Tên database (mặc định: postgres)
        DB_USER (str): Username
        DB_PASSWORD (str): Password
        DB_SSLMODE (str): SSL mode (mặc định: require)
    """

    def __init__(self) -> None:
        self.host: str = os.getenv("DB_HOST", "")
        self.port: int = int(os.getenv("DB_PORT", "6543"))
        self.dbname: str = os.getenv("DB_NAME", "postgres")
        self.user: str = os.getenv("DB_USER", "")
        self.password: str = os.getenv("DB_PASSWORD", "")
        self.sslmode: str = os.getenv("DB_SSLMODE", "require")

    @property
    def dsn(self) -> str:
        """Trả về DSN string ở định dạng key=value cho psycopg2."""
        return (
            f"host={self.host} port={self.port} "
            f"dbname={self.dbname} user={self.user} "
            f"password={self.password} sslmode={self.sslmode}"
        )


def get_config() -> DatabaseConfig:
    """Factory function — dễ mock trong test."""
    return DatabaseConfig()


def get_connection():
    """Tạo kết nối PostgreSQL tới Supabase qua psycopg2."""
    config = get_config()
    return psycopg2.connect(config.dsn)


def get_connection_from_config(config: DatabaseConfig):
    """Tạo kết nối từ một DatabaseConfig có sẵn (dùng khi cần tùy chỉnh)."""
    return psycopg2.connect(config.dsn)
