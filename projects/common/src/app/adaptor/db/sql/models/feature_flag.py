
from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import SQLRepository
from app.domain.user import FeatureFlagDTO


# Need join table on company and user

class FeatureFlagTable(Base):
    __tablename__ = "feature_flag"

    name: Mapped[str] = mapped_column(String)
    enabled: Mapped[bool] = mapped_column(Boolean)


class FeatureFlagRepository(SQLRepository):
    model = FeatureFlagTable
    model_dto = FeatureFlagDTO
