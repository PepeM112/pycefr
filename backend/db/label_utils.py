import logging
import sqlite3
from typing import List

from backend.db.db_utils import get_db_connection
from backend.models.schemas.class_model import ClassId, ClassItem
from backend.models.schemas.common import Level

logger = logging.getLogger(__name__)


def get_class_labels() -> List[ClassItem]:
    """Retrieves all language classes (metadata) from the database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        rows = cursor.execute("SELECT id, name, level FROM class_model").fetchall()
        return [ClassItem(id=ClassId(row["id"]), name=row["name"], level=Level(row["level"])) for row in rows]
    except sqlite3.Error as e:
        logger.error(f"Database error while fetching class labels: {e}")
        return []
    finally:
        conn.close()
