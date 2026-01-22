import os
import sqlite3
from collections.abc import Generator

import pytest

from backend.db import db_utils

TEST_DB_PATH = "database/pycefr_test.db"


@pytest.fixture(scope="session", autouse=True)
def setup_test_database() -> Generator[None, None, None]:
    """Configura la base de datos de test una vez por sesión."""
    # Forzamos a db_utils a usar la DB de test
    os.environ["DATABASE_PATH"] = TEST_DB_PATH
    db_utils.DATABASE_PATH = TEST_DB_PATH

    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    conn = sqlite3.connect(TEST_DB_PATH)

    # Aplicar schema.sql
    with open("backend/db/schema.sql", "r") as f:
        conn.executescript(f.read())

    # Aplicar initialize_db.sql
    with open("backend/db/initialize_db.sql", "r") as f:
        conn.executescript(f.read())

    conn.close()
    yield

    # Opcional: limpiar al terminar
    # if os.path.exists(TEST_DB_PATH): os.remove(TEST_DB_PATH)
