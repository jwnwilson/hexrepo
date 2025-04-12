from typing import TYPE_CHECKING, Any, Type

from hexrepo_db.sql.interface import Query
from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import DefaultQuery, SQLRepository
from sqlalchemy import UUID, Boolean, ForeignKey, Select, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.user import FeatureFlagBaseCreateDTO, FeatureFlagBaseDTO, FeatureFlagCreateDTO, FeatureFlagDTO

if TYPE_CHECKING:
    from .company import CompanyTable
    from .user import UserTable


class FeatureFlagTable(Base):
    __tablename__ = "feature_flag"

    name: Mapped[str] = mapped_column(String)

    def __str__(self) -> str:
        return f"{self.name} | {self.id}"
    

class FeatureFlagEnvTable(Base):
    __tablename__ = "feature_flag_env"

    feature_flag_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("feature_flag.id")
    )
    env: Mapped[str] = mapped_column(String)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)


class FeatureFlagOverride(Base):
    __tablename__ = "feature_flag_override"

    company_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("company.id"), nullable=True
    )
    user_id:Mapped[UUID] = mapped_column(
        UUID, ForeignKey("user.id"), nullable=True
    )
    feature_flag_env_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("feature_flag_env.id")
    )
    feature_flag_env: Mapped[FeatureFlagEnvTable] = relationship("FeatureFlagEnvTable")
    company: Mapped["CompanyTable"] = relationship("CompanyTable")
    user: Mapped["UserTable"] = relationship("UserTable")


class FeatureQueryLogic(DefaultQuery):
    def query_select(self) -> Select[Any]:
        return (
            Select(self.model)
            .outerjoin(FeatureFlagEnvTable)
            .outerjoin(FeatureFlagOverride)
        )


class FeatureFlagRepository(SQLRepository):
    model = FeatureFlagTable
    model_dto = FeatureFlagDTO
    query_logic: Type[Query] = FeatureQueryLogic

    def create(self, obj_in: FeatureFlagCreateDTO) -> FeatureFlagDTO:
        # Get of Create feature flag record
        breakpoint()
        feature_flag: FeatureFlagBaseDTO
        existing_feature_flag = self.read_multi(filters=dict(name=obj_in.name))
        if not existing_feature_flag.results:
            breakpoint()
            feature_flag_base_obj = FeatureFlagBaseCreateDTO(
                name=obj_in.name
            )
            feature_flag = super().create(feature_flag_base_obj)
        else:
            feature_flag = existing_feature_flag.results[0]

        # Create env feature flag record if it doesn't exist
        feature_env = FeatureFlagEnvTable(
            env=obj_in.env,
            enabled=obj_in.enabled,
            feature_flag_id=feature_flag.id,
        )
        self.session.add(feature_env)
        self.session.flush()
        return FeatureFlagDTO(
            id=feature_flag.id,
            name=feature_flag.name,
            env=obj_in.env,
            enabled=obj_in.enabled,
        )
    
