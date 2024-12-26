from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from ..respository import MongoRepository
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


class ExampleRepository(MongoRepository):
    model_dto = ExampleDTO
