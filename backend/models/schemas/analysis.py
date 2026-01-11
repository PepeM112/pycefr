from datetime import datetime
from typing import Dict, List

from models.schemas.class_model import ClassId
from models.schemas.common import BaseSchema, Level, Origin
from models.schemas.repo import RepoInfo


class AnalysisClass(BaseSchema):
    class_id: ClassId
    level: Level | None = None
    instances: int


class AnalysisList(BaseSchema):
    id: int
    name: str
    origin: Origin
    created_at: datetime


class Analysis(BaseSchema):
    id: int
    name: str
    origin: Origin
    created_at: datetime
    classes: List[AnalysisClass]


class AnalysisCreate(BaseSchema):
    name: str
    origin: Origin
    classes: List[AnalysisClass]


class AnalysisUpdate(BaseSchema):
    name: str | None = None
    origin: Origin | None = None
    classes: List[AnalysisClass] | None = None


class AnalysisResult(BaseSchema):
    elements: Dict[str, List[AnalysisClass]]


class FullAnalysisResult(AnalysisResult):
    repo_info: RepoInfo
