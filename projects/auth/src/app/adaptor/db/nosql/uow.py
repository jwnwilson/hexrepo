from hexrepo_db.nosql import BaseDynamoUOW

from app.config import config

from .models.user import UserRepository


class DynamoUOW(BaseDynamoUOW):
    # Used for testing
    def create_all(self) -> None:
        self.example.create_table()

    def drop_all(self) -> None:
        self.example.delete_table()

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
