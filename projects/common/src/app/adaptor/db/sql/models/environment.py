from typing import Any

from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import SQLRepository
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.user import EnvironmentDTO


class EnvironmentTable(Base):
    __tablename__ = "environment"

    name: Mapped[str] = mapped_column(String)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB)


class EnvironmentRepository(SQLRepository):
    model = EnvironmentTable
    model_dto = EnvironmentDTO
