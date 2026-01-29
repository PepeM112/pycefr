from datetime import datetime
from typing import List, Optional

from backend.models.schemas.common import BaseSchema


class GitHubUserPublic(BaseSchema):
    name: Optional[str] = None
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
    name: str
    url: str
    description: Optional[str] = None
    created_at: datetime
    last_updated_at: datetime
    owner: GitHubUserPublic


class RepoPublic(RepoSummaryPublic):
    commits: List[RepoCommitPublic] = []
    contributors: List[GitHubContributorPublic] = []
