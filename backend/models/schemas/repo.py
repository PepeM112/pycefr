from typing import List, Optional

from pydantic import BaseModel


class GitHubUser(BaseModel):
    name: str
    github_user: str
    avatar: str
    profile_url: str
    commits: Optional[int] = None


class GitHubContributor(GitHubUser):
    contributions: int


class RepoInfoData(BaseModel):
    name: str
    url: str
    description: Optional[str]
    created_at: str
    last_updated_at: str
    owner: GitHubUser


class RepoInfoCommit(BaseModel):
    name: str
    github_user: str
    loc: int
    commits: int
    total_hours: float
    total_files_modified: int


class RepoInfo(BaseModel):
    data: RepoInfoData
    commits: Optional[List[RepoInfoCommit]]
    contributors: Optional[List[GitHubContributor]]
