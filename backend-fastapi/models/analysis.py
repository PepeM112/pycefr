from pydantic import BaseModel
from datetime import datetime
from models.common import Level, Origin
from models.class_model import ClassEnum


class AnalysisClass(BaseModel):
    id: int
    analysis_id: int
    class_id: ClassEnum
    level: Level
    instances: int


class Analysis(BaseModel):
    id: int
    name: str
    origin: Origin
    created_at: datetime


class AnalysisCreate(BaseModel):
    name: str
    origin: Origin
    classes: list[ClassEnum]


class AnalysisUpdate(BaseModel):
    name: str | None = None
    origin: Origin | None = None
    classes: list[ClassEnum] | None = None
