import uuid
from typing import Type

from pydantic import BaseModel

from app.domain.user import CompanyDTO, FeatureFlagDTO, UserPermissionCreateDTO


def generateFeatureFlag():
    return FeatureFlagDTO(
        id=uuid.UUID("12345678-1234-5678-1234-567812345678"),
        name="test",
        created_at="2024-08-30T08:06:10.591198",
        enabled=True,
    )


def generateUserPermissionDTO():
    return UserPermissionCreateDTO(
        id=uuid.UUID("12345678-1234-5678-1234-567812345678"),
        name="test",
        username="test",
        email="test@test.com",
        permissions=[],
        groups=[],
        verified=True,
        company=None,
    )


def generateCompanyDTO():
    return CompanyDTO(name="test", website="test.com")


TEST_DATA_FACTORY = {
    FeatureFlagDTO: generateFeatureFlag,
    CompanyDTO: generateCompanyDTO,
    UserPermissionCreateDTO: generateUserPermissionDTO,
}


def get_test_data(model: Type[BaseModel]) -> BaseModel:
    try:
        return TEST_DATA_FACTORY[model]()
    except KeyError:
        raise Exception(f"Test data factory not implemented for {model}")
