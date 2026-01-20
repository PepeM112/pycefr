from typing import List, Optional

from pydantic import field_validator

from backend.models.schemas.common import BaseSchema


class GitHubUser(BaseSchema):
    name: Optional[str] = ""
    github_user: str
    avatar: str
    profile_url: str
    commits: Optional[int] = None

    @field_validator("name", mode="before")
    @classmethod
    def handle_null_name(cls, v: str | None) -> str:
        if v is None:
            return ""
        return v


class GitHubContributor(GitHubUser):
    contributions: int


class RepoInfoData(BaseSchema):
    name: str
    url: str
    description: Optional[str]
    created_at: str
    last_updated_at: str
    owner: GitHubUser


class RepoInfoCommit(BaseSchema):
    name: str
    github_user: str
    loc: int
    commits: int
    total_hours: float
    total_files_modified: int


class RepoInfo(BaseSchema):
    data: RepoInfoData
    commits: Optional[List[RepoInfoCommit]]
    contributors: Optional[List[GitHubContributor]]
