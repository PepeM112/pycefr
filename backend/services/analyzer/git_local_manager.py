import logging
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from backend.models.schemas.repo import (
    GitHubContributorPublic,
    GitHubUserPublic,
    RepoCommitPublic,
    RepoPublic,
)
from backend.services.analyzer.git_utils import get_remote_origin_url

logger = logging.getLogger(__name__)

_COMMIT_MARKER = "PYCEFR_COMMIT:"


class GitLocalManager:
    """
    Extracts repository metadata from a locally cloned git repository.

    Provides equivalent data to GitHubManager.get_repo_info() but reads
    directly from the .git folder — no GitHub API calls, no network latency.
    The bottleneck (paginated commit history via GraphQL) is replaced by a
    single local `git log --numstat` invocation.

    Attributes:
        repo_path (Path): Absolute path to the cloned repository.
    """

    def __init__(self, repo_path: str) -> None:
        self.repo_path = Path(repo_path)

    def get_repo_info(self) -> RepoPublic:
        """
        Build a RepoPublic instance from local git data.

        Returns:
            RepoPublic: Repository metadata and contributor statistics.
        """
        url = self.get_remote_url()
        name, owner_login = self.parse_url(url)
        first_date, last_date = self.get_repo_dates()
        commits = self.get_commit_stats()

        contributors: List[GitHubContributorPublic] = [
            GitHubContributorPublic(
                name=c.username,
                github_user=c.github_user,
                avatar=self._build_avatar_url(c.github_user),
                profile_url=self._build_profile_url(c.github_user),
                contributions=c.commits,
            )
            for c in commits
        ]
        contributors.sort(key=lambda x: x.contributions, reverse=True)

        return RepoPublic(
            name=name,
            url=url,
            description=None,
            created_at=first_date,
            last_updated_at=last_date,
            owner=GitHubUserPublic(
                name=owner_login,
                github_user=owner_login,
                avatar=self._build_avatar_url(owner_login),
                profile_url=self._build_profile_url(owner_login),
            ),
            commits=commits,
            contributors=contributors,
        )

    def get_remote_url(self) -> str:
        """Read the remote origin URL from .git/config."""
        return get_remote_origin_url(self.repo_path)

    def parse_url(self, url: str) -> Tuple[str, str]:
        """
        Extract (repo_name, owner_login) from a GitHub HTTPS URL.

        Args:
            url (str): A GitHub HTTPS URL.

        Returns:
            Tuple[str, str]: (repo_name, owner_login). Both empty strings if unparseable.
        """
        parsed = urlparse(url)
        segments = [s for s in parsed.path.strip("/").split("/") if s]
        if len(segments) >= 2:
            return segments[1].removesuffix(".git"), segments[0]
        return "", ""

    def get_repo_dates(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Get the dates of the first and last commit.

        Returns:
            Tuple[Optional[datetime], Optional[datetime]]: (first_commit_date, last_commit_date)
        """
        first_output = self._run_git(["log", "--reverse", "--format=%aI", "-1"])
        last_output = self._run_git(["log", "-1", "--format=%aI"])

        first_line = first_output.splitlines()[0] if first_output.strip() else None
        last_line = last_output.strip() if last_output.strip() else None

        return (
            datetime.fromisoformat(first_line) if first_line else None,
            datetime.fromisoformat(last_line) if last_line else None,
        )

    def get_commit_stats(self) -> List[RepoCommitPublic]:
        """
        Parse `git log --numstat` to build per-contributor statistics.

        The format line uses a unique marker to distinguish commit headers from
        numstat lines. Author names may contain `|` so fields are split from
        both ends (hash first, date and email last).

        Returns:
            List[RepoCommitPublic]: Aggregated stats per contributor.
        """
        output = self._run_git(
            [
                "log",
                f"--pretty=format:{_COMMIT_MARKER}%H|%an|%ae|%aI",
                "--numstat",
            ]
        )

        user_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "username": "",
                "github_user": "",
                "loc": 0,
                "commits": 0,
                "commit_timestamps": [],
                "total_files_modified": 0,
            }
        )

        current_github_user: Optional[str] = None

        for line in output.splitlines():
            if line.startswith(_COMMIT_MARKER):
                rest = line[len(_COMMIT_MARKER):]
                parts = rest.split("|")
                if len(parts) < 4:
                    continue
                # Fields: hash | name (may contain |) | email | date
                date_str = parts[-1]
                author_email = parts[-2]
                author_name = "|".join(parts[1:-2])
                current_github_user = self.extract_github_user(author_email, author_name)

                stats = user_stats[current_github_user]
                if not stats["username"] or stats["username"] == "Unknown":
                    stats["username"] = author_name
                stats["github_user"] = current_github_user
                stats["commits"] += 1
                try:
                    stats["commit_timestamps"].append(datetime.fromisoformat(date_str).timestamp())
                except ValueError:
                    logger.warning(f"Could not parse commit date: {date_str!r}")

            elif line and "\t" in line and current_github_user:
                # numstat line: additions\tdeletions\tfilepath (binary files use "-")
                tab_parts = line.split("\t", 2)
                if len(tab_parts) == 3:
                    additions_str, deletions_str = tab_parts[0], tab_parts[1]
                    try:
                        additions = int(additions_str) if additions_str != "-" else 0
                        deletions = int(deletions_str) if deletions_str != "-" else 0
                        user_stats[current_github_user]["loc"] += additions + deletions
                        user_stats[current_github_user]["total_files_modified"] += 1
                    except ValueError:
                        pass

        final: List[RepoCommitPublic] = []
        for stats in user_stats.values():
            timestamps: List[float] = stats.pop("commit_timestamps")
            estimated_hours = self.calculate_estimated_hours(timestamps)
            final.append(RepoCommitPublic(estimated_hours=estimated_hours, **stats))

        return final

    def _run_git(self, args: List[str]) -> str:
        """Run a git command in repo_path and return stdout."""
        result = subprocess.run(
            ["git"] + args,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    @staticmethod
    def extract_github_user(email: str, name: str) -> str:
        """
        Derive a GitHub username from an author email.

        GitHub generates noreply addresses in two formats:
          - ``username@users.noreply.github.com``
          - ``id+username@users.noreply.github.com``

        Falls back to the author name when the email is not a noreply address.

        Args:
            email (str): The commit author email.
            name (str): The commit author name (fallback).

        Returns:
            str: The best available GitHub username.
        """
        if email.endswith("@users.noreply.github.com"):
            local = email.split("@")[0]
            return local.split("+", 1)[-1] if "+" in local else local
        # Fallback: name may contain spaces which are invalid in GitHub usernames
        return name.replace(" ", "")

    @staticmethod
    def _build_avatar_url(github_user: str) -> str:
        return f"https://github.com/{github_user}.png"

    @staticmethod
    def _build_profile_url(github_user: str) -> str:
        return f"https://github.com/{github_user}"

    @staticmethod
    def calculate_estimated_hours(
        commit_timestamps: List[float],
        session_threshold_seconds: int = 7200,
        default_commit_time_seconds: int = 1200,
    ) -> float:
        """
        Estimate development hours from commit timestamps.

        Uses the same algorithm as GitHubManager: consecutive commits within
        ``session_threshold_seconds`` contribute their actual gap; commits
        starting a new session each add ``default_commit_time_seconds``.

        Args:
            commit_timestamps (List[float]): Unix timestamps (unsorted is fine).
            session_threshold_seconds (int): Max gap for the same session (default 2h).
            default_commit_time_seconds (int): Time credited per session start (default 20min).

        Returns:
            float: Estimated hours, rounded to 2 decimal places.
        """
        if not commit_timestamps:
            return 0.0
        commit_timestamps.sort()
        total_seconds = 0.0
        for i, ts in enumerate(commit_timestamps):
            if i == 0:
                total_seconds += default_commit_time_seconds
                continue
            diff = ts - commit_timestamps[i - 1]
            total_seconds += diff if diff <= session_threshold_seconds else default_commit_time_seconds
        return round(total_seconds / 3600, 2)
