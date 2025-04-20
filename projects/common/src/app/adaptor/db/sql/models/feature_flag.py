from typing import Any, List, Union

from hexrepo_db.sql.interface import BaseSQLModel
from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import SQLRepository
from pydantic import BaseModel
from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    ForeignKey,
    Row,
    String,
    UniqueConstraint,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.adaptor.db.sql.models.environment import EnvironmentTable
from app.domain.user import (
    FeatureFlagBaseCreateDTO,
    FeatureFlagBaseDTO,
    FeatureFlagCreateDTO,
    FeatureFlagDTO,
    FeatureFlagEnvDTO,
)


class FeatureFlagTable(Base):
    __tablename__ = "feature_flag"

    name: Mapped[str] = mapped_column(String, unique=True)
    environments: Mapped[List["FeatureFlagEnvTable"]] = relationship(
        "FeatureFlagEnvTable",
        back_populates="feature_flag",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    def __str__(self) -> str:
        return f"{self.name} | {self.id}"

    __table_args__ = (
        UniqueConstraint(
            "name",
            name="uq_feature_flag_name",
        ),
    )


class FeatureFlagEnvTable(Base):
    __tablename__ = "feature_flag_env"

    feature_flag_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("feature_flag.id"))
    overrides: Mapped[str] = mapped_column(JSON, nullable=True)
    env: Mapped[str] = mapped_column(String)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    feature_flag: Mapped[FeatureFlagTable] = relationship(
        "FeatureFlagTable", back_populates="environments", lazy="joined"
    )

    def __str__(self) -> str:
        return f"{self.env}"

    __table_args__ = (
        UniqueConstraint(
            "feature_flag_id",
            "env",
            name="uq_feature_flag_env",
        ),
    )


class FeatureFlagRepository(SQLRepository):
    model = FeatureFlagTable
    model_dto = FeatureFlagDTO
    unique_query: bool = True

    def _model_to_dto(self, row: Union[BaseSQLModel, Row[Any]]) -> BaseModel:
        flag_data: dict = row.__dict__
        flag_data["environments"] = [
            FeatureFlagEnvDTO(**env.__dict__) for env in row.environments
        ]
        return self.model_dto(**flag_data)

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
        env_list = self.session.execute(select(EnvironmentTable)).all()
        if not env_list:
            raise ValueError(
                "No environments found in the database, please create environments for feature flags"
            )

        for env in env_list:
            feature_env = FeatureFlagEnvTable(
                env=env[0].name,
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
                FeatureFlagEnvDTO(
                    id=env.id,
                    env=env.env,
                    enabled=env.enabled,
                )
                for env in feature_flag.environments
            ],
        )


class FeatureFlagEnvRepository(SQLRepository):
    model = FeatureFlagEnvTable
    model_dto = FeatureFlagEnvDTO
