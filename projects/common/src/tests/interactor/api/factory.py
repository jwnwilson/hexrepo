import uuid
from typing import Optional, Type

from pydantic import BaseModel
from polyfactory.factories.pydantic_factory import ModelFactory

from app.domain.user import (
    CompanyDTO,
    CompanyCreateDTO,
    FeatureFlagDTO,
    FeatureFlagCreateDTO,
    GroupPermissionDTO,
    PermissionDTO,
    UserPermissionCreateDTO,
    UserPermissionDTO,
)


class FeatureFlagFactory(ModelFactory[FeatureFlagDTO]):
    @classmethod
    def company_id(cls) -> Optional[uuid.UUID]:
        return None

class FeatureFlagCreateFactory(ModelFactory[FeatureFlagCreateDTO]): ...
class UserPermissionFactory(ModelFactory[UserPermissionDTO]): ...
class CompanyFactory(ModelFactory[CompanyDTO]): ...
class CompanyCreateFactory(ModelFactory[CompanyCreateDTO]): ...
class GroupPermissionFactory(ModelFactory[GroupPermissionDTO]): ...
class PermissionFactory(ModelFactory[PermissionDTO]): ...
class UserPermissionCreateFactory(ModelFactory[UserPermissionCreateDTO]): ...


TEST_DATA_FACTORY = {
    FeatureFlagDTO: FeatureFlagFactory,
    FeatureFlagCreateDTO: FeatureFlagCreateFactory,
    CompanyDTO: CompanyFactory,
    CompanyCreateDTO: CompanyCreateFactory,
    UserPermissionDTO: UserPermissionFactory,
    UserPermissionCreateDTO: UserPermissionCreateFactory,
    GroupPermissionDTO: GroupPermissionFactory,
    PermissionDTO: PermissionFactory,
}


def get_test_data(model: Type[BaseModel]) -> BaseModel:
    try:
        return TEST_DATA_FACTORY[model].build()
    except KeyError:
        raise Exception(f"Test data factory not implemented for {model}")
