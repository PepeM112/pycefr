from datetime import datetime
from typing import List

from backend.models.schemas.common import BaseSchema


class GitHubUser(BaseSchema):
    name: str | None = None
    github_user: str
    avatar: str
    profile_url: str


class GitHubContributor(GitHubUser):
    contributions: int


class RepoCommit(BaseSchema):
    username: str
    github_user: str
    loc: int
    commits: int
    estimated_hours: float
    total_files_modified: int


class RepoSummary(BaseSchema):
    name: str
    url: str
    description: str | None = None
    created_at: datetime
    last_updated_at: datetime
    owner: GitHubUser


class Repo(RepoSummary):
    commits: List[RepoCommit] = []
    contributors: List[GitHubContributor] = []
