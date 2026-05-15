"""Integration tests for the full analysis pipeline.

Tests the web flow end-to-end: POST /analyses → background task (clone, AST
analysis, git metadata) → GET /analyses/{id} with a completed result.

GitHubManager is mocked to avoid network calls and real cloning.  A temporary
git repository with Python fixture files is created per test so that both the
Analyzer (AST parsing) and GitLocalManager (git log) operate on real data.
"""

import subprocess
import textwrap
from contextlib import contextmanager
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pytest
from starlette.testclient import TestClient

from backend.main import app

BASE = "/api/v1/analyses"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _init_git_repo(repo_dir: Path) -> None:
    """Initialise a minimal git repo with a couple of Python files and a commit."""
    repo_dir.mkdir(parents=True, exist_ok=True)

    (repo_dir / "hello.py").write_text(
        textwrap.dedent("""\
            import os

            def greet(name: str) -> str:
                if not name:
                    return "Hello, World!"
                return f"Hello, {name}!"

            for i in range(10):
                print(greet(str(i)))
        """)
    )

    (repo_dir / "utils.py").write_text(
        textwrap.dedent("""\
            from typing import List

            def flatten(nested: List[List[int]]) -> List[int]:
                return [item for sublist in nested for item in sublist]

            try:
                result = flatten([[1, 2], [3]])
            except TypeError:
                result = []
        """)
    )

    _git = ["git", "-C", str(repo_dir)]
    subprocess.run([*_git, "init"], check=True, capture_output=True)
    subprocess.run([*_git, "config", "user.email", "test@users.noreply.github.com"], check=True, capture_output=True)
    subprocess.run([*_git, "config", "user.name", "Test User"], check=True, capture_output=True)
    subprocess.run(
        [*_git, "remote", "add", "origin", "https://github.com/testowner/testrepo.git"],
        check=True,
        capture_output=True,
    )
    subprocess.run([*_git, "add", "."], check=True, capture_output=True)
    subprocess.run([*_git, "commit", "-m", "initial"], check=True, capture_output=True)


@pytest.fixture()
def fake_repo(tmp_path: Path) -> Path:
    repo_dir = tmp_path / "testrepo"
    _init_git_repo(repo_dir)
    return repo_dir


@pytest.fixture()
def client(db_empty: Path) -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


_GH_CLS = "backend.services.analyzer.github_manager.GitHubManager"


@contextmanager
def _mock_github_manager(fake_repo_path: Path) -> Generator[None, None, None]:
    """Patch GitHubManager so it skips network calls and returns the fixture repo."""

    def patched_validate(self: object) -> None:
        self.user = "testowner"  # type: ignore[attr-defined]
        self.repo_name = "testrepo"  # type: ignore[attr-defined]

    def patched_clone(self: object, clone_id: str | int | None = None) -> str:
        return str(fake_repo_path)

    def patched_description(self: object) -> str:
        return "A test repository"

    with (
        patch(f"{_GH_CLS}.validate_repo_url", patched_validate),
        patch(f"{_GH_CLS}.clone_repo", patched_clone),
        patch(f"{_GH_CLS}.fetch_repo_description", patched_description),
        patch("backend.services.analyzer.analyzer.Analyzer.delete_tmp_files"),
    ):
        yield


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestFullAnalysisPipeline:
    def test_create_and_complete_analysis(self, client: TestClient, fake_repo: Path) -> None:
        """POST creates an analysis, background task completes it, GET returns full results."""
        with _mock_github_manager(fake_repo):
            create_resp = client.post(BASE, json={"repo_url": "https://github.com/testowner/testrepo"})

        assert create_resp.status_code == 201
        created = create_resp.json()
        analysis_id = created["id"]
        assert created["status"] == "in_progress"

        detail_resp = client.get(f"{BASE}/{analysis_id}")
        assert detail_resp.status_code == 200
        detail = detail_resp.json()

        assert detail["status"] == "completed"
        assert detail["name"] is not None
        assert len(detail["fileClasses"]) == 2

        filenames = sorted(f["filename"] for f in detail["fileClasses"])
        assert filenames == ["hello.py", "utils.py"]

    def test_analysis_has_classes(self, client: TestClient, fake_repo: Path) -> None:
        """The Analyzer should detect real AST constructs from fixture files."""
        with _mock_github_manager(fake_repo):
            create_resp = client.post(BASE, json={"repo_url": "https://github.com/testowner/testrepo"})

        analysis_id = create_resp.json()["id"]
        detail = client.get(f"{BASE}/{analysis_id}").json()

        all_classes = [
            cls
            for f in detail["fileClasses"]
            for cls in f["classes"]
        ]
        assert len(all_classes) > 0

        class_ids = {cls["classId"] for cls in all_classes}
        assert len(class_ids) > 3

    def test_analysis_has_repo_metadata(self, client: TestClient, fake_repo: Path) -> None:
        """The completed analysis should include repo info from GitLocalManager."""
        with _mock_github_manager(fake_repo):
            create_resp = client.post(BASE, json={"repo_url": "https://github.com/testowner/testrepo"})

        detail = client.get(f"{BASE}/{create_resp.json()['id']}").json()
        repo = detail["repo"]

        assert repo is not None
        assert repo["name"] == "testrepo"
        assert repo["description"] == "A test repository"
        assert "testowner/testrepo" in repo["url"]
        assert len(repo["commits"]) >= 1
        assert len(repo["contributors"]) >= 1

    def test_analysis_has_commit_stats(self, client: TestClient, fake_repo: Path) -> None:
        """Commit stats should reflect the initial commit in the fixture repo."""
        with _mock_github_manager(fake_repo):
            create_resp = client.post(BASE, json={"repo_url": "https://github.com/testowner/testrepo"})

        detail = client.get(f"{BASE}/{create_resp.json()['id']}").json()
        commits = detail["repo"]["commits"]

        assert len(commits) == 1
        commit = commits[0]
        assert commit["githubUser"] == "test"
        assert commit["commits"] == 1
        assert commit["loc"] > 0
        assert commit["totalFilesModified"] == 2

    def test_analysis_appears_in_list(self, client: TestClient, fake_repo: Path) -> None:
        """A completed analysis should appear in the paginated list."""
        with _mock_github_manager(fake_repo):
            create_resp = client.post(BASE, json={"repo_url": "https://github.com/testowner/testrepo"})

        analysis_id = create_resp.json()["id"]
        list_resp = client.get(BASE)
        assert list_resp.status_code == 200

        elements = list_resp.json()["elements"]
        ids = [e["id"] for e in elements]
        assert analysis_id in ids

        match = next(e for e in elements if e["id"] == analysis_id)
        assert match["status"] == "completed"

    def test_analysis_with_custom_name(self, client: TestClient, fake_repo: Path) -> None:
        """Custom name provided at creation should persist through completion."""
        with _mock_github_manager(fake_repo):
            create_resp = client.post(
                BASE, json={"repo_url": "https://github.com/testowner/testrepo", "name": "my-custom-name"}
            )

        detail = client.get(f"{BASE}/{create_resp.json()['id']}").json()
        assert detail["name"] == "my-custom-name"
        assert detail["status"] == "completed"

    def test_delete_after_completion(self, client: TestClient, fake_repo: Path) -> None:
        """Deleting a completed analysis soft-deletes it from the list."""
        with _mock_github_manager(fake_repo):
            create_resp = client.post(BASE, json={"repo_url": "https://github.com/testowner/testrepo"})

        analysis_id = create_resp.json()["id"]
        del_resp = client.delete(f"{BASE}/{analysis_id}")
        assert del_resp.status_code == 204

        list_resp = client.get(BASE)
        ids = [e["id"] for e in list_resp.json()["elements"]]
        assert analysis_id not in ids

    def test_download_completed_analysis(self, client: TestClient, fake_repo: Path) -> None:
        """The download endpoint should return the full analysis as JSON."""
        with _mock_github_manager(fake_repo):
            create_resp = client.post(BASE, json={"repo_url": "https://github.com/testowner/testrepo"})

        analysis_id = create_resp.json()["id"]
        dl_resp = client.get(f"{BASE}/{analysis_id}/download")
        assert dl_resp.status_code == 200
        assert "attachment" in dl_resp.headers.get("content-disposition", "")

        data = dl_resp.json()
        assert data["id"] == analysis_id
        assert data["status"] == "completed"
        assert len(data["file_classes"]) == 2


class TestAnalysisFailure:
    def test_invalid_repo_marks_as_failed(self, client: TestClient) -> None:
        """When GitHubManager.validate_repo_url raises, the analysis should be marked as failed."""
        def failing_validate(self: object) -> None:
            raise ValueError("Repository not found")

        with (
            patch(f"{_GH_CLS}.validate_repo_url", failing_validate),
            patch("backend.services.analyzer.analyzer.Analyzer.delete_tmp_files"),
        ):
            create_resp = client.post(BASE, json={"repo_url": "https://github.com/bad/repo"})

        assert create_resp.status_code == 201
        analysis_id = create_resp.json()["id"]

        detail = client.get(f"{BASE}/{analysis_id}").json()
        assert detail["status"] == "failed"
        assert "Repository not found" in (detail["errorMessage"] or "")
