
from typing import Optional
from sqlalchemy import UUID, ForeignKey, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import SQLRepository
from app.domain.user import FeatureFlagDTO


# Need join table on company and user

class FeatureFlagTable(Base):
    __tablename__ = "feature_flag"

    name: Mapped[str] = mapped_column(String)
    enabled: Mapped[bool] = mapped_column(Boolean)
    company_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("company.id"), nullable=True)
    company: Mapped["CompanyTable"] = relationship("CompanyTable")

    def __str__(self) -> str:
        return f"{self.name} | {self.id}"


class FeatureFlagRepository(SQLRepository):
    model = FeatureFlagTable
    model_dto = FeatureFlagDTO
