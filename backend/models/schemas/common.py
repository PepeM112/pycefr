from enum import Enum
from typing import Generic, List, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class Level(str, Enum):
    UNKNOWN = "unknown"
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class Origin(str, Enum):
    UNKNOWN = "UNKNOWN"
    USER = "USER"
    GITHUB = "GITHUB"
    LOCAL = "LOCAL"


class Pagination(BaseSchema):
    page: int
    per_page: int
    total: int


class PaginatedResponse(BaseSchema, Generic[T]):
    pagination: Pagination
    elements: List[T]
