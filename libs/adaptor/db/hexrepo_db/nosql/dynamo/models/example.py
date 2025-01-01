from typing import Optional

from pydantic import BaseModel

from ..repository import DynamoRepository
from ..uow import BaseDynamoUOW
from .base_model import Base


class ExampleDTO(Base):
    name: str
    url: str
    location: Optional[str] = None
    language: Optional[str] = None


class ExampleUpdateDTO(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    location: Optional[str] = None
    language: Optional[str] = None


class ExampleRepository(DynamoRepository):
    model_dto = ExampleDTO


class ExampleUOW(BaseDynamoUOW):
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
