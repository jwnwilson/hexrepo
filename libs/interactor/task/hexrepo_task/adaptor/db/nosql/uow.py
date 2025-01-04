from hexrepo_db.nosql import BaseDynamoUOW

from hexrepo_task.config import config

from .models.task import TaskRepository


class QueueUOW(BaseDynamoUOW):
    # Used for testing
    def create_all(self) -> None:
        self.task.create_table()

    def drop_all(self) -> None:
        self.task.delete_table()

    @property
    def task(self) -> TaskRepository:
        project: str = config.project
        table_name: str = "tasks"
        env: str = config.environment
        full_table_name = f"{project}_{env}_{table_name}"
        return TaskRepository(
            self.resource,
            table=full_table_name,
            required_filters=self._required_filters,
        )
