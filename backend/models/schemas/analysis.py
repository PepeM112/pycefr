from datetime import datetime
from enum import Enum
from typing import List, Optional

from backend.models.schemas.class_model import ClassId
from backend.models.schemas.common import BaseSchema, Origin
from backend.models.schemas.repo import RepoPublic, RepoSummaryPublic


class AnalysisStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


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
    error_message: Optional[str] = None
    file_classes: List[AnalysisFilePublic] = []
    created_at: datetime
    repo: Optional[RepoPublic] = None


class AnalysisSummaryPublic(BaseSchema):
    id: int
    name: str
    origin: Origin
    status: AnalysisStatus
    created_at: datetime
    repo: Optional[RepoSummaryPublic] = None


class AnalysisCreate(BaseSchema):
    repo_url: str
