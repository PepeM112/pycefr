import logging
import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple

from backend.constants.analysis_rules import get_class_level
from backend.models.schemas.analysis import (
    Analysis,
    AnalysisClass,
    AnalysisCreate,
    AnalysisSummary,
)
from backend.models.schemas.class_model import ClassId
from backend.models.schemas.common import Origin
from backend.models.schemas.repo import (
    GitHubContributor,
    GitHubUser,
    Repo,
    RepoCommit,
    RepoSummary,
)

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


def get_analyses(page: int, per_page: int) -> Tuple[List[AnalysisSummary], int]:
    """
    Retrieves a paginated list of analysis summaries.

    Args:
        page (int): The current page number (starts at 1).
        per_page (int): The number of records to retrieve per page.

    Returns:
        Tuple[List[AnalysisSummary], int]: A list of analyses and the total count.

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

        analyses: List[AnalysisSummary] = []
        for row in rows:
            analyses.append(
                AnalysisSummary(
                    id=row["id"],
                    name=row["name"],
                    status=row["status"],
                    origin=Origin(row["origin_id"]),
                    repo_name=row["repo_name"],
                    repo_url=row["repo_url"],
                    created_at=datetime.fromisoformat(row["created_at"].replace(" ", "T")),
                    estimated_hours=row["total_hours"],
                )
            )

        return analyses, total
    except sqlite3.Error as e:
        logger.error(f"Error fetching analyses list: {e}")
        raise
    finally:
        conn.close()


def get_analysis_details(analysis_id: int) -> Analysis | None:
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

        # Analysis
        analysis_row = cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,)).fetchone()

        if analysis_row is None:
            return None

        # Analysis Classes
        classes_rows = cursor.execute(
            "SELECT class_id, instances FROM analysis_class WHERE analysis_id = ?",
            (analysis_id,),
        ).fetchall()

        classes = [_map_row_to_class(row) for row in classes_rows]

        # Analysis Repo Info
        repo_data_row = cursor.execute(
            "SELECT * FROM repo_general_info WHERE analysis_id = ?", (analysis_id,)
        ).fetchone()
        repo_data = _map_row_to_repo_info_data(repo_data_row) if repo_data_row else None

        if not repo_data:
            return Analysis(
                status=analysis_row["status"],
                file_classes=[],
                repo=None,
            )
        repo_commits_row = cursor.execute(
            "SELECT * FROM repo_commit_stats WHERE analysis_id = ?", (analysis_id,)
        ).fetchall()
        repo_commits = [_map_row_to_repo_commit(row) for row in repo_commits_row]

        repo_contributors_row = cursor.execute(
            "SELECT * FROM repo_contributors WHERE analysis_id = ?", (analysis_id,)
        ).fetchall()
        repo_contributors = [_map_row_to_repo_contributor(row) for row in repo_contributors_row]

        repo_info = (
            Repo(
                name = 
                data=repo_info_data,
                commits=repo_commits,
                contributors=repo_contributors,
            )
            if repo_info_data
            else None
        )

        analysis_result = AnalysisResult(elements={"classes": classes})
        if repo_info:
            return FullAnalysisResult(
                elements={"classes": classes},
                repo_info=repo_info,
            )
        return analysis_result

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
            (analysis.name, analysis.origin.value, analysis.total_hours),
        )
        analysis_id = cursor.lastrowid

        classes_data = [(analysis_id, c.class_id.value, c.instances) for c in analysis.classes]

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
                "UPDATE analyses SET origin_id = ? WHERE id = ?", (analysis_update.origin.value, analysis_id)
            )

        if analysis_update.classes is not None:
            cursor.execute("DELETE FROM analysis_class WHERE analysis_id = ?", (analysis_id,))
            classes_data = [(analysis_id, c.class_id.value, c.instances) for c in analysis_update.classes]
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


def _map_row_to_class(row: sqlite3.Row) -> AnalysisClass:
    try:
        class_id_enum = ClassId(row["class_id"])
    except ValueError:
        class_id_enum = ClassId.UNKNOWN

    return AnalysisClass(class_id=class_id_enum, instances=row["instances"], level=get_class_level(class_id_enum))


def _map_row_to_repo_info_data(row: sqlite3.Row) -> RepoSummary:
    try:
        return RepoSummary(
            name=row["name"],
            url=row["url"],
            description=row["description"],
            created_at=row["created_at"],
            last_updated_at=row["last_updated_at"],
            owner=GitHubUser(
                name=row["owner_name"],
                github_user=row["owner_github_user"],
                avatar=row["owner_avatar"],
                profile_url=row["owner_profile_url"],
                commits=row["owner_commits"],
            ),
        )
    except ValueError as e:
        logger.error(f"Error mapping row to RepoInfo: {e}")
        raise


def _map_row_to_repo_commit(row: sqlite3.Row) -> RepoCommit:
    return RepoCommit(
        username=row["username"],
        github_user=row["github_user"],
        loc=row["loc"],
        commits=row["commits"],
        estimated_hours=row["estimated_hours"],
        total_files_modified=row["total_files_modified"],
    )


def _map_row_to_repo_contributor(row: sqlite3.Row) -> GitHubContributor:
    return GitHubContributor(
        name=row["name"],
        github_user=row["github_user"],
        avatar=row["avatar"],
        profile_url=row["profile_url"],
        contributions=row["contributions"],
    )
