from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ExampleDTO(BaseModel):
    id: UUID
    name: str
    url: str
    location: str


class CreateExampleDTO(BaseModel):
    name: str
    url: str
    location: str


class UpdateExampleDTO(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    location: Optional[str] = None

