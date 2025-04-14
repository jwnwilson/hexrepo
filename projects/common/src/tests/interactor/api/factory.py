import uuid
from typing import Dict, List, Optional, Type

from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel

from app.domain.user import (
    CompanyCreateDTO,
    CompanyDTO,
    FeatureFlagCreateDTO,
    FeatureFlagDTO,
    FeatureFlagEnvDTO,
    FeatureFlagUpdateDTO,
    GroupPermissionDTO,
    PermissionDTO,
    UserPermissionCreateDTO,
    UserPermissionDTO,
)


class FeatureFlagFactory(ModelFactory[FeatureFlagDTO]):
    @classmethod
    def environments(cls) -> list[FeatureFlagEnvDTO]:
        return []


class FeatureFlagCreateFactory(ModelFactory[FeatureFlagCreateDTO]): ...


class FeatureFlagUpdateFactory(ModelFactory[FeatureFlagUpdateDTO]): ...


class CompanyFactory(ModelFactory[CompanyDTO]): ...


class CompanyCreateFactory(ModelFactory[CompanyCreateDTO]): ...


class GroupPermissionFactory(ModelFactory[GroupPermissionDTO]):
    @classmethod
    def users(cls) -> List[Dict]:
        return []

    @classmethod
    def permissions(cls) -> List[Dict]:
        return []


class PermissionFactory(ModelFactory[PermissionDTO]):
    @classmethod
    def users(cls) -> List[Dict]:
        return []

    @classmethod
    def groups(cls) -> List[Dict]:
        return []


class UserPermissionFactory(ModelFactory[UserPermissionDTO]):
    @classmethod
    def permissions(cls) -> List[Dict]:
        return []

    @classmethod
    def groups(cls) -> List[Dict]:
        return []

    @classmethod
    def company_id(cls) -> Optional[uuid.UUID]:
        return None


class UserPermissionCreateFactory(ModelFactory[UserPermissionCreateDTO]):
    @classmethod
    def permissions(cls) -> List[Dict]:
        return []

    @classmethod
    def groups(cls) -> List[Dict]:
        return []

    @classmethod
    def company_id(cls) -> Optional[uuid.UUID]:
        return None


TEST_DATA_FACTORY = {
    FeatureFlagDTO: FeatureFlagFactory,
    FeatureFlagCreateDTO: FeatureFlagCreateFactory,
    FeatureFlagUpdateDTO: FeatureFlagUpdateFactory,
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
