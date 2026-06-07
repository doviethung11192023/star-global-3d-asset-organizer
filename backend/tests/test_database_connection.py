# from app.core.database import get_supabase

# #python -m pytest tests/test_database_connection.py -v -s
# def test_supabase_connection():
#     try:
#         supabase = get_supabase()

#         result = (
#             supabase
#             .table("projects")
#             .select("*")
#             .limit(1)
#             .execute()
#         )

#         print("✅ Connected")
#         print(result.data)

#         assert True

#     except Exception as e:
#         assert False, f"Connection failed: {e}"

from app.core.database import get_supabase


def test_singleton():
    client1 = get_supabase()
    client2 = get_supabase()

    assert client1 is client2

import pytest
from app.core.database import DatabaseConfig


def test_missing_env(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)

    with pytest.raises(ValueError):
        DatabaseConfig()