from typing import Dict, List
from uuid import UUID
from pydantic import BaseModel
from loguru import logger
from app.adaptor.db.nosql.uow import DynamoUOW 
from app.adaptor.db.nosql.models.group import GroupPermissionDTO

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


class UserManager:
    def __init__(self, uow: DynamoUOW):
        self.uow = uow
    
    def read_by_username(self, username: str) -> UserPermissionDTO:
        logger.info(f"Getting user data for {username}")
        user = self.uow.user.read_multi(filters={"username": username})
        if not user:
            logger.error(f"User: {username} not found")
            raise ValueError("User not found")
        return user.results[0]
    
    def create(self, user: UserPermissionDTO) -> UserPermissionDTO:
        logger.info(f"Creating user {user.username}")
        return self.uow.user.create(user)
    
    def update(self, id: UUID, user: UserPermissionDTO) -> UserPermissionDTO:
        logger.info(f"Updating user {id}")
        return self.uow.user.update(id, user)
    
    def delete(self, username: str) -> None:
        logger.info(f"Deleting user {username}")
        return self.uow.user.delete(username)


class GroupManager:
    def __init__(self, uow: DynamoUOW):
        self.uow = uow
    
    def read(self, id: UUID) -> GroupPermissionDTO:
        logger.info(f"Getting permission data for {id}")
        return self.uow.user.read(id)
    
    def read_multi(self, filters: Dict[str, str]) -> List[GroupPermissionDTO]:
        logger.info(f"Getting permission data for {filters}")
        return self.uow.user.read_multi(filters)
    
    def create(self, group: GroupPermissionDTO) -> GroupPermissionDTO:
        logger.info(f"Creating group {group.name}")
        return self.uow.user.create(group)
    
    def update(self, id: UUID, group: GroupPermissionDTO) -> GroupPermissionDTO:
        logger.info(f"Updating group {id}")
        return self.uow.user.update(id, group)
    
    def delete(self, id: UUID) -> None:
        logger.info(f"Deleting group {id}")
        return self.uow.user.delete(id)


class UserInstance:
    def __init__(self, uow: DynamoUOW, username: str):
        self.uow = uow
        self.group_manager: GroupManager = GroupManager(uow)
        self.user_manager: UserManager = UserManager(uow)
        self.user_data: UserPermissionDTO = self.user_manager.read_by_username(username)

    def has_permission(self, permission: str) -> bool:
        return permission in self.user_data.permissions

    def update_permissions(self):
        def flatten(xss):
            return [x for xs in xss for x in xs]

        # Get permissions for all groups
        groups: List[GroupPermissionDTO] = self.group_manager.read_multi(
            filters={"id__in": self.user_data.groups}
        )
        # Update permissions for user
        permissions = flatten([group.perm for group in groups])
        self.user_data.permissions = permissions
        self.uow.user.update(self.user_data.username, self.user_data)

    def add_to_group(self, group: str) -> None:
        self.user_data.groups.append(group)
        self.update_permissions()
        self.uow.user.update(self.user_data.username, self.user_data)

    def remove_from_group(self, group: str) -> None:
        self.user_data.groups.remove(group)
        self.update_permissions()
        self.uow.user.update(self.user_data.username, self.user_data)
    