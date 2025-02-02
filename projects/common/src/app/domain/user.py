from typing import Dict, List
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
    cognito_id: str
    verified: bool


class GroupPermissionDTO(BaseModel):
    name: str
    users: List[str]
    permissions: Dict[str, bool]
