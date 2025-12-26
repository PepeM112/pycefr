import sqlite3
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from models.analysis import AnalysisCreate, AnalysisUpdate
from models.common import Level, Origin
from models.class_model import ClassId
from config.analysis_map import CODE_CLASS_DETAILS

DATABASE_PATH = 'database/pycefr.db'


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
def get_analyses(page: int, per_page: int) -> Tuple[List[dict], int]:
    """
    Retrieves a paginated list of analysis summaries.

    Args:
        page (int): The current page number (starts at 1).
        per_page (int): The number of records to retrieve per page.

    Returns:
        Tuple[List[dict], int]: A tuple containing:
            - A list of dictionaries with analysis headers.
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
            (per_page, offset)
        ).fetchall()

        total = cursor.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]

        analyses = []
        for row in rows:
            analyses.append({
                "id": row["id"],
                "name": row["name"],
                "origin": Origin(row["origin_id"]),
                "created_at": datetime.fromisoformat(row["created_at"]).replace(" ", "T")
            })

        return analyses, total
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        return [], 0
    finally:
        conn.close()


def get_analysis_details(analysis_id: int) -> Optional[dict]:
    """
    Fetches a complete analysis including its nested code classes.

    Args:
        analysis_id (int): The unique identifier of the analysis.

    Returns:
        Optional[dict]: The analysis data if found, None otherwise.
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
            (analysis_id,)
        ).fetchone()

        if analysis_row is None:
            return None

        classes_rows = cursor.execute(
            """
            SELECT class_id, instances
            FROM analysis_class
            WHERE analysis_id = ?
            """,
            (analysis_id,)
        ).fetchall()

        classes = []
        for c_row in classes_rows:
            cid_value = c_row["class_id"]
            try:
                class_id_enum = ClassId(cid_value)
            except ValueError:
                class_id_enum = ClassId.UNKNOWN
            classes.append({
                "class_id": class_id_enum,
                "instances": c_row["instances"],
                "level": Level.CODE_CLASS_DETAILS.get(class_id_enum, Level.UNKNOWN)
            })

        analysis = {
            "id": analysis_row["id"],
            "name": analysis_row["name"],
            "origin": Origin(analysis_row["origin_id"]),
            "created_at": datetime.fromisoformat(analysis_row["created_at"]).replace(" ", "T"),
            "classes": classes
        }

        return analysis
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        return None
    finally:
        conn.close()


def insert_full_analysis(name: str, origin: int, classes: List[Dict]) -> Optional[int]:
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
        cursor.execute(
            "INSERT INTO analyses (name, origin_id) VALUES (?, ?)", (name, origin))
        analysis_id = cursor.lastrowid

        classes_data = [(analysis_id, c['class_id'], c['instances'])
                        for c in classes]
        cursor.executemany(
            "INSERT INTO analysis_classes (analysis_id, class_id, instances) VALUES (?, ?, ?)",
            classes_data
        )
        conn.commit()
        return analysis_id
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise ValueError(
            f"Integrity error: Duplicate class detected or foreign key violation. Details: {e}")
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def update_analysis(analysis_id: int, name: Optional[str], origin: Optional[int], classes: Optional[List[Dict]] = None) -> bool:
    """
    Updates an analysis record and replaces its associated classes.

    Args:
        analysis_id (int): The ID of the analysis to update.
        name (Optional[str]): New name for the analysis.
        origin (Optional[int]): New origin ID.
        classes (Optional[List[Dict]]): New list of classes to replace old ones.

    Returns:
        bool: True if the update was successful, False if the analysis was not found.

    Raises:
        ValueError: If the new class list contains duplicate class IDs.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        analysis_exists = cursor.execute(
            "SELECT 1 FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
        if analysis_exists is None:
            return False
        if name is not None:
            cursor.execute(
                "UPDATE analyses SET name = ? WHERE id = ?", (name, analysis_id))

        if origin is not None:
            cursor.execute(
                "UPDATE analyses SET origin_id = ? WHERE id = ?", (origin, analysis_id))

        if classes is not None:
            cursor.execute(
                "DELETE FROM analysis_classes WHERE analysis_id = ?", (analysis_id,))
            classes_data = [(analysis_id, c['class_id'], c['instances'])
                            for c in classes]
            cursor.executemany(
                "INSERT INTO analysis_classes (analysis_id, class_id, instances) VALUES (?, ?, ?)",
                classes_data
            )

        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise ValueError(
            f"Integrity error: Duplicate class detected in update list. {e}")
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
        cursor.execute(
            "DELETE FROM analyses WHERE id = ?", (analysis_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        return False
    finally:
        conn.close()
