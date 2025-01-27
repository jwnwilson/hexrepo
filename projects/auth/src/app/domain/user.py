from typing import Dict, List
from pydantic import BaseModel
from loguru import logger
from app.adaptor.db.nosql.uow import DynamoUOW 

class Token(BaseModel):
    access_token: str
    token_type: str


class UserPermissionDTO(BaseModel):
    username: str
    name: str
    email: str
    permissions: Dict[str, bool]
    groups: List[str]


def get_user_data(username: str, uow: DynamoUOW) -> UserPermissionDTO:
    breakpoint()
    logger.info(f"Getting user data for {username}")
    user = uow.user.read_multi(filters={"username": username})
    if not user:
        logger.error(f"User: {username} not found")
        raise ValueError("User not found")
    return user.results[0]
