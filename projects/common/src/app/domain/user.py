from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel

from hexrepo_db.interface import PaginatedData
from app.adaptor.db.interface import UOW


class Token(BaseModel):
    access_token: str
    token_type: str


class UserPermissionCreateDTO(BaseModel):
    username: str
    name: str
    email: str
    permissions: List[Dict[str, Any]]
    groups: List[Dict[str, Any]]
    cognito_id: Optional[str] = None
    verified: bool
    company: Optional[Dict[str, Any]]


class UserPermissionDTO(UserPermissionCreateDTO):
    id: UUID

    def is_superuser(self) -> bool:
        permissions = set([x["name"] for x in self.permissions])
        return "superadmin" in permissions


class GroupPermissionDTO(BaseModel):
    id: UUID
    name: str
    users: List[Dict[str, Any]]
    permissions: List[Dict[str, Any]]


class PermissionDTO(BaseModel):
    id: UUID
    name: str
    users: List[Dict[str, Any]]
    groups: List[Dict[str, Any]]


class CompanyDTO(BaseModel):
    name: str
    website: str


class FeatureFlagDTO(BaseModel):
    name: str
    enabled: bool
    company_id: Optional[UUID] = None


def get_user(uow: UOW, username: str) -> UserPermissionDTO:
    user_data: PaginatedData[UserPermissionDTO] = uow.user.read_multi(
        filters=dict(username=username)
    )
    if not user_data.results:
        raise ValueError("User not found")
    return user_data.results[0]
