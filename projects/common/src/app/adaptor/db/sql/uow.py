from hexrepo_db.sql import BaseSqlUOW
from sqlalchemy.orm import configure_mappers
from sqlalchemy_continuum import make_versioned

# This needs to be done before model definition for versioning to work
make_versioned(user_cls=None)

from .models.company import CompanyRepository  # noqa: E402
from .models.environment import EnvironmentRepository  # noqa: E402
from .models.feature_flag import FeatureFlagRepository  # noqa: E402
from .models.group import GroupRepository  # noqa: E402
from .models.permission import PermissionRepository  # noqa: E402
from .models.user import UserRepository  # noqa: E402

# This nees to be done after model definition for versioning to work
configure_mappers()


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

    @property
    def environment(self) -> CompanyRepository:
        return EnvironmentRepository(self.session)
