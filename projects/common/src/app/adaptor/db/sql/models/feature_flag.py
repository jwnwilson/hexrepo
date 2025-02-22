from typing import TYPE_CHECKING

from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import SQLRepository
from sqlalchemy import UUID, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.user import FeatureFlagDTO

if TYPE_CHECKING:
    from .company import CompanyTable


# Need join table on company and user


class FeatureFlagTable(Base):
    __tablename__ = "feature_flag"

    name: Mapped[str] = mapped_column(String)
    enabled: Mapped[bool] = mapped_column(Boolean)
    company_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("company.id"), nullable=True
    )
    company: Mapped["CompanyTable"] = relationship("CompanyTable")

    def __str__(self) -> str:
        return f"{self.name} | {self.id}"


class FeatureFlagRepository(SQLRepository):
    model = FeatureFlagTable
    model_dto = FeatureFlagDTO
