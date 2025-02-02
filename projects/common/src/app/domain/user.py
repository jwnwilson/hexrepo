from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel
from loguru import logger

class Token(BaseModel):
    access_token: str
    token_type: str


class UserPermissionDTO(BaseModel):
    username: str
    name: str
    email: str
    permissions: Dict[str, bool]
    groups: List[str]
    cognito_id: Optional[str] = None
    verified: bool
    company: Optional[str]


class GroupPermissionDTO(BaseModel):
    name: str
    users: List[str]
    permissions: List[str]


class PermissionDTO(BaseModel):
    name: str
    users: List[str]
    groups: List[str]


class CompanyDTO(BaseModel):
    name: str
    website: str


class FeatureFlagDTO(BaseModel):
    name: str
    enabled: bool
