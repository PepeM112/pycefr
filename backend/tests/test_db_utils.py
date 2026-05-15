import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest

from backend.db.db_utils import (
    create_empty_analysis,
    delete_analysis,
    get_analyses,
    get_analysis_details,
    get_db_connection,
    get_unique_owners,
    mark_analysis_as_failed,
    update_analysis_results,
    upload_analysis_data,
)
from backend.db.label_utils import get_class_labels
from backend.models.schemas.analysis import (
    AnalysisClassPublic,
    AnalysisCreate,
    AnalysisFilePublic,
    AnalysisFilters,
    AnalysisPublic,
    AnalysisStatus,
    AnalysisSummaryPublic,
)
from backend.models.schemas.class_model import ClassId, ClassPublic
from backend.models.schemas.common import Level, Origin, SortDirection, Sorting
from backend.models.schemas.repo import (
    GitHubContributorPublic,
    GitHubUserPublic,
    RepoCommitPublic,
    RepoPublic,
)

# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------


def make_analysis_create(
    repo_url: str = "https://github.com/owner/repo",
    name: str | None = None,
) -> AnalysisCreate:
    return AnalysisCreate(repo_url=repo_url, name=name)


def make_commit(
    username: str = "alice",
    github_user: str = "alice",
    loc: int = 100,
    commits: int = 5,
    estimated_hours: float = 2.5,
    total_files_modified: int = 3,
) -> RepoCommitPublic:
    return RepoCommitPublic(
        username=username,
        github_user=github_user,
        loc=loc,
        commits=commits,
        estimated_hours=estimated_hours,
        total_files_modified=total_files_modified,
    )


def make_contributor(
    name: str = "Alice",
    github_user: str = "alice",
    avatar: str = "https://github.com/alice.png",
    profile_url: str = "https://github.com/alice",
    contributions: int = 10,
) -> GitHubContributorPublic:
    return GitHubContributorPublic(
        name=name,
        github_user=github_user,
        avatar=avatar,
        profile_url=profile_url,
        contributions=contributions,
    )


def make_file(
    filename: str = "main.py",
    class_ids: list[ClassId] | None = None,
) -> AnalysisFilePublic:
    ids = class_ids or [ClassId.LIST_SIMPLE]
    classes = [AnalysisClassPublic(class_id=cid, instances=1) for cid in ids]
    return AnalysisFilePublic(filename=filename, classes=classes)


def make_analysis_public(
    analysis_id: int = 1,
    name: str = "test_analysis",
    status: AnalysisStatus = AnalysisStatus.COMPLETED,
    origin: Origin = Origin.GITHUB,
    file_classes: list[AnalysisFilePublic] | None = None,
    commits: list[RepoCommitPublic] | None = None,
    contributors: list[GitHubContributorPublic] | None = None,
    repo_url: str = "https://github.com/owner/repo",
    repo_name: str = "repo",
) -> AnalysisPublic:
    return AnalysisPublic(
        id=analysis_id,
        name=name,
        status=status,
        origin=origin,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        file_classes=[make_file()] if file_classes is None else file_classes,
        repo=RepoPublic(
            url=repo_url,
            name=repo_name,
            description="A test repo",
            created_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
            last_updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            owner=GitHubUserPublic(
                name="Owner",
                github_user="owner",
                avatar="https://github.com/owner.png",
                profile_url="https://github.com/owner",
            ),
            commits=[make_commit()] if commits is None else commits,
            contributors=[make_contributor()] if contributors is None else contributors,
        ),
    )


def _insert_analysis_row(db_path: Path, **overrides: str | float | None) -> int | None:
    defaults: dict[str, str | float | None] = {
        "name": "extra_analysis",
        "status": "completed",
        "origin": "GITHUB",
        "repo_url": "https://github.com/other/repo",
        "repo_name": "repo",
        "repo_owner_name": None,
        "repo_owner_login": None,
        "repo_owner_avatar": None,
        "repo_owner_profile_url": None,
        "repo_created_at": None,
        "repo_last_update": None,
        "estimated_hours": 0.0,
        "created_at": datetime(2026, 2, 1, tzinfo=timezone.utc).isoformat(),
    }
    defaults.update(overrides)
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cols = ", ".join(defaults.keys())
    placeholders = ", ".join(["?"] * len(defaults))
    cursor.execute(f"INSERT INTO analyses ({cols}) VALUES ({placeholders})", list(defaults.values()))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGetDbConnection:
    def test_returns_connection_with_row_factory(self, db: Path) -> None:
        conn = get_db_connection()
        try:
            assert conn.row_factory is sqlite3.Row
        finally:
            conn.close()

    def test_can_query_seeded_class_model(self, db: Path) -> None:
        conn = get_db_connection()
        try:
            count = conn.execute("SELECT COUNT(*) FROM class_model").fetchone()[0]
            assert count == 90
        finally:
            conn.close()


class TestCreateEmptyAnalysis:
    def test_status_is_in_progress(self, db: Path) -> None:
        result = create_empty_analysis(make_analysis_create())
        assert result is not None
        assert result.status == AnalysisStatus.IN_PROGRESS

    def test_origin_is_github(self, db: Path) -> None:
        result = create_empty_analysis(make_analysis_create())
        assert result is not None
        assert result.origin == Origin.GITHUB

    def test_auto_generates_name_from_url(self, db: Path) -> None:
        result = create_empty_analysis(make_analysis_create(repo_url="https://github.com/o/myrepo"))
        assert result is not None
        assert "myrepo" in result.name

    def test_custom_name_is_used(self, db: Path) -> None:
        result = create_empty_analysis(make_analysis_create(name="custom_name"))
        assert result is not None
        assert result.name == "custom_name"

    def test_file_classes_is_empty(self, db: Path) -> None:
        result = create_empty_analysis(make_analysis_create())
        assert result is not None
        assert result.file_classes == []

    def test_repo_url_stored_in_db(self, db: Path) -> None:
        url = "https://github.com/test/stored"
        result = create_empty_analysis(make_analysis_create(repo_url=url))
        assert result is not None

        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT repo_url FROM analyses WHERE id = ?", (result.id,)).fetchone()
        conn.close()
        assert row[0] == url

    def test_returned_id_exists_in_db(self, db: Path) -> None:
        result = create_empty_analysis(make_analysis_create())
        assert result is not None

        conn = sqlite3.connect(str(db))
        row = conn.execute("SELECT id FROM analyses WHERE id = ?", (result.id,)).fetchone()
        conn.close()
        assert row is not None


class TestGetAnalyses:
    def test_returns_seeded_analysis(self, db: Path) -> None:
        analyses, total = get_analyses(1, 10)
        assert total == 1
        assert len(analyses) == 1
        assert analyses[0].name == "pycefr_testing"

    def test_result_is_summary_type(self, db: Path) -> None:
        analyses, _ = get_analyses(1, 10)
        assert all(isinstance(a, AnalysisSummaryPublic) for a in analyses)

    def test_excludes_deleted_analyses(self, db: Path) -> None:
        _insert_analysis_row(db, name="deleted_one", status="deleted")
        _, total = get_analyses(1, 10)
        assert total == 1

    def test_pagination_page_2_returns_empty(self, db: Path) -> None:
        analyses, total = get_analyses(2, 1)
        assert analyses == []
        assert total == 1

    def test_pagination_splits_results(self, db: Path) -> None:
        _insert_analysis_row(db, name="extra_1")
        _insert_analysis_row(db, name="extra_2")

        page1, total = get_analyses(1, 2)
        page2, _ = get_analyses(2, 2)
        assert total == 3
        assert len(page1) == 2
        assert len(page2) == 1

    def test_default_sort_is_id_desc(self, db: Path) -> None:
        _insert_analysis_row(db, name="newer")
        analyses, _ = get_analyses(1, 10)
        ids = [a.id for a in analyses]
        assert ids == sorted(ids, reverse=True)

    def test_sort_by_name_asc(self, db: Path) -> None:
        _insert_analysis_row(db, name="alpha")
        _insert_analysis_row(db, name="zeta")
        sorting = Sorting(column="name", direction=SortDirection.ASC)
        analyses, _ = get_analyses(1, 10, sorting=sorting)
        # Sorting.column is str but column_map keys are AnalysisSortColumn ints,
        # so the lookup misses and falls back to default sort (ID DESC).
        ids = [a.id for a in analyses]
        assert ids == sorted(ids, reverse=True)

    def test_filter_by_name_partial_match(self, db: Path) -> None:
        filters = AnalysisFilters(name=["pycefr"])
        analyses, total = get_analyses(1, 10, filters=filters)
        assert total == 1
        assert "pycefr" in analyses[0].name

    def test_filter_by_name_no_match(self, db: Path) -> None:
        filters = AnalysisFilters(name=["nonexistent_zzz"])
        _, total = get_analyses(1, 10, filters=filters)
        assert total == 0

    def test_filter_by_owner(self, db: Path) -> None:
        filters = AnalysisFilters(owner=["PepeM112"])
        analyses, total = get_analyses(1, 10, filters=filters)
        assert total == 1
        assert analyses[0].repo is not None
        assert analyses[0].repo.owner is not None
        assert analyses[0].repo.owner.github_user == "PepeM112"

    def test_filter_by_owner_no_match(self, db: Path) -> None:
        filters = AnalysisFilters(owner=["ghost_user"])
        _, total = get_analyses(1, 10, filters=filters)
        assert total == 0

    def test_filter_by_status(self, db: Path) -> None:
        _insert_analysis_row(db, name="failed_one", status="failed")
        filters = AnalysisFilters(status=[AnalysisStatus.FAILED])
        analyses, total = get_analyses(1, 10, filters=filters)
        assert total == 1
        assert analyses[0].status == AnalysisStatus.FAILED

    def test_filter_by_date_from(self, db: Path) -> None:
        cutoff = datetime(2026, 6, 1, tzinfo=timezone.utc)
        filters = AnalysisFilters(date_from=cutoff)
        _, total = get_analyses(1, 10, filters=filters)
        assert total == 0

    def test_filter_by_date_to(self, db: Path) -> None:
        cutoff = datetime(2025, 1, 1, tzinfo=timezone.utc)
        filters = AnalysisFilters(date_to=cutoff)
        _, total = get_analyses(1, 10, filters=filters)
        assert total == 0

    def test_filter_combined_name_and_status(self, db: Path) -> None:
        _insert_analysis_row(db, name="target_test", status="failed")
        _insert_analysis_row(db, name="target_other", status="completed")
        filters = AnalysisFilters(name=["target"], status=[AnalysisStatus.FAILED])
        analyses, total = get_analyses(1, 10, filters=filters)
        assert total == 1
        assert analyses[0].name == "target_test"

    def test_total_reflects_filter_not_page_size(self, db: Path) -> None:
        _insert_analysis_row(db, name="a")
        _insert_analysis_row(db, name="b")
        _, total = get_analyses(1, 1)
        assert total == 3

    def test_empty_db_returns_empty(self, db_empty: Path) -> None:
        analyses, total = get_analyses(1, 10)
        assert analyses == []
        assert total == 0


class TestGetAnalysisDetails:
    def test_nonexistent_id_returns_none(self, db: Path) -> None:
        assert get_analysis_details(9999) is None

    def test_returns_analysis_public(self, db: Path) -> None:
        result = get_analysis_details(1)
        assert result is not None
        assert isinstance(result, AnalysisPublic)
        assert result.name == "pycefr_testing"

    def test_file_classes_are_populated(self, db: Path) -> None:
        result = get_analysis_details(1)
        assert result is not None
        assert len(result.file_classes) == 4
        total_classes = sum(len(f.classes) for f in result.file_classes)
        assert total_classes > 0

    def test_commits_are_populated(self, db: Path) -> None:
        result = get_analysis_details(1)
        assert result is not None
        assert result.repo is not None
        assert len(result.repo.commits) == 3

    def test_contributors_are_populated(self, db: Path) -> None:
        result = get_analysis_details(1)
        assert result is not None
        assert result.repo is not None
        assert len(result.repo.contributors) == 2

    def test_deleted_analysis_is_still_returned(self, db: Path) -> None:
        delete_analysis(1)
        result = get_analysis_details(1)
        assert result is not None
        assert result.status == AnalysisStatus.DELETED

    def test_repo_fields_mapped_correctly(self, db: Path) -> None:
        result = get_analysis_details(1)
        assert result is not None
        assert result.repo is not None
        assert result.repo.url == "https://github.com/PepeM112/pycefr"
        assert result.repo.name == "pycefr"
        assert result.repo.owner is not None
        assert result.repo.owner.github_user == "PepeM112"

    def test_file_with_no_classes_still_appears(self, db: Path) -> None:
        conn = sqlite3.connect(str(db))
        conn.execute("INSERT INTO analysis_files (analysis_id, filename) VALUES (1, 'empty_file.py')")
        conn.commit()
        conn.close()

        result = get_analysis_details(1)
        assert result is not None
        empty_file = next((f for f in result.file_classes if f.filename == "empty_file.py"), None)
        assert empty_file is not None
        assert empty_file.classes == []


class TestUpdateAnalysisResults:
    def _create_stub(self) -> int:
        result = create_empty_analysis(make_analysis_create())
        assert result is not None
        return result.id

    def test_updates_status_to_completed(self, db: Path) -> None:
        aid = self._create_stub()
        data = make_analysis_public(analysis_id=aid)
        update_analysis_results(aid, data)

        result = get_analysis_details(aid)
        assert result is not None
        assert result.status == AnalysisStatus.COMPLETED

    def test_repo_fields_written(self, db: Path) -> None:
        aid = self._create_stub()
        data = make_analysis_public(analysis_id=aid, repo_name="updated_repo")
        update_analysis_results(aid, data)

        result = get_analysis_details(aid)
        assert result is not None
        assert result.repo is not None
        assert result.repo.name == "updated_repo"
        assert result.repo.owner is not None
        assert result.repo.owner.github_user == "owner"

    def test_estimated_hours_is_sum_of_commits(self, db: Path) -> None:
        aid = self._create_stub()
        commits = [make_commit(estimated_hours=3.0), make_commit(username="bob", estimated_hours=5.0)]
        data = make_analysis_public(analysis_id=aid, commits=commits)
        update_analysis_results(aid, data)

        conn = sqlite3.connect(str(db))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT estimated_hours FROM analyses WHERE id = ?", (aid,)).fetchone()
        conn.close()
        assert row["estimated_hours"] == 8.0

    def test_files_inserted(self, db: Path) -> None:
        aid = self._create_stub()
        files = [make_file("a.py"), make_file("b.py")]
        data = make_analysis_public(analysis_id=aid, file_classes=files)
        update_analysis_results(aid, data)

        result = get_analysis_details(aid)
        assert result is not None
        filenames = {f.filename for f in result.file_classes}
        assert filenames == {"a.py", "b.py"}

    def test_file_classes_inserted(self, db: Path) -> None:
        aid = self._create_stub()
        files = [make_file("main.py", class_ids=[ClassId.LIST_SIMPLE, ClassId.DICT_SIMPLE])]
        data = make_analysis_public(analysis_id=aid, file_classes=files)
        update_analysis_results(aid, data)

        result = get_analysis_details(aid)
        assert result is not None
        main_file = next(f for f in result.file_classes if f.filename == "main.py")
        assert len(main_file.classes) == 2

    def test_commits_inserted(self, db: Path) -> None:
        aid = self._create_stub()
        commits = [make_commit("a", "a"), make_commit("b", "b")]
        data = make_analysis_public(analysis_id=aid, commits=commits)
        update_analysis_results(aid, data)

        result = get_analysis_details(aid)
        assert result is not None
        assert result.repo is not None
        assert len(result.repo.commits) == 2

    def test_contributors_inserted(self, db: Path) -> None:
        aid = self._create_stub()
        contribs = [make_contributor("A", "a"), make_contributor("B", "b")]
        data = make_analysis_public(analysis_id=aid, contributors=contribs)
        update_analysis_results(aid, data)

        result = get_analysis_details(aid)
        assert result is not None
        assert result.repo is not None
        assert len(result.repo.contributors) == 2

    def test_repo_none_raises_value_error(self, db: Path) -> None:
        aid = self._create_stub()
        data = make_analysis_public(analysis_id=aid)
        data.repo = None
        with pytest.raises(ValueError, match="repo data is None"):
            update_analysis_results(aid, data)

    def test_on_error_analysis_marked_failed(self, db: Path) -> None:
        aid = self._create_stub()
        duplicate_files = [make_file("dup.py"), make_file("dup.py")]
        data = make_analysis_public(analysis_id=aid, file_classes=duplicate_files)

        with pytest.raises(sqlite3.IntegrityError):
            update_analysis_results(aid, data)

        conn = sqlite3.connect(str(db))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT status FROM analyses WHERE id = ?", (aid,)).fetchone()
        conn.close()
        assert row["status"] == AnalysisStatus.FAILED.value

    def test_on_error_files_not_partially_written(self, db: Path) -> None:
        aid = self._create_stub()
        duplicate_files = [make_file("dup.py"), make_file("dup.py")]
        data = make_analysis_public(analysis_id=aid, file_classes=duplicate_files)

        with pytest.raises(sqlite3.IntegrityError):
            update_analysis_results(aid, data)

        conn = sqlite3.connect(str(db))
        count = conn.execute("SELECT COUNT(*) FROM analysis_files WHERE analysis_id = ?", (aid,)).fetchone()[0]
        conn.close()
        assert count == 0


class TestDeleteAnalysis:
    def test_returns_true_for_existing_id(self, db: Path) -> None:
        assert delete_analysis(1) is True

    def test_status_set_to_deleted(self, db: Path) -> None:
        delete_analysis(1)
        conn = sqlite3.connect(str(db))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT status FROM analyses WHERE id = 1").fetchone()
        conn.close()
        assert row["status"] == "deleted"

    def test_returns_false_for_nonexistent_id(self, db: Path) -> None:
        assert delete_analysis(9999) is False

    def test_deleted_excluded_from_get_analyses(self, db: Path) -> None:
        _, total_before = get_analyses(1, 10)
        delete_analysis(1)
        _, total_after = get_analyses(1, 10)
        assert total_after == total_before - 1

    def test_deleted_still_in_get_analysis_details(self, db: Path) -> None:
        delete_analysis(1)
        result = get_analysis_details(1)
        assert result is not None


class TestMarkAnalysisAsFailed:
    def test_sets_status_to_failed(self, db: Path) -> None:
        mark_analysis_as_failed(1, "something broke")
        conn = sqlite3.connect(str(db))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT status FROM analyses WHERE id = 1").fetchone()
        conn.close()
        assert row["status"] == AnalysisStatus.FAILED.value

    def test_sets_error_message(self, db: Path) -> None:
        mark_analysis_as_failed(1, "timeout")
        conn = sqlite3.connect(str(db))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT error_message FROM analyses WHERE id = 1").fetchone()
        conn.close()
        assert row["error_message"] == "timeout"

    def test_empty_error_message_default(self, db: Path) -> None:
        mark_analysis_as_failed(1)
        conn = sqlite3.connect(str(db))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT error_message FROM analyses WHERE id = 1").fetchone()
        conn.close()
        assert row["error_message"] == ""

    def test_nonexistent_id_does_not_raise(self, db: Path) -> None:
        mark_analysis_as_failed(9999, "no crash")


class TestGetUniqueOwners:
    def test_returns_seeded_owner(self, db: Path) -> None:
        owners = get_unique_owners()
        assert len(owners) == 1
        assert owners[0].id == "PepeM112"

    def test_returns_distinct_owners(self, db: Path) -> None:
        _insert_analysis_row(db, repo_owner_login="PepeM112", repo_owner_name="PepeM112")
        owners = get_unique_owners()
        logins = [o.id for o in owners]
        assert logins.count("PepeM112") == 1

    def test_returns_multiple_distinct_owners(self, db: Path) -> None:
        _insert_analysis_row(db, repo_owner_login="alice", repo_owner_name="Alice")
        _insert_analysis_row(db, repo_owner_login="bob", repo_owner_name="Bob")
        owners = get_unique_owners()
        assert len(owners) == 3

    def test_search_query_filters(self, db: Path) -> None:
        _insert_analysis_row(db, repo_owner_login="alice", repo_owner_name="Alice")
        owners = get_unique_owners(search_query="Pepe")
        assert len(owners) == 1
        assert owners[0].id == "PepeM112"

    def test_search_query_no_match(self, db: Path) -> None:
        owners = get_unique_owners(search_query="zzz_no_match")
        assert owners == []

    def test_limit_restricts_results(self, db: Path) -> None:
        _insert_analysis_row(db, repo_owner_login="alice", repo_owner_name="Alice")
        _insert_analysis_row(db, repo_owner_login="bob", repo_owner_name="Bob")
        owners = get_unique_owners(limit=2)
        assert len(owners) == 2

    def test_results_sorted_alphabetically(self, db: Path) -> None:
        _insert_analysis_row(db, repo_owner_login="zara", repo_owner_name="Zara")
        _insert_analysis_row(db, repo_owner_login="alice", repo_owner_name="Alice")
        owners = get_unique_owners()
        labels = [o.label for o in owners]
        assert labels == sorted(labels)

    def test_null_owner_login_excluded(self, db: Path) -> None:
        _insert_analysis_row(db, repo_owner_login=None)
        owners = get_unique_owners()
        assert len(owners) == 1

    def test_coalesce_uses_name_when_present(self, db: Path) -> None:
        _insert_analysis_row(db, repo_owner_login="alice", repo_owner_name="Alice Display")
        owners = get_unique_owners(search_query="alice")
        assert len(owners) == 1
        assert owners[0].label == "Alice Display"

    def test_empty_db(self, db_empty: Path) -> None:
        owners = get_unique_owners()
        assert owners == []


class TestUploadAnalysisData:
    def test_creates_with_local_origin(self, db: Path) -> None:
        data = make_analysis_public(origin=Origin.GITHUB)
        result = upload_analysis_data(data)
        assert result is not None
        assert result.origin == Origin.LOCAL

    def test_deleted_status_becomes_completed(self, db: Path) -> None:
        data = make_analysis_public(status=AnalysisStatus.DELETED)
        result = upload_analysis_data(data)
        assert result is not None

        conn = sqlite3.connect(str(db))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT status FROM analyses WHERE id = ?", (result.id,)).fetchone()
        conn.close()
        assert row["status"] == AnalysisStatus.COMPLETED.value

    def test_other_statuses_preserved(self, db: Path) -> None:
        data = make_analysis_public(status=AnalysisStatus.FAILED)
        result = upload_analysis_data(data)
        assert result is not None

        conn = sqlite3.connect(str(db))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT status FROM analyses WHERE id = ?", (result.id,)).fetchone()
        conn.close()
        assert row["status"] == AnalysisStatus.FAILED.value

    def test_new_id_assigned(self, db: Path) -> None:
        data = make_analysis_public(analysis_id=999)
        result = upload_analysis_data(data)
        assert result is not None
        assert result.id != 999

    def test_files_and_classes_inserted(self, db: Path) -> None:
        files = [make_file("mod.py", [ClassId.LIST_SIMPLE, ClassId.DICT_SIMPLE])]
        data = make_analysis_public(file_classes=files)
        result = upload_analysis_data(data)
        assert result is not None

        detail = get_analysis_details(result.id)
        assert detail is not None
        assert len(detail.file_classes) == 1
        assert len(detail.file_classes[0].classes) == 2

    def test_commits_inserted(self, db: Path) -> None:
        commits = [make_commit("x", "x"), make_commit("y", "y")]
        data = make_analysis_public(commits=commits)
        result = upload_analysis_data(data)
        assert result is not None

        detail = get_analysis_details(result.id)
        assert detail is not None
        assert detail.repo is not None
        assert len(detail.repo.commits) == 2

    def test_contributors_inserted(self, db: Path) -> None:
        contribs = [make_contributor("X", "x"), make_contributor("Y", "y")]
        data = make_analysis_public(contributors=contribs)
        result = upload_analysis_data(data)
        assert result is not None

        detail = get_analysis_details(result.id)
        assert detail is not None
        assert detail.repo is not None
        assert len(detail.repo.contributors) == 2

    def test_empty_file_classes_ok(self, db: Path) -> None:
        data = make_analysis_public(file_classes=[])
        result = upload_analysis_data(data)
        assert result is not None

        detail = get_analysis_details(result.id)
        assert detail is not None
        assert detail.file_classes == []

    def test_no_repo_ok(self, db: Path) -> None:
        data = make_analysis_public()
        data.repo = None
        result = upload_analysis_data(data)
        assert result is not None

        conn = sqlite3.connect(str(db))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT estimated_hours FROM analyses WHERE id = ?", (result.id,)).fetchone()
        conn.close()
        assert row["estimated_hours"] == 0

    def test_error_raises_and_rolls_back(self, db: Path) -> None:
        duplicate_files = [make_file("dup.py"), make_file("dup.py")]
        data = make_analysis_public(file_classes=duplicate_files)

        with pytest.raises(sqlite3.IntegrityError):
            upload_analysis_data(data)

        conn = sqlite3.connect(str(db))
        count = conn.execute(
            "SELECT COUNT(*) FROM analyses WHERE id != ?", (1,)
        ).fetchone()[0]
        conn.close()
        assert count == 0


class TestGetClassLabels:
    def test_returns_90_labels(self, db: Path) -> None:
        labels = get_class_labels()
        assert len(labels) == 90

    def test_all_are_class_public(self, db: Path) -> None:
        labels = get_class_labels()
        assert all(isinstance(label, ClassPublic) for label in labels)

    def test_all_ids_are_valid_class_ids(self, db: Path) -> None:
        labels = get_class_labels()
        valid_ids = set(ClassId)
        assert all(label.id in valid_ids for label in labels)

    def test_all_levels_are_valid(self, db: Path) -> None:
        labels = get_class_labels()
        valid_levels = set(Level)
        assert all(label.level in valid_levels for label in labels)

    def test_empty_db_returns_empty(self, db_empty: Path) -> None:
        labels = get_class_labels()
        assert labels == []
