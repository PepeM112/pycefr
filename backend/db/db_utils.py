import logging
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator, List, Optional, Tuple

from backend.models.schemas.analysis import (
    AnalysisClassPublic,
    AnalysisCreate,
    AnalysisFilePublic,
    AnalysisFilters,
    AnalysisPublic,
    AnalysisSortColumn,
    AnalysisStatus,
    AnalysisSummaryPublic,
)
from backend.models.schemas.class_model import ClassId
from backend.models.schemas.common import EntityLabelString, Origin, SortDirection, Sorting
from backend.models.schemas.repo import (
    GitHubContributorPublic,
    GitHubUserPublic,
    RepoCommitPublic,
    RepoPublic,
    RepoSummaryPublic,
)

logger = logging.getLogger(__name__)
DATABASE_PATH = os.getenv("DATABASE_PATH", "database/pycefr.db")


class AnalysisRepository:

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Row → Model mappers
    # ------------------------------------------------------------------

    @staticmethod
    def _map_owner(row: sqlite3.Row) -> GitHubUserPublic:
        return GitHubUserPublic(
            name=row["repo_owner_name"] or "",
            github_user=row["repo_owner_login"] or "Unknown",
            avatar=row["repo_owner_avatar"] or "",
            profile_url=(
                (row["repo_owner_profile_url"] or f"https://github.com/{row['repo_owner_login']}")
                if row["repo_owner_login"]
                else ""
            ),
        )

    @staticmethod
    def _map_commit(row: sqlite3.Row) -> RepoCommitPublic:
        return RepoCommitPublic(
            username=row["username"],
            github_user=row["github_user"],
            loc=row["loc"],
            commits=row["commits"],
            estimated_hours=row["estimated_hours"],
            total_files_modified=row["total_files_modified"],
        )

    @staticmethod
    def _map_contributor(row: sqlite3.Row) -> GitHubContributorPublic:
        return GitHubContributorPublic(
            name=row["name"],
            github_user=row["github_user"],
            avatar=row["avatar"],
            profile_url=row["profile_url"],
            contributions=row["contributions"],
        )

    @staticmethod
    def _parse_dt(value: str | None) -> datetime | None:
        return datetime.fromisoformat(value) if value else None

    # ------------------------------------------------------------------
    # Shared write helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _insert_files(cursor: sqlite3.Cursor, analysis_id: int, files: List[AnalysisFilePublic]) -> None:
        for file in files:
            cursor.execute(
                "INSERT INTO analysis_files (analysis_id, filename) VALUES (?, ?)", (analysis_id, file.filename)
            )
            file_id = cursor.lastrowid
            if file.classes:
                cursor.executemany(
                    "INSERT INTO analysis_file_classes (file_id, class_id, instances) VALUES (?, ?, ?)",
                    [(file_id, cls.class_id.value, cls.instances) for cls in file.classes],
                )

    @staticmethod
    def _insert_commits(cursor: sqlite3.Cursor, analysis_id: int, commits: List[RepoCommitPublic]) -> None:
        if not commits:
            return
        cursor.executemany(
            """
            INSERT INTO repo_commits
            (analysis_id, username, github_user, loc, commits, estimated_hours, total_files_modified)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (analysis_id, c.username, c.github_user, c.loc, c.commits, c.estimated_hours, c.total_files_modified)
                for c in commits
            ],
        )

    @staticmethod
    def _insert_contributors(
        cursor: sqlite3.Cursor, analysis_id: int, contributors: List[GitHubContributorPublic]
    ) -> None:
        if not contributors:
            return
        cursor.executemany(
            """
            INSERT INTO repo_contributors
            (analysis_id, name, github_user, avatar, profile_url, contributions)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [(analysis_id, c.name, c.github_user, c.avatar, c.profile_url, c.contributions) for c in contributors],
        )

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_analyses(
        self,
        page: int,
        per_page: int,
        sorting: Sorting | None = None,
        filters: AnalysisFilters | None = None,
    ) -> Tuple[List[AnalysisSummaryPublic], int]:
        offset = (page - 1) * per_page

        column_map = {
            AnalysisSortColumn.ID: "id",
            AnalysisSortColumn.NAME: "name",
            AnalysisSortColumn.STATUS: "status",
            AnalysisSortColumn.CREATED_AT: "created_at",
        }

        sort_column = column_map[AnalysisSortColumn.ID]
        sort_dir = SortDirection.DESC.name

        if sorting and sorting.column:
            if sorting.column in column_map:
                sort_column = column_map[sorting.column]
                if sorting.direction in [SortDirection.ASC, SortDirection.DESC]:
                    sort_dir = sorting.direction.name
                else:
                    sort_dir = "DESC"

        where_clauses = ["status != 'deleted'"]
        params: List[Any] = []

        if filters:
            if filters.name:
                name_conditions = " OR ".join(["name LIKE ?" for _ in filters.name])
                where_clauses.append(f"({name_conditions})")
                params.extend([f"%{n}%" for n in filters.name])

            if filters.owner:
                placeholders = ",".join(["?" for _ in filters.owner])
                where_clauses.append(f"repo_owner_login IN ({placeholders})")
                params.extend(filters.owner)

            if filters.status:
                placeholders = ",".join("?" * len(filters.status))
                where_clauses.append(f"status IN ({placeholders})")
                params.extend(filters.status)

            if filters.date_from:
                where_clauses.append("created_at >= ?")
                params.append(filters.date_from.isoformat())

            if filters.date_to:
                where_clauses.append("created_at <= ?")
                params.append(filters.date_to.isoformat())

        where_sql = " AND ".join(where_clauses)

        with self._connect() as conn:
            cursor = conn.cursor()
            rows = cursor.execute(
                f"SELECT * FROM analyses WHERE {where_sql} ORDER BY {sort_column} {sort_dir} LIMIT ? OFFSET ?",
                params + [per_page, offset],
            ).fetchall()

            total = cursor.execute(f"SELECT COUNT(*) FROM analyses WHERE {where_sql}", params).fetchone()[0]

            return [
                AnalysisSummaryPublic(
                    id=row["id"],
                    name=row["name"],
                    status=AnalysisStatus(row["status"]),
                    error_message=row["error_message"],
                    origin=Origin(row["origin"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    repo=RepoSummaryPublic(
                        name=row["repo_name"],
                        url=row["repo_url"],
                        description=row["repo_description"],
                        created_at=self._parse_dt(row["repo_created_at"]),
                        last_updated_at=self._parse_dt(row["repo_last_update"]),
                        owner=self._map_owner(row),
                    ),
                )
                for row in rows
            ], total

    def get_analysis_details(self, analysis_id: int) -> Optional[AnalysisPublic]:
        with self._connect() as conn:
            cursor = conn.cursor()
            row = cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
            if not row:
                return None

            file_rows = cursor.execute(
                """
                SELECT f.filename, c.class_id, c.instances
                FROM analysis_files f
                LEFT JOIN analysis_file_classes c ON f.id = c.file_id
                WHERE f.analysis_id = ?
                """,
                (analysis_id,),
            ).fetchall()

            files_map: dict[str, AnalysisFilePublic] = {}
            for r in file_rows:
                fname = r["filename"]
                if fname not in files_map:
                    files_map[fname] = AnalysisFilePublic(filename=fname, classes=[])
                if r["class_id"]:
                    files_map[fname].classes.append(
                        AnalysisClassPublic(class_id=ClassId(r["class_id"]), instances=r["instances"])
                    )

            commits = [
                self._map_commit(r)
                for r in cursor.execute("SELECT * FROM repo_commits WHERE analysis_id = ?", (analysis_id,)).fetchall()
            ]
            contributors = [
                self._map_contributor(r)
                for r in cursor.execute(
                    "SELECT * FROM repo_contributors WHERE analysis_id = ?", (analysis_id,)
                ).fetchall()
            ]

            owner = self._map_owner(row)

            return AnalysisPublic(
                id=row["id"],
                name=row["name"],
                origin=Origin(row["origin"]),
                status=AnalysisStatus(row["status"]),
                error_message=row["error_message"],
                created_at=datetime.fromisoformat(row["created_at"]),
                file_classes=list(files_map.values()),
                repo=RepoPublic(
                    name=row["repo_name"],
                    url=row["repo_url"],
                    description=row["repo_description"],
                    created_at=self._parse_dt(row["repo_created_at"]) or datetime.now(),
                    last_updated_at=self._parse_dt(row["repo_last_update"]) or datetime.now(),
                    owner=owner,
                    commits=commits,
                    contributors=contributors,
                ),
            )

    def get_unique_owners(
        self, search_query: str | None = None, limit: int | None = None
    ) -> List[EntityLabelString]:
        with self._connect() as conn:
            cursor = conn.cursor()
            query = """
                SELECT DISTINCT
                repo_owner_login AS id,
                COALESCE(repo_owner_name, repo_owner_login) AS label
                FROM analyses
                WHERE repo_owner_login IS NOT NULL
            """
            params: List[str] = []

            if search_query:
                query += " AND (repo_owner_login LIKE ? OR repo_owner_name LIKE ?)"
                search_param = f"%{search_query}%"
                params.extend([search_param, search_param])

            query += " ORDER BY label"

            if limit is not None:
                query += " LIMIT ?"
                params.append(str(limit))

            try:
                rows = cursor.execute(query, params).fetchall()
                return [EntityLabelString(id=row["id"], label=row["label"]) for row in rows]
            except sqlite3.Error as e:
                logger.error(f"Database error while fetching unique owners: {e}")
                return []

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def create_empty_analysis(self, analysis: AnalysisCreate) -> AnalysisPublic | None:
        repo_name = analysis.repo_url.rstrip("/").split("/")[-1] or "unknown"
        now_utc = datetime.now(timezone.utc)
        name = analysis.name or f"{now_utc.strftime('%Y%m%d')}_{repo_name}"

        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO analyses (name, status, origin, repo_url, created_at) VALUES (?, ?, ?, ?, ?)",
                    (name, AnalysisStatus.IN_PROGRESS.value, Origin.GITHUB.value,
                     analysis.repo_url, now_utc.isoformat()),
                )
                conn.commit()
                analysis_id = cursor.lastrowid

                if analysis_id is None:
                    raise sqlite3.Error("Failed to retrieve lastrowid after INSERT")

                logger.info(f"Empty analysis record created with ID: {analysis_id} for repo: {analysis.repo_url}")
                return AnalysisPublic(
                    id=analysis_id,
                    name=name,
                    status=AnalysisStatus.IN_PROGRESS,
                    origin=Origin.GITHUB,
                    created_at=now_utc,
                    file_classes=[],
                    repo=RepoPublic(url=analysis.repo_url, name=repo_name, owner=None, commits=[], contributors=[]),
                )
        except sqlite3.Error as e:
            logger.error(f"Database error while creating empty analysis: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating initial analysis: {e}")
            return None

    def update_analysis_results(self, analysis_id: int, analysis_data: AnalysisPublic) -> None:
        with self._connect() as conn:
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
                        analysis_data.status.value,
                        analysis_data.repo.name,
                        analysis_data.repo.description,
                        analysis_data.repo.owner.name if analysis_data.repo.owner else None,
                        analysis_data.repo.owner.github_user if analysis_data.repo.owner else None,
                        analysis_data.repo.owner.avatar if analysis_data.repo.owner else None,
                        analysis_data.repo.created_at.isoformat() if analysis_data.repo.created_at else None,
                        analysis_data.repo.last_updated_at.isoformat() if analysis_data.repo.last_updated_at else None,
                        sum(c.estimated_hours for c in analysis_data.repo.commits),
                        analysis_id,
                    ),
                )

                self._insert_files(cursor, analysis_id, analysis_data.file_classes or [])
                self._insert_commits(cursor, analysis_id, analysis_data.repo.commits)
                self._insert_contributors(cursor, analysis_id, analysis_data.repo.contributors)

                conn.commit()
            except Exception as e:
                conn.rollback()
                self.mark_analysis_as_failed(analysis_id, f"Database update error: {str(e)}")
                raise

    def delete_analysis(self, analysis_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE analyses SET status = 'deleted' WHERE id = ?", (analysis_id,))
            conn.commit()
            return cursor.rowcount > 0

    def mark_analysis_as_failed(self, analysis_id: int, error_message: str = "") -> None:
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE analyses SET status = ?, error_message = ? WHERE id = ?",
                    (AnalysisStatus.FAILED.value, error_message, analysis_id),
                )
                conn.commit()
                logger.info(f"Analysis {analysis_id} marked as FAILED. Reason: {error_message}")
        except sqlite3.Error as e:
            logger.error(f"Database error while marking analysis {analysis_id} as failed: {e}")

    def upload_analysis_data(self, analysis_data: AnalysisPublic) -> AnalysisPublic | None:
        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                status_to_save = analysis_data.status
                if status_to_save == AnalysisStatus.DELETED:
                    status_to_save = AnalysisStatus.COMPLETED

                repo = analysis_data.repo
                cursor.execute(
                    """
                    INSERT INTO analyses (
                        name, status, origin, repo_url, repo_name, repo_description,
                        repo_owner_name, repo_owner_login, repo_owner_avatar, repo_owner_profile_url,
                        repo_created_at, repo_last_update, estimated_hours, error_message, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        analysis_data.name,
                        status_to_save.value,
                        Origin.LOCAL.value,
                        repo.url if repo else None,
                        repo.name if repo else None,
                        repo.description if repo else None,
                        repo.owner.name if repo and repo.owner else None,
                        repo.owner.github_user if repo and repo.owner else None,
                        repo.owner.avatar if repo and repo.owner else None,
                        repo.owner.profile_url if repo and repo.owner else None,
                        repo.created_at.isoformat() if repo and repo.created_at else None,
                        repo.last_updated_at.isoformat() if repo and repo.last_updated_at else None,
                        sum(c.estimated_hours for c in repo.commits) if repo else 0,
                        analysis_data.error_message,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                new_analysis_id = cursor.lastrowid

                if not new_analysis_id:
                    raise sqlite3.Error("Failed to get new ID for imported analysis")

                if analysis_data.file_classes:
                    self._insert_files(cursor, new_analysis_id, analysis_data.file_classes)

                if repo:
                    self._insert_commits(cursor, new_analysis_id, repo.commits)
                    self._insert_contributors(cursor, new_analysis_id, repo.contributors)

                conn.commit()
                analysis_data.id = new_analysis_id
                analysis_data.origin = Origin.LOCAL
                return analysis_data

            except Exception as e:
                conn.rollback()
                logger.error(f"Error uploading analysis: {e}")
                raise


# ---------------------------------------------------------------------------
# Module-level API (delegates to a default repository instance)
# ---------------------------------------------------------------------------

_repo = AnalysisRepository()


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_analyses(
    page: int, per_page: int, sorting: Sorting | None = None, filters: AnalysisFilters | None = None
) -> Tuple[List[AnalysisSummaryPublic], int]:
    return _repo.get_analyses(page, per_page, sorting, filters)


def get_analysis_details(analysis_id: int) -> Optional[AnalysisPublic]:
    return _repo.get_analysis_details(analysis_id)


def create_empty_analysis(analysis: AnalysisCreate) -> AnalysisPublic | None:
    return _repo.create_empty_analysis(analysis)


def update_analysis_results(analysis_id: int, analysis_data: AnalysisPublic) -> None:
    _repo.update_analysis_results(analysis_id, analysis_data)


def delete_analysis(analysis_id: int) -> bool:
    return _repo.delete_analysis(analysis_id)


def mark_analysis_as_failed(analysis_id: int, error_message: str = "") -> None:
    _repo.mark_analysis_as_failed(analysis_id, error_message)


def get_unique_owners(search_query: str | None = None, limit: int | None = None) -> List[EntityLabelString]:
    return _repo.get_unique_owners(search_query, limit)


def upload_analysis_data(analysis_data: AnalysisPublic) -> AnalysisPublic | None:
    return _repo.upload_analysis_data(analysis_data)
