import logging
import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple

from backend.constants.analysis_rules import get_class_level
from backend.models.schemas.analysis import Analysis, AnalysisClass, AnalysisCreate, AnalysisList, AnalysisUpdate
from backend.models.schemas.class_model import ClassId
from backend.models.schemas.common import Origin

logger = logging.getLogger(__name__)

DATABASE_PATH = "database/pycefr.db"


def get_db_connection() -> sqlite3.Connection:
    """
    Establishes a connection to the SQLite database.

    Returns:
        sqlite3.Connection: A connection object with the row_factory set to Row.

    Raises:
        sqlite3.OperationalError: If the database connection fails.
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.OperationalError as e:
        logger.critical(f"Failed to connect to database at {DATABASE_PATH}: {e}")
        raise


# --- READ OPERATIONS ---

def get_analyses(page: int, per_page: int) -> Tuple[List[AnalysisList], int]:
    """
    Retrieves a paginated list of analysis summaries.

    Args:
        page (int): The current page number (starts at 1).
        per_page (int): The number of records to retrieve per page.

    Returns:
        Tuple[List[AnalysisList], int]: A list of analyses and the total count.

    Raises:
        sqlite3.Error: If a database error occurs.
    """
    offset = (page - 1) * per_page
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        rows = cursor.execute(
            """
            SELECT id, name, origin_id, created_at, total_hours
            FROM analyses
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (per_page, offset),
        ).fetchall()

        total = cursor.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]

        analyses: List[AnalysisList] = []
        for row in rows:
            analyses.append(
                AnalysisList(
                    id=row["id"],
                    name=row["name"],
                    origin=Origin(row["origin_id"]),
                    created_at=datetime.fromisoformat(row["created_at"].replace(" ", "T")),
                    total_hours=row["total_hours"]
                )
            )

        return analyses, total
    except sqlite3.Error as e:
        logger.error(f"Error fetching analyses list: {e}")
        raise
    finally:
        conn.close()


def get_analysis_details(analysis_id: int) -> Optional[Analysis]:
    """
    Fetches a complete analysis including its nested code classes.

    Args:
        analysis_id (int): The unique identifier of the analysis.

    Returns:
        Optional[Analysis]: The analysis data if found, None otherwise.

    Raises:
        sqlite3.Error: If a database error occurs.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        analysis_row = cursor.execute(
            "SELECT * FROM analyses WHERE id = ?", (analysis_id,)
        ).fetchone()

        if analysis_row is None:
            return None

        classes_rows = cursor.execute(
            "SELECT class_id, instances FROM analysis_class WHERE analysis_id = ?",
            (analysis_id,),
        ).fetchall()

        classes: List[AnalysisClass] = []
        for c_row in classes_rows:
            cid_value: int = c_row["class_id"]
            try:
                class_id_enum = ClassId(cid_value)
            except ValueError:
                class_id_enum = ClassId.UNKNOWN

            classes.append(
                AnalysisClass(
                    class_id=class_id_enum,
                    instances=c_row["instances"],
                    level=get_class_level(class_id_enum)
                )
            )

        return Analysis(
            id=analysis_row["id"],
            name=analysis_row["name"],
            origin=Origin(analysis_row["origin_id"]),
            created_at=datetime.fromisoformat(analysis_row["created_at"].replace(" ", "T")),
            total_hours=analysis_row["total_hours"],
            classes=classes,
        )
    except sqlite3.Error as e:
        logger.error(f"Error fetching analysis details for ID {analysis_id}: {e}")
        raise
    finally:
        conn.close()


# --- WRITE OPERATIONS ---

def insert_full_analysis(analysis: AnalysisCreate) -> Optional[int]:
    """
    Inserts a new analysis and its related classes in a single transaction.

    Args:
        analysis (AnalysisCreate): The analysis data to insert.

    Returns:
        Optional[int]: The ID of the newly created analysis.

    Raises:
        ValueError: If a duplicate class_id or integrity violation occurs.
        sqlite3.Error: If a general database error occurs.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO analyses (name, origin_id, total_hours) VALUES (?, ?, ?)",
            (analysis.name, analysis.origin.value, analysis.total_hours)
        )
        analysis_id = cursor.lastrowid

        classes_data = [
            (analysis_id, c.class_id.value, c.instances)
            for c in analysis.classes
        ]

        cursor.executemany(
            "INSERT INTO analysis_class (analysis_id, class_id, instances) VALUES (?, ?, ?)",
            classes_data,
        )

        conn.commit()
        return analysis_id
    except sqlite3.IntegrityError as e:
        conn.rollback()
        logger.warning(f"Integrity violation on insert: {e}")
        raise ValueError(f"Integrity error: {e}") from e
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Database error during full analysis insertion: {e}")
        raise
    finally:
        conn.close()


def update_analysis(analysis_id: int, analysis_update: AnalysisUpdate) -> bool:
    """
    Updates an analysis record and replaces its associated classes.

    Args:
        analysis_id (int): The ID of the analysis to update.
        analysis_update (AnalysisUpdate): The fields to update.

    Returns:
        bool: True if the update was successful, False if the analysis was not found.

    Raises:
        ValueError: If duplicate classes are provided.
        sqlite3.Error: If a database error occurs.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Check existence
        if not cursor.execute("SELECT 1 FROM analyses WHERE id = ?", (analysis_id,)).fetchone():
            return False

        if analysis_update.name is not None:
            cursor.execute("UPDATE analyses SET name = ? WHERE id = ?", (analysis_update.name, analysis_id))

        if analysis_update.origin is not None:
            cursor.execute(
                "UPDATE analyses SET origin_id = ? WHERE id = ?",
                (analysis_update.origin.value, analysis_id)
            )

        if analysis_update.classes is not None:
            cursor.execute("DELETE FROM analysis_class WHERE analysis_id = ?", (analysis_id,))
            classes_data = [
                (analysis_id, c.class_id.value, c.instances)
                for c in analysis_update.classes
            ]
            cursor.executemany(
                "INSERT INTO analysis_class (analysis_id, class_id, instances) VALUES (?, ?, ?)",
                classes_data,
            )

        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        conn.rollback()
        logger.warning(f"Integrity violation on update for ID {analysis_id}: {e}")
        raise ValueError(f"Update integrity error: {e}") from e
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Database error updating analysis {analysis_id}: {e}")
        raise
    finally:
        conn.close()


def delete_analysis(analysis_id: int) -> bool:
    """
    Deletes an analysis record and its dependencies.

    Args:
        analysis_id (int): The ID of the analysis to delete.

    Returns:
        bool: True if a record was deleted, False otherwise.

    Raises:
        sqlite3.Error: If a database error occurs.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Database error deleting analysis {analysis_id}: {e}")
        raise
    finally:
        conn.close()
