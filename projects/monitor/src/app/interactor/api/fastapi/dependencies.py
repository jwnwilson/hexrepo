import logging
import uuid
from collections.abc import Generator
from typing import Optional, Type

from monorepo_db import UOW, Repository
from monorepo_db.sql.stub import StubbedRepository
from pydantic import BaseModel

from app.domain.example import ExampleDTO

logger = logging.getLogger(__name__)


class StubbedExampleRepository(StubbedRepository):
    model_dto: Type[BaseModel] = ExampleDTO

    def _generate_fake_dto(self, obj_in: Optional[BaseModel] = None) -> BaseModel:
        return self.model_dto(
            id=uuid.uuid4(),
            name="test",
            url="https://test.com",
            location="test location",
        )


class StubbedUOW(UOW):
    @property
    def example(self) -> Repository:
        return StubbedExampleRepository()


def get_uow() -> Generator[UOW, None, None]:
    yield StubbedUOW(db_url="test")
