from typing import Dict, List, Optional

from hexrepo_db.nosql.dynamo.repository import DynamoRepository
from pydantic import BaseModel

from .base_model import Base


class GroupPermissionDTO(Base):
    name: str
    permissions: Dict[str, bool]


class GroupRepository(DynamoRepository):
    model_dto = GroupPermissionDTO
