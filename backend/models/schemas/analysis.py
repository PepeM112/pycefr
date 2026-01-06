from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel

from models.schemas.class_model import ClassId
from models.schemas.common import Level, Origin
from models.schemas.repo import RepoInfo


class AnalysisClass(BaseModel):
    class_id: ClassId
    level: Level | None = None
    instances: int


class AnalysisList(BaseModel):
    id: int
    name: str
    origin: Origin
    created_at: datetime


class Analysis(BaseModel):
    id: int
    name: str
    origin: Origin
    created_at: datetime
    classes: List[AnalysisClass]


class AnalysisCreate(BaseModel):
    name: str
    origin: Origin
    classes: List[AnalysisClass]


class AnalysisUpdate(BaseModel):
    name: str | None = None
    origin: Origin | None = None
    classes: List[AnalysisClass] | None = None


class AnalysisResult(BaseModel):
    elements: Dict[str, List[AnalysisClass]]


class FullAnalysisResult(AnalysisResult):
    repo_info: RepoInfo
