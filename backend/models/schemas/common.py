from enum import Enum, IntEnum
from typing import Generic, List, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class Level(IntEnum, Enum):
    UNKNOWN = 0
    A1 = 1
    A2 = 2
    B1 = 3
    B2 = 4
    C1 = 5
    C2 = 6


class Origin(IntEnum, Enum):
    UNKNOWN = 0
    USER = 1
    GITHUB = 2
    LOCAL = 3


class Pagination(BaseSchema):
    page: int
    per_page: int
    total: int


class PaginatedResponse(BaseSchema, Generic[T]):
    pagination: Pagination
    elements: List[T]
