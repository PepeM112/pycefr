from datetime import datetime
from typing import List

from backend.models.schemas.common import BaseSchema


class GitHubUserPublic(BaseSchema):
    name: str | None = None
    github_user: str
    avatar: str
    profile_url: str


class GitHubContributorPublic(GitHubUserPublic):
    contributions: int


class RepoCommitPublic(BaseSchema):
    username: str
    github_user: str
    loc: int
    commits: int
    estimated_hours: float
    total_files_modified: int


class RepoSummaryPublic(BaseSchema):
    name: str | None = None
    url: str | None = None
    description: str | None = None
    created_at: datetime | None = None
    last_updated_at: datetime | None = None
    owner: GitHubUserPublic | None = None


class RepoPublic(RepoSummaryPublic):
    commits: List[RepoCommitPublic] = []
    contributors: List[GitHubContributorPublic] = []
