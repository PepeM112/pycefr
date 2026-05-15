import sqlite3
from pathlib import Path

import pytest

_DB_DIR = Path(__file__).resolve().parent.parent / "db"


@pytest.fixture(scope="module")
def schema_sql() -> str:
    return (_DB_DIR / "schema.sql").read_text()


@pytest.fixture(scope="module")
def seed_sql() -> str:
    return (_DB_DIR / "initialize_db.sql").read_text()


@pytest.fixture()
def db(tmp_path: Path, schema_sql: str, seed_sql: str, monkeypatch: pytest.MonkeyPatch) -> Path:
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.executescript(schema_sql)
    conn.executescript(seed_sql)
    conn.close()

    monkeypatch.setattr("backend.db.db_utils.DATABASE_PATH", str(db_path))
    return db_path


@pytest.fixture()
def db_empty(tmp_path: Path, schema_sql: str, monkeypatch: pytest.MonkeyPatch) -> Path:
    db_path = tmp_path / "test_empty.db"
    conn = sqlite3.connect(str(db_path))
    conn.executescript(schema_sql)
    conn.close()

    monkeypatch.setattr("backend.db.db_utils.DATABASE_PATH", str(db_path))
    return db_path
