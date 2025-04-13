from typing import TYPE_CHECKING, Any, List, Type

from app.adaptor.db.sql.models.environment import EnvironmentTable

from hexrepo_db.sql.interface import Query
from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import DefaultQuery, SQLRepository
from sqlalchemy import JSON, UUID, Boolean, ForeignKey, Select, String, UniqueConstraint, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.user import FeatureFlagBaseCreateDTO, FeatureFlagBaseDTO, FeatureFlagCreateDTO, FeatureFlagDTO, FeatureFlagEnvDTO


class FeatureFlagTable(Base):
    __tablename__ = "feature_flag"

    name: Mapped[str] = mapped_column(String, unique=True)
    environments: Mapped[List["FeatureFlagEnvTable"]] = relationship(
        "FeatureFlagEnvTable",
        back_populates="feature_flag",
        cascade="all, delete-orphan",
    )

    def __str__(self) -> str:
        return f"{self.name} | {self.id}"
    

class FeatureFlagEnvTable(Base):
    __tablename__ = "feature_flag_env"

    feature_flag_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("feature_flag.id")
    )
    overrides: Mapped[str] = mapped_column(JSON)
    env: Mapped[str] = mapped_column(String)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint(
            "feature_flag_id",
            "env",
            name="uq_feature_flag_env",
        ),
    )


class FeatureQueryLogic(DefaultQuery):
    def query_select(self) -> Select[Any]:
        return (
            Select(self.model)
            .outerjoin(FeatureFlagEnvTable)
        )


class FeatureFlagRepository(SQLRepository):
    model = FeatureFlagTable
    model_dto = FeatureFlagDTO
    query_logic: Type[Query] = FeatureQueryLogic

    def create(self, obj_in: FeatureFlagCreateDTO) -> FeatureFlagDTO:
        # Get of Create feature flag record
        feature_flag: FeatureFlagBaseDTO
        feature_flag_base_obj = FeatureFlagBaseCreateDTO(
            name=obj_in.name,
        )
        feature_flag = self.query.parse_dto(feature_flag_base_obj)
        self.session.add(feature_flag)
        self.session.flush()

        # Create env feature flag record if it doesn't exist
        env_list = select(EnvironmentTable).all()
        for env in env_list:
            feature_env = FeatureFlagEnvTable(
                env=env.name,
                enabled=obj_in.enabled,
                feature_flag_id=feature_flag.id,
            )
            self.session.add(feature_env)
        self.session.flush()
        self.session.refresh(feature_flag)
        return FeatureFlagDTO(
            id=feature_flag.id,
            name=feature_flag.name,
            environments=[
                FeatureFlagDTO(
                    id=env.id,
                    env=env.env,
                    enabled=env.enabled,
                )
                for env in feature_flag.environments
            ],
        )


class FeatureEnvQueryLogic(DefaultQuery):
    def query_select(self) -> Select[Any]:
        return (
            Select(self.model)
            .outerjoin(FeatureFlagTable)
        )

class FeatureFlagEnvRepository(SQLRepository):
    model = FeatureFlagEnvTable
    model_dto = FeatureFlagEnvDTO
    query_logic: Type[Query] = FeatureEnvQueryLogic


