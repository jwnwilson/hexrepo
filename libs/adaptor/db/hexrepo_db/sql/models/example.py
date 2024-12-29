from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hexrepo_db.sql.uow import BaseSqlUOW

from ..repository import SQLRepository
from .base_model import Base


class ExampleCreateDTO(BaseModel):
    name: str
    url: str
    location: Optional[str] = None
    language: Optional[str] = None


class ExampleDTO(BaseModel):
    id: UUID


class ExampleUpdateDTO(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    location: Optional[str] = None
    language: Optional[str] = None


# This is only used in tests and will not be used in projects
class ExampleTable(Base):
    __tablename__ = "example"

    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    url: Mapped[str] = mapped_column(String)
    location: Mapped[str] = mapped_column(String, nullable=True)
    language: Mapped[str] = mapped_column(String, nullable=True)


class ExampleRepository(SQLRepository):
    model = ExampleTable
    model_dto = ExampleDTO


class SqlUOW(BaseSqlUOW):
    @property
    def example(self) -> ExampleRepository:
        return ExampleRepository(self.session)
