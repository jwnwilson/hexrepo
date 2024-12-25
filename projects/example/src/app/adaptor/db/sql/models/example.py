
from monorepo_db.sql.models.base_model import Base
from monorepo_db.sql.repository import SQLRepository
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

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
