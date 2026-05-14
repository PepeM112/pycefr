"""
Tests for GitLocalManager — verifies that all data returned to the frontend
via RepoPublic can be obtained from a locally cloned .git folder without any
GitHub API calls.

Fixtures build a minimal git repository with two contributors so every field
in the schema can be exercised deterministically.
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest

from backend.services.analyzer.git_local_manager import GitLocalManager

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git"] + args, cwd=cwd, check=True, capture_output=True)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def git_repo(tmp_path: Path) -> Generator[Path, None, None]:
    """
    Minimal git repository with two contributors and two commits.

    Author 1 — Alice — uses a GitHub noreply email (plain form).
    Author 2 — Bob   — uses a GitHub noreply email (id+username form).

    Remote origin is set to a fake GitHub HTTPS URL so URL parsing is testable.
    """
    repo = tmp_path / "test_repo"
    repo.mkdir()

    _git(["init", "-b", "main"], repo)
    _git(["config", "user.email", "alice@users.noreply.github.com"], repo)
    _git(["config", "user.name", "Alice"], repo)
    _git(["remote", "add", "origin", "https://github.com/testowner/test_repo.git"], repo)

    # Commit 1 — Alice: 2 new lines in one file
    (repo / "module.py").write_text("x = 1\ny = 2\n")
    _git(["add", "."], repo)
    _git(["commit", "-m", "Initial commit"], repo)

    # Commit 2 — Bob: 3 new lines in a second file, modifies first file
    _git(["config", "user.email", "123+bob@users.noreply.github.com"], repo)
    _git(["config", "user.name", "Bob"], repo)
    (repo / "utils.py").write_text("def foo():\n    return 42\n\n")
    (repo / "module.py").write_text("x = 1\ny = 2\nz = 3\n")  # +1 line
    _git(["add", "."], repo)
    _git(["commit", "-m", "Add utils and extend module"], repo)

    yield repo


@pytest.fixture()
def manager(git_repo: Path) -> GitLocalManager:
    return GitLocalManager(str(git_repo))


# ---------------------------------------------------------------------------
# get_remote_url
# ---------------------------------------------------------------------------


class TestGetRemoteUrl:
    def test_returns_https_url(self, manager: GitLocalManager) -> None:
        url = manager.get_remote_url()
        assert url == "https://github.com/testowner/test_repo"

    def test_strips_dot_git_suffix(self, manager: GitLocalManager) -> None:
        assert not manager.get_remote_url().endswith(".git")

    def test_missing_git_dir_returns_empty(self, tmp_path: Path) -> None:
        mgr = GitLocalManager(str(tmp_path / "nonexistent"))
        assert mgr.get_remote_url() == ""

    def test_ssh_remote_converted_to_https(self, tmp_path: Path) -> None:
        repo = tmp_path / "ssh_repo"
        repo.mkdir()
        _git(["init", "-b", "main"], repo)
        _git(["remote", "add", "origin", "git@github.com:owner/repo.git"], repo)
        mgr = GitLocalManager(str(repo))
        assert mgr.get_remote_url() == "https://github.com/owner/repo"


# ---------------------------------------------------------------------------
# parse_url
# ---------------------------------------------------------------------------


class TestParseUrl:
    def test_extracts_name_and_owner(self, manager: GitLocalManager) -> None:
        name, owner = manager.parse_url("https://github.com/testowner/test_repo")
        assert name == "test_repo"
        assert owner == "testowner"

    def test_strips_dot_git_from_name(self, manager: GitLocalManager) -> None:
        name, _ = manager.parse_url("https://github.com/owner/repo.git")
        assert name == "repo"

    def test_invalid_url_returns_empty_strings(self, manager: GitLocalManager) -> None:
        name, owner = manager.parse_url("https://github.com/only-one-segment")
        assert name == ""
        assert owner == ""


# ---------------------------------------------------------------------------
# extract_github_user (static)
# ---------------------------------------------------------------------------


class TestExtractGithubUser:
    def test_plain_noreply_email(self) -> None:
        result = GitLocalManager.extract_github_user("alice@users.noreply.github.com", "Alice")
        assert result == "alice"

    def test_id_plus_username_noreply_email(self) -> None:
        result = GitLocalManager.extract_github_user("123+bob@users.noreply.github.com", "Bob")
        assert result == "bob"

    def test_regular_email_falls_back_to_name(self) -> None:
        result = GitLocalManager.extract_github_user("charlie@example.com", "Charlie")
        assert result == "Charlie"

    def test_empty_email_falls_back_to_name(self) -> None:
        result = GitLocalManager.extract_github_user("", "Dave")
        assert result == "Dave"


# ---------------------------------------------------------------------------
# calculate_estimated_hours (static) — same algorithm as GitHubManager
# ---------------------------------------------------------------------------


class TestCalculateEstimatedHours:
    def test_empty_list_returns_zero(self) -> None:
        assert GitLocalManager.calculate_estimated_hours([]) == 0.0

    def test_single_commit_returns_default_session_time(self) -> None:
        result = GitLocalManager.calculate_estimated_hours([1_000_000.0])
        expected = round(1200 / 3600, 2)
        assert result == expected

    def test_two_commits_within_session(self) -> None:
        t1 = 1_000_000.0
        t2 = t1 + 3600.0  # 1 h gap — within the 2 h threshold
        result = GitLocalManager.calculate_estimated_hours([t1, t2])
        expected = round((1200 + 3600) / 3600, 2)
        assert result == expected

    def test_two_commits_in_separate_sessions(self) -> None:
        t1 = 1_000_000.0
        t2 = t1 + 10_000.0  # > 7 200 s → new session
        result = GitLocalManager.calculate_estimated_hours([t1, t2])
        expected = round((1200 + 1200) / 3600, 2)
        assert result == expected

    def test_unsorted_timestamps_give_same_result_as_sorted(self) -> None:
        timestamps = [1_000_000.0, 1_003_000.0, 1_001_800.0]
        assert GitLocalManager.calculate_estimated_hours(timestamps) == GitLocalManager.calculate_estimated_hours(
            sorted(timestamps)
        )


# ---------------------------------------------------------------------------
# get_repo_dates
# ---------------------------------------------------------------------------


class TestGetRepoDates:
    def test_both_dates_returned(self, manager: GitLocalManager) -> None:
        first, last = manager.get_repo_dates()
        assert first is not None
        assert last is not None

    def test_first_date_not_after_last_date(self, manager: GitLocalManager) -> None:
        first, last = manager.get_repo_dates()
        assert first is not None and last is not None
        assert first <= last

    def test_dates_are_timezone_aware(self, manager: GitLocalManager) -> None:
        first, last = manager.get_repo_dates()
        assert first is not None and last is not None
        assert first.tzinfo is not None
        assert last.tzinfo is not None


# ---------------------------------------------------------------------------
# get_commit_stats
# ---------------------------------------------------------------------------


class TestGetCommitStats:
    def test_returns_one_entry_per_contributor(self, manager: GitLocalManager) -> None:
        stats = manager.get_commit_stats()
        assert len(stats) == 2

    def test_alice_has_one_commit(self, manager: GitLocalManager) -> None:
        stats = manager.get_commit_stats()
        alice = next((c for c in stats if c.github_user == "alice"), None)
        assert alice is not None
        assert alice.commits == 1

    def test_bob_has_one_commit(self, manager: GitLocalManager) -> None:
        stats = manager.get_commit_stats()
        bob = next((c for c in stats if c.github_user == "bob"), None)
        assert bob is not None
        assert bob.commits == 1

    def test_alice_username_is_preserved(self, manager: GitLocalManager) -> None:
        stats = manager.get_commit_stats()
        alice = next(c for c in stats if c.github_user == "alice")
        assert alice.username == "Alice"

    def test_alice_loc_counts_additions(self, manager: GitLocalManager) -> None:
        # Alice added 2 lines in module.py
        stats = manager.get_commit_stats()
        alice = next(c for c in stats if c.github_user == "alice")
        assert alice.loc >= 2

    def test_bob_modified_two_files(self, manager: GitLocalManager) -> None:
        # Bob touched utils.py AND module.py
        stats = manager.get_commit_stats()
        bob = next(c for c in stats if c.github_user == "bob")
        assert bob.total_files_modified == 2

    def test_all_fields_present_and_non_negative(self, manager: GitLocalManager) -> None:
        for entry in manager.get_commit_stats():
            assert entry.username
            assert entry.github_user
            assert entry.commits >= 1
            assert entry.loc >= 0
            assert entry.estimated_hours >= 0.0
            assert entry.total_files_modified >= 0


# ---------------------------------------------------------------------------
# get_repo_info — full RepoPublic output (the contract with the frontend)
# ---------------------------------------------------------------------------


class TestGetRepoInfo:
    def test_name_matches_remote_repo(self, manager: GitLocalManager) -> None:
        repo = manager.get_repo_info()
        assert repo.name == "test_repo"

    def test_url_matches_remote_origin(self, manager: GitLocalManager) -> None:
        repo = manager.get_repo_info()
        assert repo.url == "https://github.com/testowner/test_repo"

    def test_description_is_none(self, manager: GitLocalManager) -> None:
        # description is a GitHub-only field; not available from .git
        repo = manager.get_repo_info()
        assert repo.description is None

    def test_owner_github_user(self, manager: GitLocalManager) -> None:
        repo = manager.get_repo_info()
        assert repo.owner is not None
        assert repo.owner.github_user == "testowner"

    def test_owner_avatar_url_format(self, manager: GitLocalManager) -> None:
        repo = manager.get_repo_info()
        assert repo.owner is not None
        assert repo.owner.avatar == "https://github.com/testowner.png"

    def test_owner_profile_url_format(self, manager: GitLocalManager) -> None:
        repo = manager.get_repo_info()
        assert repo.owner is not None
        assert repo.owner.profile_url == "https://github.com/testowner"

    def test_created_at_is_set(self, manager: GitLocalManager) -> None:
        repo = manager.get_repo_info()
        assert repo.created_at is not None
        assert isinstance(repo.created_at, datetime)

    def test_last_updated_at_is_set(self, manager: GitLocalManager) -> None:
        repo = manager.get_repo_info()
        assert repo.last_updated_at is not None
        assert isinstance(repo.last_updated_at, datetime)

    def test_created_at_not_after_last_updated_at(self, manager: GitLocalManager) -> None:
        repo = manager.get_repo_info()
        assert repo.created_at is not None and repo.last_updated_at is not None
        assert repo.created_at <= repo.last_updated_at

    def test_two_commits_entries(self, manager: GitLocalManager) -> None:
        repo = manager.get_repo_info()
        assert len(repo.commits) == 2

    def test_two_contributors(self, manager: GitLocalManager) -> None:
        repo = manager.get_repo_info()
        assert len(repo.contributors) == 2

    def test_contributors_sorted_by_contributions_descending(self, manager: GitLocalManager) -> None:
        repo = manager.get_repo_info()
        contribs = repo.contributors
        for i in range(len(contribs) - 1):
            assert contribs[i].contributions >= contribs[i + 1].contributions

    def test_contributor_avatar_url_format(self, manager: GitLocalManager) -> None:
        repo = manager.get_repo_info()
        for contrib in repo.contributors:
            assert contrib.avatar.startswith("https://github.com/")
            assert contrib.avatar.endswith(".png")

    def test_contributor_profile_url_format(self, manager: GitLocalManager) -> None:
        repo = manager.get_repo_info()
        for contrib in repo.contributors:
            assert contrib.profile_url.startswith("https://github.com/")

    def test_contributor_github_users_match_commit_users(self, manager: GitLocalManager) -> None:
        repo = manager.get_repo_info()
        commit_users = {c.github_user for c in repo.commits}
        contributor_users = {c.github_user for c in repo.contributors}
        assert commit_users == contributor_users

    def test_all_commit_fields_are_populated(self, manager: GitLocalManager) -> None:
        repo = manager.get_repo_info()
        for commit in repo.commits:
            assert commit.username
            assert commit.github_user
            assert commit.commits >= 1
            assert commit.loc >= 0
            assert commit.estimated_hours >= 0.0
            assert commit.total_files_modified >= 0
