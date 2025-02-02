from typing import Dict, List, Optional

from hexrepo_db.nosql.dynamo.repository import DynamoRepository
from pydantic import BaseModel

from .base_model import Base


class UserPermissionDTO(Base):
    username: str
    name: str
    email: str
    permissions: Dict[str, bool]
    groups: List[str]    
    cognito_id: Optional[str] = None
    verified: bool


class UserRepository(DynamoRepository):
    model_dto = UserPermissionDTO
