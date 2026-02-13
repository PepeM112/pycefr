from datetime import datetime
from enum import Enum
from typing import List

from backend.models.schemas.class_model import ClassId
from backend.models.schemas.common import BaseSchema, NamedIntEnum, Origin
from backend.models.schemas.repo import RepoPublic, RepoSummaryPublic


class AnalysisStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"


class AnalysisClassPublic(BaseSchema):
    class_id: ClassId
    instances: int


class AnalysisFilePublic(BaseSchema):
    filename: str
    classes: List[AnalysisClassPublic] = []


class AnalysisPublic(BaseSchema):
    id: int
    name: str
    origin: Origin
    status: AnalysisStatus
    error_message: str | None = None
    file_classes: List[AnalysisFilePublic] = []
    created_at: datetime
    repo: RepoPublic | None = None


class AnalysisSummaryPublic(BaseSchema):
    id: int
    name: str
    origin: Origin
    status: AnalysisStatus
    error_message: str | None = None
    created_at: datetime
    repo: RepoSummaryPublic | None = None


class AnalysisCreate(BaseSchema):
    repo_url: str


class AnalysisSortColumn(NamedIntEnum):
    UNKNOWN = 0
    ID = 1
    NAME = 2
    STATUS = 3
    CREATED_AT = 4


class AnalysisFilters(BaseSchema):
    name: List[str] | None = None
    owner: List[int] | None = None
    status: List[AnalysisStatus] | None = None
    created_after: str | None = None
    created_before: str | None = None
