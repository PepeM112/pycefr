import configparser
import logging
import os
import shutil
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, cast
from urllib.parse import urlparse

import requests

from backend.config.settings import settings
from backend.models.schemas.repo import (
    GitHubContributorPublic,
    GitHubUserPublic,
    RepoCommitPublic,
    RepoPublic,
    RepoSummaryPublic,
)

logger = logging.getLogger(__name__)
python_threshold_percentage = settings.python_threshold_percentage


class GitHubManager:
    def __init__(self, user: str = "", repo_url: str = "", is_cli: bool = True) -> None:
        self.user = user
        self.repo_url = repo_url
        self.repo_name = ""
        self.is_cli = is_cli
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {settings.api_key}"})
        self.graphql_url = "https://api.github.com/graphql"
        self._temp_pr_data: List[Dict[str, Any]] = []

    def _print_status(self, message: str, end: str = "\n", flush: bool = False) -> None:
        if self.is_cli:
            print(message, end=end, flush=flush)

    @property
    def api_url(self) -> str:
        return f"https://api.github.com/repos/{self.user}/{self.repo_name}"

    def _query_graphql(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Helper para ejecutar consultas GraphQL."""
        response = self.session.post(self.graphql_url, json={"query": query, "variables": variables})

        self._check_response(response)

        data = response.json()
        if "errors" in data:
            if any(err.get("type") == "NOT_FOUND" for err in data["errors"]):
                raise FileNotFoundError(f"Repository {self.user}/{self.repo_name} not found.")

            logger.error(f"GraphQL Errors: {data['errors']}")
            raise RuntimeError(f"GraphQL error: {data['errors'][0]['message']}")

        return cast(Dict[str, Any], data["data"])

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

    def get_repo_info(self) -> RepoPublic:
        """
        Obtiene toda la información del repositorio usando GraphQL.
        Optimiza la obtención de info básica, contribuidores y commits.
        """
        self._print_status("[ ] Fetching data via GraphQL...", end="")
        repo_data = self._get_repo_base_data()
        repo_commits = self._get_repo_commits_graphql()
        self._print_status("\r[✓] Data fetched successfully")
        repo_contributors = self._get_repo_contributors()

        return RepoPublic(
            name=repo_data.name,
            url=repo_data.url,
            description=repo_data.description,
            created_at=repo_data.created_at,
            last_updated_at=repo_data.last_updated_at,
            owner=repo_data.owner,
            commits=repo_commits,
            contributors=repo_contributors,
        )

    def _get_repo_base_data(self) -> RepoSummaryPublic:
        query = """
        query($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) {
            name
            url
            description
            createdAt
            updatedAt
            owner {
              login
              avatarUrl
              ... on User { name }
              ... on Organization { name }
            }
            pullRequests(states: MERGED, last: 50) {
              nodes {
                author { login }
                commits(last: 100) {
                  totalCount
                  nodes {
                    commit { committedDate }
                  }
                }
              }
            }
          }
        }
        """
        variables = {"owner": self.user, "name": self.repo_name}

        self._print_status("[ ] Fetching repository data", end=" ")
        data = self._query_graphql(query, variables)["repository"]

        # Store PRs for later processing
        self._temp_pr_data = data.get("pullRequests", {}).get("nodes", [])

        return RepoSummaryPublic(
            name=data["name"],
            url=data["url"],
            description=data["description"],
            created_at=data["createdAt"],
            last_updated_at=data["updatedAt"],
            owner=GitHubUserPublic(
                name=data["owner"].get("name") or data["owner"]["login"],
                github_user=data["owner"]["login"],
                avatar=data["owner"]["avatarUrl"],
                profile_url=f"https://github.com/{data['owner']['login']}",
            ),
        )

    def _get_repo_commits_graphql(self) -> List[RepoCommitPublic]:
        """
        Obtiene el historial de commits paginado mediante cursores de GraphQL.
        Trae additions, deletions y changedFiles en cada nodo.
        """
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

        query = """
        query($owner: String!, $name: String!, $cursor: String) {
          repository(owner: $owner, name: $name) {
            defaultBranchRef {
              target {
                ... on Commit {
                  history(first: 100, after: $cursor) {
                    totalCount
                    pageInfo {
                      hasNextPage
                      endCursor
                    }
                    nodes {
                      additions
                      deletions
                      changedFiles
                      committedDate
                      author {
                        name
                        user { login }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """

        has_next_page = True
        cursor = None
        total_processed = 0

        while has_next_page:
            variables: Dict[str, Any] = {"owner": self.user, "name": self.repo_name, "cursor": cursor}
            data = self._query_graphql(query, variables)

            repo_ref = data["repository"].get("defaultBranchRef")
            if not repo_ref:
                break

            history = repo_ref["target"]["history"]
            total_count = history["totalCount"]
            nodes = history["nodes"]

            for node in cast(List[Dict[str, Any]], nodes):
                author_data: Dict[str, Any] = node.get("author") or {}
                author_name: str = str(author_data.get("name") or "Unknown")

                user_obj: Dict[str, Any] | None = author_data.get("user")
                github_login: str = (user_obj.get("login") if user_obj else None) or "ghost"

                stats = user_stats[author_name]
                stats["username"] = author_name
                stats["github_user"] = github_login
                stats["commits"] += 1
                stats["loc"] += node["additions"] + node["deletions"]
                stats["total_files_modified"] += node["changedFiles"]

                if node["committedDate"]:
                    dt = datetime.fromisoformat(node["committedDate"].replace("Z", "+00:00"))
                    stats["commit_timestamps"].append(dt.timestamp())

            total_processed += len(nodes)
            if self.is_cli:
                print(f"\r[ ] Fetching commits: {total_processed}/{total_count}", end="", flush=True)

            page_info = history["pageInfo"]
            has_next_page = page_info["hasNextPage"]
            cursor = page_info["endCursor"]

        # Apply PR compensation
        for pr in self._temp_pr_data:
            author_obj = pr.get("author")
            if not author_obj:
                continue

            login = author_obj.get("login")
            for stats in user_stats.values():
                if stats["github_user"] == login:
                    pr_commits = pr.get("commits", {})
                    # Add extra commits (subtracting the 1 squash commit already counted in main)
                    stats["commits"] += max(0, pr_commits.get("totalCount", 0) - 1)

                    # Extract real timestamps from the PR's internal commits
                    for c_node in pr_commits.get("nodes", []):
                        c_date = c_node.get("commit", {}).get("committedDate")
                        if c_date:
                            dt = datetime.fromisoformat(c_date.replace("Z", "+00:00"))
                            stats["commit_timestamps"].append(dt.timestamp())
                    break

        # Format final results
        final_results: List[RepoCommitPublic] = []
        for data in user_stats.values():
            data["estimated_hours"] = self._calculate_estimated_hours(data["commit_timestamps"])
            del data["commit_timestamps"]
            final_results.append(RepoCommitPublic(**data))

        return final_results

    def _get_repo_contributors(self) -> List[GitHubContributorPublic]:
        self._print_status("[ ] Fetching contributors", end="", flush=True)
        response = self.session.get(f"{self.api_url}/contributors")
        self._check_response(response)
        contributors_data = response.json()
        contributors = [
            GitHubContributorPublic(
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

    def fetch_user(self) -> GitHubUserPublic:
        self._print_status(f"[ ] Fetching user: {self.user}", end="")
        response = self.session.get(f"https://api.github.com/users/{self.user}")
        self._check_response(response)
        self._print_status("\r[✓] Fetching user")
        user = response.json()
        return GitHubUserPublic(
            name=user.get("name", ""),
            github_user=user.get("login"),
            avatar=user.get("avatar_url"),
            profile_url=user.get("html_url"),
        )

    # ... (fetch_user_repos y get_git_repo_url se mantienen igual) ...
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
