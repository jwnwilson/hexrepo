from hexrepo_db.sql import BaseSqlUOW

from .models.company import CompanyRepository
from .models.feature_flag import FeatureFlagRepository
from .models.group import GroupRepository
from .models.permission import PermissionRepository
from .models.user import UserRepository


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

    @property
    def feature_flag(self) -> FeatureFlagRepository:
        return FeatureFlagRepository(self.session)

    @property
    def company(self) -> CompanyRepository:
        return CompanyRepository(self.session)
