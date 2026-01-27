import configparser
import logging
import math
import os
import re
import shutil
import subprocess
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, cast
from urllib.parse import urlparse

import requests

from backend.config.settings import settings
from backend.models.schemas.repo import (
    GitHubContributor,
    GitHubUser,
    Repo,
    RepoCommit,
    RepoSummary,
)

logger = logging.getLogger(__name__)
python_threshold_percentage = settings.python_threshold_percentage

PER_PAGE = 100


class GitHubManager:
    def __init__(self, user: str = "", repo_url: str = "", is_cli: bool = True) -> None:
        self.user = user
        self.repo_url = repo_url
        self.repo_name = ""
        self.is_cli = is_cli
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {settings.api_key}"})

    def _print_status(self, message: str, end: str = "\n", flush: bool = False) -> None:
        """Helper para imprimir solo si estamos en CLI."""
        if self.is_cli:
            print(message, end=end, flush=flush)

    @property
    def api_url(self) -> str:
        return f"https://api.github.com/repos/{self.user}/{self.repo_name}"

    def validate_repo_url(self) -> None:
        self._print_status("[ ] Validating URL", end="")

        if not self.repo_url:
            raise ValueError("Incorrect URL format. Use: https://github.com/USER/REPO")

        parsed_url = urlparse(self.repo_url)
        if parsed_url.scheme != "https":
            raise ValueError("URL must use the 'https' protocol.")
        if parsed_url.netloc != "github.com":
            raise ValueError("URL must be from 'github.com'.")

        path_segments = parsed_url.path.strip("/").split("/")
        if not path_segments or len(path_segments) < 2:
            raise ValueError("Incorrect URL format. Use: https://github.com/USER/REPO")

        self.user = path_segments[0]
        self.repo_name = path_segments[1].replace(".git", "")

        if not self.validate_python_language():
            raise ValueError(f"The repository does not contain at least {python_threshold_percentage}% of Python.")

        self._print_status("\r[✓] Validating URL")

    def validate_python_language(self) -> bool:
        response = self.session.get(f"{self.api_url}/languages")
        self._check_response(response)

        languages = response.json()
        total_bytes = sum(languages.values())
        python_bytes = languages.get("Python", 0)
        return python_bytes >= total_bytes * python_threshold_percentage / 100 if total_bytes > 0 else False

    def clone_repo(self) -> str:
        self._print_status("[ ] Cloning repository", end="")
        clone_dir = Path("backend/tmp")
        clone_path = clone_dir / self.repo_name

        if clone_dir.exists():
            shutil.rmtree(clone_dir)

        clone_dir.mkdir(parents=True, exist_ok=True)

        command_line = ["git", "clone", self.repo_url, str(clone_path)]
        subprocess.run(command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        self._print_status("\r[✓] Cloning repository")
        return str(clone_path)

    def get_repo_info(self) -> Repo:
        repo_data = self._get_repo()
        repo_commits = self._get_repo_commits()
        repo_contributors = self._get_repo_contributors()

        return Repo(
            name=repo_data.name,
            url=repo_data.url,
            description=repo_data.description,
            created_at=repo_data.created_at,
            last_updated_at=repo_data.last_updated_at,
            owner=repo_data.owner,
            commits=repo_commits,
            contributors=repo_contributors,
        )

    def _get_repo(self) -> RepoSummary:
        self._print_status("[ ] Fetching data", end=" ")
        response = self.session.get(self.api_url)

        self._check_response(response)

        data = response.json()
        owner_data = data.get("owner", {})
        self._print_status("\r[✓] Fetching data")

        owner = GitHubUser(
            name=owner_data.get("name") or owner_data.get("login"),
            github_user=owner_data.get("login", "Unknown"),
            avatar=owner_data.get("avatar_url", ""),
            profile_url=owner_data.get("html_url", ""),
        )

        return RepoSummary(
            name=data["name"],
            url=data["html_url"],
            description=data.get("description"),
            created_at=data["created_at"],
            last_updated_at=data["updated_at"],
            owner=owner,
        )

    def _get_repo_commits(self) -> List[RepoCommit]:
        total_commits = self._get_total_commits_count()
        if total_commits == 0:
            self._print_status("[✓] Fetching commits")
            return []

        all_commits = self._fetch_all_pages(total_commits)

        user_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "username": "",
                "github_user": "",
                "loc": 0,
                "commits": 0,
                "commit_timestamps": [],
                "files_set": set(),
            }
        )

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(self._fetch_commit_details, c["url"]) for c in all_commits]

            completed = 0
            for future in as_completed(futures):
                try:
                    details = future.result()
                    author_name = details.get("commit", {}).get("committer", {}).get("name", "")

                    stats = user_stats[author_name]
                    stats["username"] = author_name
                    stats["github_user"] = details.get("author", {}).get("login", "")
                    stats["commits"] += 1

                    date_str = details.get("commit", {}).get("committer", {}).get("date")
                    if date_str:
                        stats["commit_timestamps"].append(datetime.fromisoformat(date_str).timestamp())

                    stats["loc"] += details.get("stats", {}).get("total", 0)
                    for f in details.get("files", []):
                        stats["files_set"].add(f["filename"])

                    completed += 1

                    if self.is_cli:
                        percent = int((completed / total_commits) * 100)
                        bar_length = 40
                        block = int(round(bar_length * completed / total_commits))
                        progress_bar = "█" * block + "-" * (bar_length - block)
                        print(f"\r[ ] Fetching commits [{progress_bar}] {percent}%\033[K", end="", flush=True)

                except Exception as e:
                    if self.is_cli:
                        print(f"\nERROR: Could not process commit: {e}")
                    logger.warning(f"Commit error: {e}")

        final_results: List[RepoCommit] = []
        for data in user_stats.values():
            data["estimated_hours"] = self._calculate_estimated_hours(data["commit_timestamps"])
            data["total_files_modified"] = len(data["files_set"])
            del data["commit_timestamps"]
            del data["files_set"]
            final_results.append(RepoCommit(**data))

        self._print_status("\r[✓] Fetching commits\033[K", flush=True)
        return final_results

    def _get_repo_contributors(self) -> List[GitHubContributor]:
        self._print_status("[ ] Fetching contributors", end="", flush=True)
        response = self.session.get(f"{self.api_url}/contributors")
        self._check_response(response)

        contributors_data = response.json()
        contributors = [
            GitHubContributor(
                name=contributor.get("login", "Unknown"),
                github_user=contributor.get("login", "Unknown"),
                avatar=contributor.get("avatar_url", ""),
                profile_url=contributor.get("html_url", ""),
                contributions=contributor.get("contributions", 0),
            )
            for contributor in contributors_data
        ]

        self._print_status("\r[✓] Fetching contributors")
        return contributors

    def _get_total_commits_count(self) -> int:
        url = f"{self.api_url}/commits?per_page=1&page=1"
        response = self.session.get(url)

        link_header = response.headers.get("Link")
        if not link_header:
            return len(response.json())

        match = re.search(r'page=(\d+)>; rel="last"', link_header)
        return int(match.group(1)) if match else 1

    def _fetch_commit_details(self, url: str) -> Dict[str, Any]:
        res = self.session.get(url)
        return cast(Dict[str, Any], res.json())

    def _fetch_all_pages(self, total: int) -> List[Dict[str, Any]]:
        num_pages = math.ceil(total / PER_PAGE)

        def _fetch_page(page_num: int) -> List[Dict[str, Any]]:
            res = self.session.get(f"{self.api_url}/commits", params={"per_page": PER_PAGE, "page": page_num})
            self._check_response(res)
            return cast(List[Dict[str, Any]], res.json())

        self._print_status("[ ] Fetching commits", end="", flush=True)
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_page = {executor.submit(_fetch_page, p): p for p in range(1, num_pages + 1)}

            all_data: List[Dict[str, Any]] = []
            for future in as_completed(future_to_page):
                all_data.extend(future.result())
        all_data.sort(key=lambda x: x.get("commit", {}).get("author", {}).get("date", ""))
        return all_data

    def _check_response(self, response: requests.Response) -> None:
        if response.status_code in [401, 403]:
            raise PermissionError("API rate limit exceeded or invalid token.")
        if response.status_code == 404:
            raise FileNotFoundError(f"Repository {self.user}/{self.repo_name} not found.")
        if response.status_code != 200:
            raise RuntimeError(f"Unexpected API error. Status: {response.status_code}")

    def _calculate_estimated_hours(
        self,
        commit_timestamps: List[float],
        session_threshold_seconds: int = 7200,
        default_commit_time_seconds: int = 1200,
    ) -> float:
        if not commit_timestamps:
            return 0.0

        commit_timestamps.sort()
        total_seconds = 0.0

        for i in range(len(commit_timestamps)):
            if i == 0:
                total_seconds += default_commit_time_seconds
                continue
            diff = commit_timestamps[i] - commit_timestamps[i - 1]
            if diff <= session_threshold_seconds:
                total_seconds += diff
            else:
                total_seconds += default_commit_time_seconds

        return round(total_seconds / 3600, 2)

    def fetch_user(self) -> GitHubUser:
        self._print_status(f"[ ] Fetching user: {self.user}", end="")
        response = self.session.get(f"https://api.github.com/users/{self.user}")
        self._check_response(response)
        self._print_status("\r[✓] Fetching user")

        user = response.json()
        return GitHubUser(
            name=user.get("name", ""),
            github_user=user.get("login"),
            avatar=user.get("avatar_url"),
            profile_url=user.get("html_url"),
        )

    def fetch_user_repos(self) -> List[Dict[str, Any]]:
        self._print_status("[ ] Fetching repositories", end="")
        response = self.session.get(f"https://api.github.com/users/{self.user}/repos")
        self._check_response(response)
        self._print_status("\r[✓] Fetching repositories")

        return cast(List[Dict[str, Any]], response.json())

    @staticmethod
    def get_git_repo_url(dir: str = ".") -> str:
        git_dir = os.path.join(dir, ".git")
        if not os.path.isdir(git_dir):
            return ""

        config_file = os.path.join(git_dir, "config")
        if not os.path.isfile(config_file):
            return ""

        config = configparser.ConfigParser()
        config.read(config_file)

        if 'remote "origin"' not in config:
            return ""

        url = config['remote "origin"'].get("url")
        if not url:
            return ""

        if url.startswith("git@"):
            url_part = url[4:]
            http_url = url_part.replace(":", "/", 1).replace(".git", "")
            return f"https://{http_url}"

        return url
