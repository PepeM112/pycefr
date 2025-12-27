import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from config.analysis_map import get_class_level
from models.analysis import Analysis, AnalysisClass, AnalysisCreate, AnalysisList, AnalysisUpdate
from models.class_model import ClassId
from models.common import Origin

DATABASE_PATH = "database/pycefr.db"


def get_db_connection() -> sqlite3.Connection:
    """
    Establishes a connection to the SQLite database.

    Returns:
        sqlite3.Connection: A connection object with the row_factory set to Row.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# --- READ OPERATIONS ---
def get_analyses(page: int, per_page: int) -> Tuple[List[AnalysisList], int]:
    """
    Retrieves a paginated list of analysis summaries.

    Args:
        page (int): The current page number (starts at 1).
        per_page (int): The number of records to retrieve per page.

    Returns:
        Tuple[List[AnalysisList], int]: A tuple containing:
            - A list of analyses.
            - The total count of analysis records in the database.
    """
    offset = (page - 1) * per_page
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        rows = cursor.execute(
            """
            SELECT id, name, origin_id, created_at
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
                )
            )

        return analyses, total
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        return [], 0
    finally:
        conn.close()


def get_analysis_details(analysis_id: int) -> Optional[Analysis]:
    """
    Fetches a complete analysis including its nested code classes.

    Args:
        analysis_id (int): The unique identifier of the analysis.

    Returns:
        Optional[Dict[str, Any]]: The analysis data if found, None otherwise.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        analysis_row = cursor.execute(
            """
            SELECT *
            FROM analyses
            WHERE id = ?
            """,
            (analysis_id,),
        ).fetchone()

        if analysis_row is None:
            return None

        classes_rows = cursor.execute(
            """
            SELECT class_id, instances
            FROM analysis_class
            WHERE analysis_id = ?
            """,
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
                    class_id=class_id_enum, instances=c_row["instances"], level=get_class_level(class_id_enum)
                )
            )

        analysis: Analysis = Analysis(
            id=analysis_row["id"],
            name=analysis_row["name"],
            origin=Origin(analysis_row["origin_id"]),
            created_at=datetime.fromisoformat(analysis_row["created_at"].replace(" ", "T")),
            classes=classes,
        )

        return analysis
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        return None
    finally:
        conn.close()


def insert_full_analysis(analysis: AnalysisCreate) -> Optional[int]:
    """
    Inserts a new analysis and its related classes in a single transaction.

    Args:
        name (str): The name of the analysis.
        origin (int): The integer value of the Origin Enum.
        classes (List[Dict]): List of dicts with 'class_id' and 'instances'.

    Returns:
        Optional[int]: The ID of the newly created analysis, or None if it failed.

    Raises:
        ValueError: If a duplicate class_id is provided for the same analysis.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO analyses (name, origin_id) VALUES (?, ?)", (analysis.name, analysis.origin))
        analysis_id = cursor.lastrowid

        classes = [c.model_dump() for c in analysis.classes]

        classes_data = [(analysis_id, c["class_id"], c["instances"]) for c in classes]
        cursor.executemany(
            "INSERT INTO analysis_classes (analysis_id, class_id, instances) VALUES (?, ?, ?)",
            classes_data,
        )
        conn.commit()
        return analysis_id
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise ValueError(f"Integrity error: Duplicate class detected or foreign key violation. Details: {e}") from e
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def update_analysis(analysis_id: int, analysis_update: AnalysisUpdate) -> bool:
    """
    Updates an analysis record and replaces its associated classes.

    Args:
        analysis_id (int): The ID of the analysis to update.
        analysis_update (AnalysisUpdate): The fields to update (name, origin, classes).

    Returns:
        bool: True if the update was successful, False if the analysis was not found.

    Raises:
        ValueError: If the new class list contains duplicate class IDs.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        name = analysis_update.name
        origin = analysis_update.origin.value if analysis_update.origin else None
        classes = [c.model_dump() for c in analysis_update.classes] if analysis_update.classes else None

        analysis_exists = cursor.execute("SELECT 1 FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
        if analysis_exists is None:
            return False
        if name is not None:
            cursor.execute("UPDATE analyses SET name = ? WHERE id = ?", (name, analysis_id))

        if origin is not None:
            cursor.execute("UPDATE analyses SET origin_id = ? WHERE id = ?", (origin, analysis_id))

        if classes is not None:
            cursor.execute("DELETE FROM analysis_classes WHERE analysis_id = ?", (analysis_id,))
            classes_data = [(analysis_id, c["class_id"], c["instances"]) for c in classes]
            cursor.executemany(
                "INSERT INTO analysis_classes (analysis_id, class_id, instances) VALUES (?, ?, ?)",
                classes_data,
            )

        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise ValueError(f"Integrity error: Duplicate class detected in update list. {e}") from e
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def delete_analysis(analysis_id: int) -> bool:
    """
    Deletes an analysis record and its dependencies.

    Args:
        analysis_id (int): The ID of the analysis to delete.

    Returns:
        bool: True if a record was deleted, False otherwise.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        return False
    finally:
        conn.close()
