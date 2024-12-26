from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from ..repository import DynamoRepository
from .base_model import Base


class ExampleDTO(Base):
    name: str
    url: str
    location: Optional[str] = None
    language: Optional[str] = None


class ExampleUpdateDTO(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    location: Optional[str] = None
    language: Optional[str] = None


class ExampleRepository(DynamoRepository):
    model_dto = ExampleDTO
