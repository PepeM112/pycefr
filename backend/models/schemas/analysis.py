from datetime import datetime
from enum import Enum
from typing import List

from backend.models.schemas.class_model import ClassId
from backend.models.schemas.common import BaseSchema, Level, Origin
from backend.models.schemas.repo import Repo, RepoSummary


class AnalysisStatus(Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisClass(BaseSchema):
    class_id: ClassId
    level: Level | None = None
    instances: int


class AnalysisFile(BaseSchema):
    filename: str
    classes: List[AnalysisClass] = []


class Analysis(BaseSchema):
    id: int | None = None
    name: str | None = None
    origin: Origin | None = None
    status: AnalysisStatus | None = None
    error_message: str | None = None
    file_classes: List[AnalysisFile] | None = None
    created_at: datetime | None = None
    repo: Repo | None = None


class AnalysisSummary(BaseSchema):
    id: int
    name: str | None = None
    origin: Origin | None = None
    status: AnalysisStatus | None = None
    error_message: str | None = None
    created_at: datetime | None = None
    repo: RepoSummary | None = None


class AnalysisCreate(BaseSchema):
    repo_url: str
