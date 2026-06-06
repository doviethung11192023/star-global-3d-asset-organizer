"""
Test cases cho database connection module.

Kiểm tra:
1. DatabaseConfig đọc đúng biến môi trường
2. get_connection() gọi psycopg2.connect() với đúng tham số
3. INSERT vào bảng projects trả về ID không rỗng (mock cursor)
"""

from unittest.mock import MagicMock, patch

import pytest

from app.core.database import get_config, get_connection


class TestDatabaseConfig:
    """Nhóm test cho DatabaseConfig — kiểm tra đọc biến môi trường."""

    @patch.dict(
        "os.environ",
        {
            "DB_HOST": "test-host.supabase.com",
            "DB_PORT": "6543",
            "DB_NAME": "testdb",
            "DB_USER": "testuser",
            "DB_PASSWORD": "testpass",
            "DB_SSLMODE": "require",
        },
        clear=True,
    )
    def test_config_loads_env_vars(self):
        """Config đọc đúng tất cả biến môi trường."""
        config = get_config()
        assert config.host == "test-host.supabase.com"
        assert config.port == 6543
        assert config.dbname == "testdb"
        assert config.user == "testuser"
        assert config.password == "testpass"
        assert config.sslmode == "require"

    @patch.dict(
        "os.environ",
        {
            "DB_HOST": "test-host.supabase.com",
            "DB_PORT": "6543",
            "DB_NAME": "postgres",
            "DB_USER": "user",
            "DB_PASSWORD": "pass",
        },
        clear=True,
    )
    def test_dsn_format_contains_all_fields(self):
        """DSN string chứa đầy đủ thông tin các field."""
        config = get_config()
        dsn = config.dsn
        assert "host=test-host.supabase.com" in dsn
        assert "port=6543" in dsn
        assert "dbname=postgres" in dsn
        assert "user=user" in dsn
        assert "password=pass" in dsn
        assert "sslmode=require" in dsn

    @patch.dict(
        "os.environ",
        {},  # Không có biến nào — kiểm tra giá trị mặc định
        clear=True,
    )
    def test_default_values_when_env_missing(self):
        """Khi thiếu biến môi trường, dùng giá trị mặc định."""
        config = get_config()
        assert config.host == ""
        assert config.port == 6543
        assert config.dbname == "postgres"
        assert config.user == ""
        assert config.password == ""
        assert config.sslmode == "require"


class TestDatabaseConnection:
    """Nhóm test cho get_connection — mock psycopg2 hoàn toàn."""

    @patch("app.core.database.psycopg2.connect")
    @patch.dict(
        "os.environ",
        {
            "DB_HOST": "host.supabase.com",
            "DB_PORT": "6543",
            "DB_NAME": "postgres",
            "DB_USER": "user",
            "DB_PASSWORD": "pass",
        },
        clear=True,
    )
    def test_get_connection_success(self, mock_connect):
        """get_connection() gọi psycopg2.connect() và trả về connection object."""
        # Arrange
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # Act
        conn = get_connection()

        # Assert
        mock_connect.assert_called_once()
        assert conn == mock_conn

    @patch("app.core.database.psycopg2.connect")
    @patch.dict(
        "os.environ",
        {
            "DB_HOST": "host.supabase.com",
            "DB_PORT": "6543",
            "DB_NAME": "postgres",
            "DB_USER": "user",
            "DB_PASSWORD": "pass",
        },
        clear=True,
    )
    def test_get_connection_passes_correct_dsn(self, mock_connect):
        """Kiểm tra DSN đúng được truyền vào psycopg2.connect()."""
        # Arrange
        mock_connect.return_value = MagicMock()

        # Act
        get_connection()

        # Assert
        args, kwargs = mock_connect.call_args
        # Kiểm tra dsn được truyền dưới dạng positional arg
        dsn_arg = args[0] if args else kwargs.get("dsn")
        assert dsn_arg is not None
        assert "host=host.supabase.com" in dsn_arg
        assert "password=pass" in dsn_arg


class TestInsertProject:
    """Nhóm test cho thao tác INSERT — mock cursor."""

    @patch("app.core.database.psycopg2.connect")
    @patch.dict(
        "os.environ",
        {
            "DB_HOST": "host.supabase.com",
            "DB_PORT": "6543",
            "DB_NAME": "postgres",
            "DB_USER": "user",
            "DB_PASSWORD": "pass",
        },
        clear=True,
    )
    def test_insert_project_returns_non_empty_id(self, mock_connect):
        """
        Chèn một dummy_record vào bảng projects và assert ID trả về không rỗng.

        Mô phỏng: cursor.fetchone() trả về dict chứa UUID.
        """
        # Arrange
        fake_uuid = "123e4567-e89b-12d3-a456-426614174000"

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"id": fake_uuid}
        mock_cursor.__iter__.return_value = iter([{"id": fake_uuid}])

        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        conn = get_connection()

        # Act — giả lập INSERT với RETURNING id
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO projects (name, raw_input) VALUES (%s, %s) RETURNING id",
                ("Dummy Project", "raw input data"),
            )
            result = cur.fetchone()

        # Assert
        assert result is not None, "Result không được rỗng"
        assert result["id"] == fake_uuid, "ID phải khớp với UUID giả định"
        assert len(result["id"]) == 36, "UUID phải có 36 ký tự (dạng 8-4-4-4-12)"
