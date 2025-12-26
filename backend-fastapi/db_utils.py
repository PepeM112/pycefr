import sqlite3
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from models.analysis import AnalysisCreate, AnalysisUpdate
from models.common import Level, Origin
from models.class_model import ClassID
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
        page (int): The current page number.
        per_page (int): The number of records to retrieve per page.

    Returns:
        Tuple[List[dict], int]: A tuple containing the list of analyses and the total count.
    """

    # TODO


def get_analysis_details(analysis_id: int) -> Optional[dict]:
    """
    Fetches a complete analysis including its nested code classes.

    Args:
        analysis_id (int): The unique identifier of the analysis.

    Returns:
        Optional[dict]: The analysis data if found, None otherwise.
    """

    # TODO


def insert_full_analysis(name: str, origin: int, classes: List[Dict]) -> Optional[int]:
    """
    Inserts a new analysis in a single transaction.

    Args:
        data (AnalysisCreate): The Pydantic model containing analysis data.

    Returns:
        Optional[int]: The ID of the newly created analysis, or None if the operation failed.
    """

    # TODO


def update_analysis(analysis_id: int, name: Optional[str], origin: Optional[int], classes: Optional[List[Dict]] = None) -> bool:
    """
    Updates an existing analysis record.

    Args:
        analysis_id (int): The ID of the analysis to update.
        data (AnalysisUpdate): The Pydantic model containing updated fields.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    with get_db_connection() as conn:
        cursor = conn.execute(
            "UPDATE analyses SET name = ?, origin_id = ? WHERE id = ?",
            (name, origin, analysis_id)
        )
        conn.commit()
        # cursor.rowcount devuelve el número de filas modificadas
        return cursor.rowcount > 0


def delete_analysis(analysis_id: int) -> bool:
    """
    Deletes an analysis record and its dependencies.

    Args:
        analysis_id (int): The ID of the analysis to delete.

    Returns:
        bool: True if a record was deleted, False otherwise.
    """

    # TODO
