import configparser
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, cast
from urllib.parse import urlparse

import requests

from backend.config.settings import settings
from backend.models.schemas.repo import GitHubUserPublic

logger = logging.getLogger(__name__)
python_threshold_percentage = settings.python_threshold_percentage


class GitHubManager:
    """
    Manager for interacting with the GitHub REST API.

    Handles repository validation, cloning, and lightweight metadata fetching
    (description, user profiles). Commit history and contributor statistics are
    handled by GitLocalManager, which reads from the cloned .git folder.

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

    def clone_repo(self, clone_id: str | int | None = None) -> str:
        """
        Clone the GitHub repository into a temporary local directory.

        Args:
            clone_id: Optional identifier to isolate the clone directory
                (e.g. analysis ID). When provided, clones into
                ``backend/tmp/{clone_id}/{repo_name}`` so parallel analyses
                don't interfere with each other.

        Returns:
            str: The absolute path where the repository was cloned.

        Raises:
            subprocess.CalledProcessError: If the git clone command fails.
        """
        self._print_status("[ ] Cloning repository", end="")
        clone_dir = Path("backend/tmp") / str(clone_id) if clone_id is not None else Path("backend/tmp")
        clone_path = clone_dir / self.repo_name
        if clone_dir.exists():
            shutil.rmtree(clone_dir)
        clone_dir.mkdir(parents=True, exist_ok=True)
        command_line = ["git", "clone", self.repo_url, str(clone_path)]
        subprocess.run(command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        self._print_status("[✓] Cloning repository")
        return str(clone_path)

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

    def fetch_repo_description(self) -> str | None:
        """
        Fetch only the description field for the current repository.

        Uses the REST API since it's a single lightweight field — no need for GraphQL.
        Requires ``self.user`` and ``self.repo_name`` to be set (call ``validate_repo_url``
        first, or set them manually).

        Returns:
            str | None: The repository description, or None if absent or on error.
        """
        response = self.session.get(self.api_url)
        self._check_response(response)
        return response.json().get("description")

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
