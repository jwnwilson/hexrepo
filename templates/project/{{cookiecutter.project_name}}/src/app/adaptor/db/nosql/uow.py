from monorepo_db.nosql import BaseDynamoUOW
from .models.example import ExampleRepository


class DynamoUOW(BaseDynamoUOW):
    # Used for testing
    def create_all(self) -> None:
        self.example.create_table()

    def drop_all(self) -> None:
        self.example.delete_table()

    @property
    def example(self) -> ExampleRepository:
        return ExampleRepository(
            self.resource, table="example", required_filters=self._required_filters
        )