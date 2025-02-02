from hexrepo_db.sql import BaseSqlUOW
from .models.user import UserRepository
from .models.group import GroupRepository
from .models.permission import PermissionRepository

class SqlUOW(BaseSqlUOW):

    @property
    def user(self) -> UserRepository:
        return UserRepository(self.session)
    
    @property
    def group(self) -> GroupRepository:
        return GroupRepository(self.session)
    
    @property
    def permission(self) -> PermissionRepository:
        return PermissionRepository(self.session)
