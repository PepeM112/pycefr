from datetime import datetime
from typing import Dict, List

from backend.models.schemas.class_model import ClassId
from backend.models.schemas.common import BaseSchema, Level, Origin
from backend.models.schemas.repo import RepoInfo


class AnalysisClass(BaseSchema):
    class_id: ClassId
    level: Level | None = None
    instances: int


class AnalysisList(BaseSchema):
    id: int
    name: str
    origin: Origin
    created_at: datetime
    total_hours: float


class Analysis(AnalysisList):
    classes: List[AnalysisClass]


class AnalysisCreate(BaseSchema):
    name: str
    origin: Origin
    total_hours: float
    classes: List[AnalysisClass]


class AnalysisUpdate(BaseSchema):
    name: str | None = None
    origin: Origin | None = None
    total_hours: float | None = None
    classes: List[AnalysisClass] | None = None


class AnalysisResult(BaseSchema):
    elements: Dict[str, List[AnalysisClass]]


class FullAnalysisResult(AnalysisResult):
    repo_info: RepoInfo
