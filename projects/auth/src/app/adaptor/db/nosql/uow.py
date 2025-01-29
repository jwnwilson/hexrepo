from hexrepo_db.nosql import BaseDynamoUOW

from app.config import config

from .models.user import UserRepository
from .models.group import GroupRepository


class DynamoUOW(BaseDynamoUOW):
    # Used for testing
    def create_all(self) -> None:
        self.user.create_table()
        self.group.create_table()

    def drop_all(self) -> None:
        self.user.delete_table()
        self.group.delete_table()

    @property
    def user(self) -> UserRepository:
        project: str = config.PROJECT
        table_name: str = "user"
        env: str = config.ENVIRONMENT
        full_table_name = f"{project}_{env}_{table_name}"
        return UserRepository(
            self.resource,
            table=full_table_name,
            required_filters=self._required_filters,
        )
    
    @property
    def group(self) -> GroupRepository:
        project: str = config.PROJECT
        table_name: str = "group"
        env: str = config.ENVIRONMENT
        full_table_name = f"{project}_{env}_{table_name}"
        return GroupRepository(
            self.resource,
            table=full_table_name,
            required_filters=self._required_filters,
        )
