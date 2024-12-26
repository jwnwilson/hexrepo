from monorepo_db.sql import SqlUOW

from .models.example import ExampleRepository


class SqlUOW(SqlUOW):
    @property
    def example(self) -> ExampleRepository:
        return ExampleRepository(self.session)
