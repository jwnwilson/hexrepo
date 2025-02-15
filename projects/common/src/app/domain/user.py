from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


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
