from datetime import datetime
from typing import List

from backend.models.schemas.common import BaseSchema


class TopConstruct(BaseSchema):
    name: str
    level: str
    count: int


class RecentAnalysis(BaseSchema):
    id: int
    repo_name: str
    status: str
    created_at: datetime


class DashboardStats(BaseSchema):
    total_analyses: int
    completed: int
    failed: int
    in_progress: int
    level_distribution: dict[str, int]
    top_constructs: List[TopConstruct]
    recent_analyses: List[RecentAnalysis]
