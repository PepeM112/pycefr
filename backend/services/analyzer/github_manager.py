import configparser
import math
import os
import re
import shutil
import subprocess
import sys
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
    RepoInfo,
    RepoInfoCommit,
    RepoInfoData,
)

PER_PAGE = 100


class GitHubManager:
    def __init__(self, user: str = "", repo_url: str = "") -> None:
        self.user = user
        self.repo_url = repo_url
        self.repo_name = ""
        self.headers = {"Authorization": f"Bearer {settings.api_key}"}

    @property
    def api_url(self) -> str:
        """Genera la URL base de la API dinámicamente."""
        return f"https://api.github.com/repos/{self.user}/{self.repo_name}"

    def validate_repo_url(self) -> None:
        print("[ ] Validating URL", end="")
        if not self.repo_url:
            sys.exit("\nERROR: Incorrect URL format. For option -r (repository URL), use: https://github.com/USER/REPO")
        parsed_url = urlparse(self.repo_url)
        if parsed_url.scheme != "https":
            sys.exit("\nERROR: URL must use the 'https' protocol.")
        if parsed_url.netloc != "github.com":
            sys.exit("\nERROR: URL must  be from 'github.com'.")

        path_segments = parsed_url.path.strip("/").split("/")
        self.user = path_segments[0]
        self.repo_name = path_segments[1].replace(".git", "")

        if not path_segments:
            sys.exit(
                "\nERROR: Incorrect URL format. For option -r (repository URL), use: https://github.com/USER/REPO.git"
            )

        if not self.validate_python_language():
            sys.exit("\nERROR: The repository does not contain at least 50% of Python.")

        print("\r[✓] Validating URL")

    def validate_python_language(self) -> bool:
        response = requests.get(f"{self.api_url}/languages", headers=self.headers)
        self._check_response(response)

        languages = response.json()
        total_bytes = sum(languages.values())
        python_bytes = languages.get("Python", 0)
        return python_bytes >= total_bytes / 2 if total_bytes > 0 else False

    def clone_repo(self) -> str:
        print("[ ] Cloning repository", end="")
        clone_dir = Path("backend/tmp")
        clone_path = clone_dir / self.repo_name

        if clone_dir.exists():
            shutil.rmtree(clone_dir)

        clone_dir.mkdir(parents=True, exist_ok=True)

        command_line = ["git", "clone", self.repo_url, str(clone_path)]
        # Redirect standard output and error output to subprocess.PIPE
        subprocess.run(command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        print("\r[✓] Cloning repository")
        return str(clone_path)

    def get_repo_info(self) -> RepoInfo:
        repo_data = self._get_repo()
        repo_commits = self._get_repo_commits()
        repo_contributors = self._get_repo_contributors()

        return RepoInfo(data=repo_data, commits=repo_commits, contributors=repo_contributors)

    def _get_repo(self) -> RepoInfoData:
        print("[ ] Fetching data", end="")
        response = requests.get(self.api_url, headers=self.headers)

        self._check_response(response)

        data = response.json()
        owner_data = data.get("owner", {})
        print("\r[✓] Fetching data")

        owner = GitHubUser(
            name=owner_data.get("login", "Unknown"),
            github_user=owner_data.get("login", "Unknown"),
            avatar=owner_data.get("avatar_url", ""),
            profile_url=owner_data.get("html_url", ""),
        )

        return RepoInfoData(
            name=data["name"],
            url=data["html_url"],
            description=data.get("description"),
            created_at=data["created_at"],
            last_updated_at=data["updated_at"],
            owner=owner,
        )

    def _get_repo_commits(self) -> List[RepoInfoCommit]:
        total_commits = self._get_total_commits_count()
        if total_commits == 0:
            print("[✓] Fetching commits")  # TODO: check what to do here, sys.exit?
            return []

        all_commits = self._fetch_all_pages(total_commits)

        user_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"name": "", "github_user": "", "loc": 0, "commits": 0, "commit_dates": [], "files_set": set()}
        )

        bar_length = 40

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(self._fetch_commit_details, c["url"]) for c in all_commits]

            completed = 0
            for future in as_completed(futures):
                try:
                    details = future.result()
                    author_name = details["commit"]["committer"]["name"]

                    stats = user_stats[author_name]
                    stats["name"] = author_name
                    stats["github_user"] = details.get("author", {}).get("login", "Unknown")
                    stats["commits"] += 1

                    # Timestamp for total hours calculation
                    date_str = details["commit"]["committer"]["date"]
                    stats["commit_dates"].append(datetime.fromisoformat(date_str).timestamp())

                    # LOC and Files
                    stats["loc"] += details.get("stats", {}).get("total", 0)
                    for f in details.get("files", []):
                        stats["files_set"].add(f["filename"])

                    completed += 1
                    percent = int((completed / total_commits) * 100)
                    block = int(round(bar_length * completed / total_commits))
                    progress_bar = "█" * block + "-" * (bar_length - block)
                    print(f"\r[ ] Fetching commits [{progress_bar}] {percent}%\033[K", end="", flush=True)
                except Exception as e:
                    print(f"\nERROR: Could not process commit: {e}")

        final_results: List[RepoInfoCommit] = []
        for data in user_stats.values():
            data["total_hours"] = self._calculate_total_hours(data["commit_dates"])
            data["total_files_modified"] = len(data["files_set"])
            del data["commit_dates"]
            del data["files_set"]
            final_results.append(RepoInfoCommit(**data))

        print("\r[✓] Fetching commits\033[K", flush=True)
        return final_results

    def _get_repo_contributors(self) -> List[GitHubContributor]:
        print("[ ] Fetching contributors", end="", flush=True)
        response = requests.get(f"{self.api_url}/contributors", headers=self.headers)
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

        print("\r[✓] Fetching contributors")
        return contributors

    def _get_total_commits_count(self) -> int:
        url = f"{self.api_url}/commits?per_page=1&page=1"
        response = requests.get(url, headers=self.headers)

        link_header = response.headers.get("Link")
        if not link_header:
            # No Link header means only one page
            return len(response.json())

        # Search page number before rel="last"
        match = re.search(r'page=(\d+)>; rel="last"', link_header)
        return int(match.group(1)) if match else 1

    def _fetch_commit_details(self, url: str) -> Dict[str, Any]:
        res = requests.get(url, headers=self.headers)
        return cast(Dict[str, Any], res.json())

    def _fetch_all_pages(self, total: int) -> List[Dict[str, Any]]:
        num_pages = math.ceil(total / PER_PAGE)

        def _fetch_page(page_num: int) -> List[Dict[str, Any]]:
            res = requests.get(
                f"{self.api_url}/commits", params={"per_page": PER_PAGE, "page": page_num}, headers=self.headers
            )
            self._check_response(res)
            return cast(List[Dict[str, Any]], res.json())

        print("[ ] Fetching commits", end="", flush=True)
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_page = {executor.submit(_fetch_page, p): p for p in range(1, num_pages + 1)}

            all_data: List[Dict[str, Any]] = []
            for future in as_completed(future_to_page):
                all_data.extend(future.result())
        all_data.sort(key=lambda x: x["commit"]["author"]["date"])
        return all_data

    @staticmethod
    def display_api_token_error() -> None:
        """
        Handle GitHub API token error by displaying a message and exiting the program.
        """
        print("ERROR: Looks like you've reached the limit of API requests.")
        print(
            "To continue, you will need an API key. You can generate one at:\n\thttps://github.com/settings/tokens\n"
            "and add it to your .env file."
        )
        print("Also see: https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting")
        sys.exit(1)

    def _check_response(self, response: requests.Response) -> None:
        if response.status_code in [401, 403]:
            print("ERROR: API rate limit or invalid token.")
            sys.exit(1)
        if response.status_code == 404:
            sys.exit(f"ERROR: {self.user}/{self.repo_name} not found.")
        if response.status_code != 200:
            sys.exit(f"ERROR: Unexpected error occurred. Status code: {response.status_code}")

    def _calculate_total_hours(
        self,
        commit_dates: List[float],
        session_threshold_seconds: int = 7200,  # 2 horas
        default_commit_time_seconds: int = 1200,  # 20 minutos de "contexto"
    ) -> float:
        """
        Calcula las horas basándose en sesiones de trabajo.
        Cada salto mayor a threshold inicia una nueva sesión con un tiempo base.
        """
        if not commit_dates:
            return 0.0

        commit_dates.sort()

        total_seconds = 0.0

        for i in range(len(commit_dates)):
            if i == 0:
                total_seconds += default_commit_time_seconds
                continue

            diff = commit_dates[i] - commit_dates[i - 1]

            if diff <= session_threshold_seconds:
                total_seconds += diff
            else:
                total_seconds += default_commit_time_seconds

        return round(total_seconds / 3600, 2)

    def fetch_user(self) -> GitHubUser:
        print("[ ] Fetching user", end="")
        response = requests.get(f"https://api.github.com/users/{self.user}", headers=self.headers)
        self._check_response(response)

        user_data = response.json()
        user = GitHubUser(
            name=user_data.get("name", "Unknown"),
            github_user=user_data.get("login", "Unknown"),
            avatar=user_data.get("avatar_url", ""),
            profile_url=user_data.get("html_url", ""),
        )

        print("\r[✓] Fetching user")
        return user

    def fetch_user_repos(self) -> List[Dict[str, Any]]:
        print("[ ] Fetching repositories", end="")
        response = requests.get(f"https://api.github.com/users/{self.user}/repos", headers=self.headers)
        self._check_response(response)

        print("\r[✓] Fetching repositories")
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
            url_part = url[4:]  # Skip 'git@'
            http_url = url_part.replace(":", "/", 1).replace(".git", "")
            return f"https://{http_url}"

        return url

    @staticmethod
    def choose_repo(repos: List[Dict[str, Any]]) -> str:
        print("Repositories found:")
        for idx, repo in enumerate(repos, start=1):
            print(f"\t[{idx}] {repo.get('name')}")
        while True:
            repo_input = input("\nSelect which one you want to analyze (Enter [0] to exit): ")
            if repo_input == "0":
                sys.exit()
            elif repo_input.isdigit():
                repo_pos = int(repo_input) - 1
                if 0 <= repo_pos < len(repos):
                    selected_repo = repos[repo_pos]
                else:
                    print("Invalid number. Please try again.")
                    continue
            else:
                matching_repos = [repo for repo in repos if repo.get("name") == repo_input]
                if not matching_repos:
                    print("Repository name not found. Please try again (Enter [0] to exit).")
                    continue
                selected_repo = matching_repos[0]

            # Confirmar la selección

            confirm_input = input(f"Analyze [{selected_repo.get('name')}]? (Y/n) ")
            if confirm_input.lower() == "y":
                return str(selected_repo.get("html_url"))
            elif confirm_input.lower() != "n":
                print("Not valid. Please enter 'y' or 'n'.")
