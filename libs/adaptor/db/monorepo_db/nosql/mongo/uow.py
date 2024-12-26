import contextlib
from typing import Dict, Optional
from pymongo import MongoClient
from ...interface import UOW
from .models.example import ExampleRepository


class DynamoUOW(UOW):
    def __init__(self, db_url: str, required_filters: Optional[Dict[str, str]] = None):
        self._required_filters: Optional[Dict[str, str]] = required_filters
        # Auth using env vars
        self.client: MongoClient = MongoClient(db_url)

    @contextlib.contextmanager
    def transaction_context_manager(self):
        with self.client.start_session() as session:
            with session.start_transaction():
                yield

    # Used for testing
    def create_all(self) -> None:
        self.example.create_table()

    def drop_all(self) -> None:
        self.example.delete_table()
    
    @property
    def example(self) -> ExampleRepository:
        return ExampleRepository(self.client, table="example", required_filters=self._required_filters)
