import configparser
import logging
import os
import shutil
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, cast
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
    """
    Manager for interacting with the GitHub API (REST and GraphQL).

    Handles repository validation, cloning, metadata extraction, and commit history
    analysis to calculate contribution statistics.

    Attributes:
        user (str): GitHub username or organization name.
        repo_url (str): The full HTTPS URL of the repository.
        repo_name (str): The extracted name of the repository.
        is_cli (bool): Whether to output progress messages to the console.
        session (requests.Session): Authenticated session for API requests.
    """

    def __init__(self, user: str = "", repo_url: str = "", is_cli: bool = True) -> None:
        """
        Initialize the GitHubManager with credentials and targets.

        Args:
            user (str): GitHub username.
            repo_url (str): Repository URL.
            is_cli (bool): Enable CLI status printing.
        """
        self.user = user
        self.repo_url = repo_url
        self.repo_name = ""
        self.is_cli = is_cli
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {settings.api_key}"})
        self.graphql_url = "https://api.github.com/graphql"
        self._temp_pr_data: List[Dict[str, Any]] = []
        self._avatar_cache: Dict[str, str] = {}
        self._profile_url_cache: Dict[str, str] = {}

    def _print_status(self, message: str, end: str = "\n", flush: bool = False) -> None:
        """
        Print a status message to the console if CLI mode is enabled.

        Args:
            message (str): The message to display.
            end (str): The string appended after the last character.
            flush (bool): Whether to forcibly flush the stream.
        """
        if self.is_cli:
            print(f"\r{message}\033[K", end=end, flush=flush)

    @property
    def api_url(self) -> str:
        """
        Construct the base GitHub REST API URL for the current repository.

        Returns:
            str: The formatted REST API URL.
        """
        return f"https://api.github.com/repos/{self.user}/{self.repo_name}"

    def _query_graphql(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a GraphQL query against the GitHub API.

        Args:
            query (str): The GraphQL query string.
            variables (Dict[str, Any]): Variables required by the query.

        Returns:
            Dict[str, Any]: The 'data' payload from the JSON response.

        Raises:
            FileNotFoundError: If the repository is not found.
            RuntimeError: If the GraphQL response contains API errors.
        """
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
        """
        Validate the format of the GitHub URL and extract user/repo info.

        Also verifies if the repository meets the Python language percentage threshold.

        Raises:
            ValueError: If the URL format is invalid or the Python threshold is not met.
        """
        self._print_status("[ ] Validating URL", end="")
        if not self.repo_url:
            raise ValueError("Incorrect URL format. Use: https://github.com/USER/REPO")
        parsed_url = urlparse(self.repo_url)
        if parsed_url.scheme != "https" or parsed_url.netloc != "github.com":
            raise ValueError("URL must be a valid https://github.com/USER/REPO")
        path_segments = parsed_url.path.strip("/").split("/")
        if len(path_segments) < 2:
            raise ValueError("Incorrect URL format. Use: https://github.com/USER/REPO")
        self.user = path_segments[0]
        self.repo_name = path_segments[1].replace(".git", "")
        if not self.validate_python_language():
            raise ValueError(f"The repository does not contain at least {python_threshold_percentage}% of Python.")
        self._print_status("[✓] Validating URL")

    def validate_python_language(self) -> bool:
        """
        Check if the repository reaches the required Python language threshold.

        Returns:
            bool: True if Python usage is above the threshold, False otherwise.
        """
        response = self.session.get(f"{self.api_url}/languages")
        self._check_response(response)
        languages = response.json()
        total_bytes = sum(languages.values())
        python_bytes = languages.get("Python", 0)
        return python_bytes >= total_bytes * python_threshold_percentage / 100 if total_bytes > 0 else False

    def clone_repo(self) -> str:
        """
        Clone the GitHub repository into a temporary local directory.

        Returns:
            str: The absolute path where the repository was cloned.

        Raises:
            subprocess.CalledProcessError: If the git clone command fails.
        """
        self._print_status("[ ] Cloning repository", end="")
        clone_dir = Path("backend/tmp")
        clone_path = clone_dir / self.repo_name
        if clone_dir.exists():
            shutil.rmtree(clone_dir)
        clone_dir.mkdir(parents=True, exist_ok=True)
        command_line = ["git", "clone", self.repo_url, str(clone_path)]
        subprocess.run(command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        self._print_status("[✓] Cloning repository")
        return str(clone_path)

    def get_repo_info(self) -> RepoPublic:
        """
        Fetch comprehensive repository data, including commits and contributors.

        Returns:
            RepoPublic: An object containing metadata, commits, and contributor list.
        """
        self._print_status("[ ] Fetching data via GraphQL...", end="")
        repo_data = self._get_repo_base_data()
        repo_commits = self._get_repo_commits_graphql()

        # Build Contributors List based on Commits Stats
        contributors: List[GitHubContributorPublic] = []
        for committer in repo_commits:
            avatar = self._avatar_cache.get(committer.github_user, "")
            profile = self._profile_url_cache.get(committer.github_user, "")

            contributors.append(
                GitHubContributorPublic(
                    name=committer.username,
                    github_user=committer.github_user,
                    avatar=avatar,
                    profile_url=profile,
                    contributions=committer.commits,
                )
            )

        contributors.sort(key=lambda x: x.contributions, reverse=True)

        self._print_status("[✓] Data fetched successfully")

        return RepoPublic(
            name=repo_data.name,
            url=repo_data.url,
            description=repo_data.description,
            created_at=repo_data.created_at,
            last_updated_at=repo_data.last_updated_at,
            owner=repo_data.owner,
            commits=repo_commits,
            contributors=contributors,
        )

    def _get_repo_base_data(self) -> RepoSummaryPublic:
        """
        Fetch basic repository metadata and initial contributor cache.

        Returns:
            RepoSummaryPublic: Summary information about the repository.
        """
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
            mentionableUsers(first: 50) {
              nodes {
                login
                name
                avatarUrl
                url
              }
            }
            pullRequests(states: MERGED, last: 50) {
              nodes {
                author { login }
                commits(last: 100) {
                  totalCount
                  nodes {
                    commit { oid committedDate }
                  }
                }
              }
            }
          }
        }
        """
        variables = {"owner": self.user, "name": self.repo_name}
        data = self._query_graphql(query, variables)["repository"]

        # Store PRs
        self._temp_pr_data = data.get("pullRequests", {}).get("nodes", [])

        # Pre-populate Cache
        for node in data.get("mentionableUsers", {}).get("nodes", []):
            login = node.get("login")
            if login:
                self._avatar_cache[login] = node.get("avatarUrl", "")
                self._profile_url_cache[login] = node.get("url", "")

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
        Fetch and process paginated commit history with PR compensation.

        Returns:
            List[RepoCommitPublic]: Aggregated commit statistics per contributor.
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
        # Tracking SHAs to avoid double-counting non-squashed commits
        processed_shas: Set[str] = set()

        query = """
        query($owner: String!, $name: String!, $cursor: String) {
          repository(owner: $owner, name: $name) {
            defaultBranchRef {
              target {
                ... on Commit {
                  history(first: 100, after: $cursor) {
                    totalCount
                    pageInfo { hasNextPage endCursor }
                    nodes {
                      oid
                      additions
                      deletions
                      changedFiles
                      committedDate
                      author {
                        name
                        user { login avatarUrl url }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """

        has_next_page, cursor, total_processed = True, None, 0

        while has_next_page:
            variables: Dict[str, Any] = {"owner": self.user, "name": self.repo_name, "cursor": cursor}
            data = self._query_graphql(query, variables)

            repo_ref = data["repository"].get("defaultBranchRef")
            if not repo_ref:
                break

            history = repo_ref["target"]["history"]
            total_count, nodes = history["totalCount"], history["nodes"]

            for node in cast(List[Dict[str, Any]], nodes):
                processed_shas.add(node["oid"])
                author_data: Dict[str, Any] = node.get("author") or {}
                author_name: str = str(author_data.get("name") or "Unknown")
                user_obj: Dict[str, Any] | None = author_data.get("user")
                github_login: str = (user_obj.get("login") if user_obj else None) or "ghost"

                # Cache avatar/profile
                if user_obj and github_login not in self._avatar_cache:
                    self._avatar_cache[github_login] = user_obj.get("avatarUrl", "")
                    self._profile_url_cache[github_login] = user_obj.get("url", "")

                stats = user_stats[github_login]

                if not stats["username"] or stats["username"] == "Unknown":
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
                self._print_status(f"[ ] Fetching commits: {total_processed}/{total_count}", end="", flush=True)

            page_info = history["pageInfo"]
            has_next_page, cursor = page_info["hasNextPage"], page_info["endCursor"]

        # PR Compensation
        for pr in self._temp_pr_data:
            author_obj = pr.get("author")
            if not author_obj:
                continue

            login = author_obj.get("login")
            if login in user_stats:
                stats = user_stats[login]
                added_from_pr = 0
                pr_commits = pr.get("commits", {}).get("nodes", [])

                for c_node in pr_commits:
                    commit_data = c_node.get("commit", {})
                    sha = commit_data.get("oid")

                    # Only count if this commit wasn't already in the main history
                    if sha and sha not in processed_shas:
                        added_from_pr += 1
                        c_date = commit_data.get("committedDate")
                        if c_date:
                            dt = datetime.fromisoformat(c_date.replace("Z", "+00:00"))
                            stats["commit_timestamps"].append(dt.timestamp())

                if added_from_pr > 0:
                    # Squash and merge: We subtract the 1 summary commit that was already counted in the main
                    # history loop.
                    stats["commits"] += added_from_pr - 1

                    # Merge/Rebase: added_from_pr will be 0 because SHAs are already in processed_shas. stats["commits"]
                    # remains unchanged.

        # Generate final results
        final_results: List[RepoCommitPublic] = []
        for data in user_stats.values():
            data["estimated_hours"] = self._calculate_estimated_hours(data["commit_timestamps"])
            del data["commit_timestamps"]
            final_results.append(RepoCommitPublic(**data))

        return final_results

    def _check_response(self, response: requests.Response) -> None:
        """
        Check for common HTTP errors in API responses.

        Args:
            response (requests.Response): The response object to check.

        Raises:
            PermissionError: If API rate limits are hit or the token is invalid.
            FileNotFoundError: If the resource is not found (404).
            RuntimeError: For other non-200 status codes.
        """
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
        """
        Estimate development hours based on the time gaps between commits.

        Args:
            commit_timestamps (List[float]): List of unix timestamps of commits.
            session_threshold_seconds (int): Maximum gap before considering a new session.
            default_commit_time_seconds (int): Time credited for the first commit of a session.

        Returns:
            float: Total estimated hours rounded to 2 decimal places.
        """
        if not commit_timestamps:
            return 0.0
        commit_timestamps.sort()
        total_seconds = 0.0
        for i in range(len(commit_timestamps)):
            if i == 0:
                total_seconds += default_commit_time_seconds
                continue
            diff = commit_timestamps[i] - commit_timestamps[i - 1]
            total_seconds += diff if diff <= session_threshold_seconds else default_commit_time_seconds
        return round(total_seconds / 3600, 2)

    def fetch_user(self) -> GitHubUserPublic:
        """
        Fetch basic information about a GitHub user.

        Returns:
            GitHubUserPublic: Public profile data of the user.
        """
        self._print_status(f"[ ] Fetching user: {self.user}", end="")
        response = self.session.get(f"https://api.github.com/users/{self.user}")
        self._check_response(response)
        self._print_status("[✓] Fetching user")
        user = response.json()
        return GitHubUserPublic(
            name=user.get("name", ""),
            github_user=user.get("login"),
            avatar=user.get("avatar_url"),
            profile_url=user.get("html_url"),
        )

    def fetch_user_repos(self) -> List[Dict[str, Any]]:
        """
        Fetch a list of repositories belonging to a user.

        Returns:
            List[Dict[str, Any]]: List of repository data dictionaries.
        """
        self._print_status("[ ] Fetching repositories", end="")
        response = self.session.get(f"https://api.github.com/users/{self.user}/repos")
        self._check_response(response)
        self._print_status("[✓] Fetching repositories")
        return cast(List[Dict[str, Any]], response.json())

    @staticmethod
    def get_git_repo_url(dir: str = ".") -> str:
        """
        Extract the GitHub remote origin URL from a local .git directory.

        Args:
            dir (str): The local directory to check.

        Returns:
            str: The HTTPS URL of the remote origin, or empty string if not found.
        """
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
