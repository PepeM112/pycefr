import logging
import sqlite3
from typing import List

from backend.db.db_utils import get_db_connection
from backend.models.schemas.class_model import ClassId, ClassPublic
from backend.models.schemas.common import Level

logger = logging.getLogger(__name__)


def get_class_labels() -> List[ClassPublic]:
    """
    Retrieve all language classes and their metadata from the database.

    Connects to the local SQLite database to fetch the mapping between
    class identifiers and their assigned CEFR levels.

    Returns:
        List[ClassPublic]: A list of ClassPublic objects containing ID and Level.
            Returns an empty list if a database error occurs.

    Raises:
        sqlite3.Error: Logged internally if the query fails, but not raised to caller.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        rows = cursor.execute("SELECT id, level FROM class_model").fetchall()
        return [ClassPublic(id=ClassId(row["id"]), level=Level(row["level"])) for row in rows]
    except sqlite3.Error as e:
        logger.error(f"Database error while fetching class labels: {e}")
        return []
    finally:
        conn.close()
