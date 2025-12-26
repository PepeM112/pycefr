from pydantic import BaseModel
from datetime import datetime
from models.common import Level, Origin
from models.class_model import ClassId


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
    classes: list[AnalysisClass]


class AnalysisCreate(BaseModel):
    name: str
    origin: Origin
    classes: list[AnalysisClass]


class AnalysisUpdate(BaseModel):
    name: str | None = None
    origin: Origin | None = None
    classes: list[AnalysisClass] | None = None
