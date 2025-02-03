from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel
from loguru import logger

class Token(BaseModel):
    access_token: str
    token_type: str


class UserPermissionDTO(BaseModel):
    id: UUID
    username: str
    name: str
    email: str
    permissions: List[str]
    groups: List[str]
    cognito_id: Optional[str] = None
    verified: bool
    company: Optional[str]


class GroupPermissionDTO(BaseModel):
    id: UUID
    name: str
    users: List[str]
    permissions: List[str]


class PermissionDTO(BaseModel):
    id: UUID
    name: str
    users: List[str]
    groups: List[str]


class CompanyDTO(BaseModel):
    name: str
    website: str


class FeatureFlagDTO(BaseModel):
    name: str
    enabled: bool
