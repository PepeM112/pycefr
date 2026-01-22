from datetime import datetime
from enum import Enum
from typing import List

from backend.models.schemas.class_model import ClassId
from backend.models.schemas.common import BaseSchema, Level, Origin
from backend.models.schemas.repo import Repo


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
    classes: List[AnalysisClass]


class Analysis(BaseSchema):
    id: int | None = None
    name: str | None = None
    origin: Origin = Origin.GITHUB
    status: AnalysisStatus = AnalysisStatus.IN_PROGRESS
    file_classes: List[AnalysisFile] = []
    repo: Repo | None = None


class AnalysisSummary(BaseSchema):
    id: int
    name: str | None = None
    status: AnalysisStatus
    origin: Origin
    repo_name: str | None = None
    repo_url: str | None = None
    created_at: datetime
    classes: List[AnalysisClass] = []  # total classes in the analysis, not per file
    estimated_hours: float | None = None


class AnalysisCreate(BaseSchema):
    repo_url: str
