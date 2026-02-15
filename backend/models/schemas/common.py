from datetime import datetime
from enum import Enum
from typing import Dict, Generic, List, TypeVar

from pydantic import BaseModel, ConfigDict, Field, GetJsonSchemaHandler
from pydantic.alias_generators import to_camel
from pydantic_core import CoreSchema

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class NamedEnum(Enum):
    """Base Enum que exporta nombres de variables a OpenAPI para Hey API."""

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler) -> Dict[str, object]:
        json_schema = handler(core_schema)

        json_schema["x-enum-varnames"] = [e.name for e in cls]

        return json_schema


class NamedStrEnum(str, NamedEnum):
    """Base para Enums de tipo String con nombres exportables."""

    pass


class NamedIntEnum(int, NamedEnum):
    """Base para Enums de tipo Integer con nombres exportables."""

    pass


class Level(NamedIntEnum):
    UNKNOWN = 0
    A1 = 1
    A2 = 2
    B1 = 3
    B2 = 4
    C1 = 5
    C2 = 6


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


class SortDirection(NamedIntEnum):
    UNKNOWN = 0
    ASC = 1
    DESC = 2


class Sorting(BaseSchema, Generic[T]):
    column: T
    direction: SortDirection


class DateRange(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_: datetime | None = Field(None, alias="from")
    to: datetime | None = None


class EntityLabel(BaseSchema):
    id: int
    label: str


class EntityLabelString(BaseSchema):
    id: str
    label: str
