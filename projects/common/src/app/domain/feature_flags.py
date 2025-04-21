from typing import Any, Dict, List
from uuid import UUID
from app.domain.user import UserPermissionDTO
from pydantic import BaseModel
from app.adaptor.db.interface import UOW

from hexrepo_db.interface import PaginatedData


class FeatureFlagBaseDTO(BaseModel):
    id: UUID
    name: str


class FeatureFlagBaseCreateDTO(BaseModel):
    name: str


class FeatureFlagEnvCreateDTO(BaseModel):
    env: str
    enabled: bool
    overrides: Dict[str, Any] | None = None


class FeatureFlagEnvDTO(BaseModel):
    id: UUID
    env: str
    enabled: bool
    overrides: Dict[str, Any] | None = None


class FeatureFlagCreateDTO(BaseModel):
    name: str
    enabled: bool = False


class FeatureFlagUpdateDTO(BaseModel):
    id: UUID
    name: str


class FeatureFlagDTO(BaseModel):
    id: UUID
    name: str
    environments: List[FeatureFlagEnvDTO] = []


class FlagsArgs(BaseModel):
    flags: list[str]
    env: str


class FeatureFlagGetDTO(BaseModel):
    id: UUID
    name: str
    env: str
    enabled: bool
    overrides: Dict[str, Any] | None = None


def get_feature_flag_data(uow: UOW, flag_args: FlagsArgs) -> list[FeatureFlagGetDTO]:
    # Get feature flags filtering by env, user and company if provided
    # return list of feature flags
    flag_names: list[str] = [flag for flag in flag_args.flags]
    feature_flags: PaginatedData[FeatureFlagDTO] = uow.feature_flag.read_multi(
        filters={"name__in": flag_names, "environments.env": flag_args.env},
    )
    feature_flag_get_dto: list[FeatureFlagGetDTO] = []
    for flag in feature_flags.results:
        feature_flag_get_dto.append(
            FeatureFlagGetDTO(
                id=flag.id,
                name=flag.name,
                env=flag_args.env,
                enabled=any(
                    [
                        env.enabled
                        for env in flag.environments
                        if env.env == flag_args.env
                    ]
                ),
                overrides=next(
                    env.overrides
                    for env in flag.environments
                    if env.env == flag_args.env
                )
            )
        )
    return feature_flag_get_dto