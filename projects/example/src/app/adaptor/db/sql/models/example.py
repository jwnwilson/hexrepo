from typing import TYPE_CHECKING, Dict, List

from monorepo_db.sql.models.base_model import Base
from monorepo_db.sql.repository import SQLRepository
from pydantic import UUID4
from sqlalchemy import UUID, Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, joinedload, mapped_column, relationship

from app.domain.example import ExampleDTO


class ExampleTable(Base):
    __tablename__ = "example"

    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    url: Mapped[str] = mapped_column(String)
    location: Mapped[str] = mapped_column(String, nullable=True)
    language: Mapped[str] = mapped_column(String, nullable=True)


class ExampleRepository(SQLRepository):
    model = ExampleTable
    model_dto = ExampleDTO
