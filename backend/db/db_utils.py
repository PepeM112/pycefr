import logging
import os
import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple

from backend.models.schemas.analysis import (
    AnalysisClassPublic,
    AnalysisFilePublic,
    AnalysisPublic,
    AnalysisStatus,
    AnalysisSummaryPublic,
)
from backend.models.schemas.class_model import ClassId
from backend.models.schemas.common import Origin
from backend.models.schemas.repo import (
    GitHubContributorPublic,
    GitHubUserPublic,
    RepoCommitPublic,
    RepoPublic,
    RepoSummaryPublic,
)

logger = logging.getLogger(__name__)
DATABASE_PATH = os.getenv("DATABASE_PATH", "database/pycefr.db")


def get_db_connection() -> sqlite3.Connection:
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.OperationalError as e:
        logger.critical(f"Failed to connect to database: {e}")
        raise


# --- READ OPERATIONS ---


def get_analyses(page: int, per_page: int) -> Tuple[List[AnalysisSummaryPublic], int]:
    offset = (page - 1) * per_page
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        rows = cursor.execute(
            """
            SELECT * FROM analyses
            ORDER BY created_at DESC LIMIT ? OFFSET ?
            """,
            (per_page, offset),
        ).fetchall()

        total = cursor.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
        analyses: List[AnalysisSummaryPublic] = []

        for row in rows:
            owner = GitHubUserPublic(
                name=row["repo_owner_name"],
                github_user=row["repo_owner_login"] or "Unknown",
                avatar=row["repo_owner_avatar"] or "",
                profile_url=row["repo_owner_profile_url"] or "",
            )

            repo_summary = RepoSummaryPublic(
                name=row["repo_name"],
                url=row["repo_url"],
                description=row["repo_description"],  # Puede ser None, y el Schema lo permite
                created_at=datetime.fromisoformat(row["created_at"]),
                last_updated_at=datetime.fromisoformat(row["created_at"]),
                owner=owner,
            )

            analyses.append(
                AnalysisSummaryPublic(
                    id=row["id"],
                    name=row["name"],
                    status=AnalysisStatus(row["status"]),
                    origin=Origin(row["origin"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    repo=repo_summary,
                )
            )
        return analyses, total
    finally:
        conn.close()


def get_analysis_details(analysis_id: int) -> Optional[AnalysisPublic]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        row = cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
        if not row:
            return None

        # Reconstruir estructura de archivos y clases
        file_rows = cursor.execute(
            """
            SELECT f.filename, c.class_id, c.instances
            FROM analysis_files f
            LEFT JOIN analysis_file_classes c ON f.id = c.file_id
            WHERE f.analysis_id = ?
            """,
            (analysis_id,),
        ).fetchall()

        files_list: List[AnalysisFilePublic] = []
        current_file = None

        for r in file_rows:
            if current_file is None or current_file.filename != r["filename"]:
                current_file = next((f for f in files_list if f.filename == r["filename"]), None)

                if not current_file:
                    current_file = AnalysisFilePublic(filename=r["filename"], classes=[])
                    files_list.append(current_file)

            if r["class_id"]:
                current_file.classes.append(
                    AnalysisClassPublic(
                        class_id=ClassId(r["class_id"]),
                        instances=r["instances"],
                    )
                )

        commits = [
            _map_row_to_repo_commit(r)
            for r in cursor.execute("SELECT * FROM repo_commits WHERE analysis_id = ?", (analysis_id,)).fetchall()
        ]

        contributors = [
            _map_row_to_repo_contributor(r)
            for r in cursor.execute("SELECT * FROM repo_contributors WHERE analysis_id = ?", (analysis_id,)).fetchall()
        ]

        repo = RepoPublic(
            name=row["repo_name"],
            url=row["repo_url"],
            description=row["repo_description"],
            created_at=datetime.fromisoformat(row["repo_created_at"]) if row["repo_created_at"] else datetime.now(),
            last_updated_at=datetime.fromisoformat(row["repo_last_update"])
            if row["repo_last_update"]
            else datetime.now(),
            owner=GitHubUserPublic(
                name=row["repo_owner_name"] or "",
                github_user=row["repo_owner_login"] or "",
                avatar=row["repo_owner_avatar"] or "",
                profile_url=f"https://github.com/{row['repo_owner_login']}" if row["repo_owner_login"] else "",
            ),
            commits=commits,
            contributors=contributors,
        )

        return AnalysisPublic(
            id=row["id"],
            name=row["name"],
            origin=Origin(row["origin"]),
            status=AnalysisStatus(row["status"]),
            error_message=row["error_message"],
            created_at=datetime.fromisoformat(row["created_at"]),
            file_classes=files_list,
            repo=repo,
        )
    finally:
        conn.close()


# --- WRITE OPERATIONS ---


def create_empty_analysis(repo_url: str) -> int | None:
    """Crea el registro inicial en estado IN_PROGRESS."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        repo_name = repo_url.rstrip("/").split("/")[-1]
        name = f"{datetime.now().strftime('%Y%m%d')}_{repo_name}"

        cursor.execute(
            "INSERT INTO analyses (name, status, origin, repo_url) VALUES (?, ?, ?, ?)",
            (name, AnalysisStatus.IN_PROGRESS.value, Origin.GITHUB.value, repo_url),
        )
        conn.commit()
        analysis_id = cursor.lastrowid
        logger.info(f"Created initial analysis record with ID {analysis_id} for {repo_url}")
        return analysis_id
    except sqlite3.Error as e:
        logger.error(f"Database error while creating empty analysis: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error creating initial analysis: {e}")
        return None
    finally:
        conn.close()


def update_analysis_results(analysis_id: int, analysis_data: AnalysisPublic) -> None:
    """Actualiza un análisis existente con los resultados finales."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if analysis_data.repo is None:
            raise ValueError("Cannot update analysis results: repo data is None")

        cursor.execute(
            """
            UPDATE analyses SET
                status = ?, repo_name = ?, repo_description = ?,
                repo_owner_name = ?, repo_owner_login = ?,
                repo_owner_avatar = ?, repo_created_at = ?,
                repo_last_update = ?, estimated_hours = ?
            WHERE id = ?
            """,
            (
                analysis_data.status,
                analysis_data.repo.name,
                analysis_data.repo.description,
                analysis_data.repo.owner.name,
                analysis_data.repo.owner.github_user,
                analysis_data.repo.owner.avatar,
                analysis_data.repo.created_at.isoformat(),
                analysis_data.repo.last_updated_at.isoformat(),
                sum(c.estimated_hours for c in analysis_data.repo.commits),
                analysis_id,
            ),
        )

        for file in analysis_data.file_classes or []:
            cursor.execute(
                "INSERT INTO analysis_files (analysis_id, filename) VALUES (?, ?)", (analysis_id, file.filename)
            )
            file_id = cursor.lastrowid

            for cls in file.classes:
                cursor.execute(
                    "INSERT INTO analysis_file_classes (file_id, class_id, instances) VALUES (?, ?, ?)",
                    (file_id, cls.class_id.value, cls.instances),
                )

        # Inserción de Commits
        cursor.executemany(
            """
            INSERT INTO repo_commits
            (analysis_id, username, github_user, loc, commits, estimated_hours, total_files_modified)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    analysis_id,
                    commit.username,
                    commit.github_user,
                    commit.loc,
                    commit.commits,
                    commit.estimated_hours,
                    commit.total_files_modified,
                )
                for commit in analysis_data.repo.commits
            ],
        )

        # Inserción de Contributors
        cursor.executemany(
            """
            INSERT INTO repo_contributors
            (analysis_id, name, github_user, avatar, profile_url, contributions)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    analysis_id,
                    contributor.name,
                    contributor.github_user,
                    contributor.avatar,
                    contributor.profile_url,
                    contributor.contributions,
                )
                for contributor in analysis_data.repo.contributors
            ],
        )

        conn.commit()
    except Exception as e:
        conn.rollback()
        mark_analysis_as_failed(analysis_id, f"Database update error: {str(e)}")
        raise
    finally:
        conn.close()


def delete_analysis(analysis_id: int) -> bool:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def mark_analysis_as_failed(analysis_id: int, error_message: str = "") -> None:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE analyses SET status = ? WHERE id = ?",
            (AnalysisStatus.FAILED.value, analysis_id),
        )
        conn.commit()
        logger.info(f"Analysis {analysis_id} marked as FAILED. Reason: {error_message}")
    except sqlite3.Error as e:
        logger.error(f"Database error while marking analysis {analysis_id} as failed: {e}")
    finally:
        conn.close()


# --- HELPERS ---


def _map_row_to_repo_commit(row: sqlite3.Row) -> RepoCommitPublic:
    return RepoCommitPublic(
        username=row["username"],
        github_user=row["github_user"],
        loc=row["loc"],
        commits=row["commits"],
        estimated_hours=row["estimated_hours"],
        total_files_modified=row["total_files_modified"],
    )


def _map_row_to_repo_contributor(row: sqlite3.Row) -> GitHubContributorPublic:
    return GitHubContributorPublic(
        name=row["name"],
        github_user=row["github_user"],
        avatar=row["avatar"],
        profile_url=row["profile_url"],
        contributions=row["contributions"],
    )
