import logging
import uuid
from collections.abc import Generator

from monorepo_db import UOW, PaginatedData, Repository
from monorepo_db.interface import PaginatedData
from pydantic import BaseModel

from app.domain.example import ExampleDTO

logger = logging.getLogger(__name__)


# Move to db lib
class StubbedExampleRepository(Repository):
    def create(self, obj_in: BaseModel) -> BaseModel:
        logger.info("StubbedRepository create called")
        return ExampleDTO(
            id=uuid.uuid4(),
            name="test",
            url="https://test.com",
            location="test location",
        )

    def read(self, id) -> BaseModel:
        logger.info("StubbedRepository read called")
        return ExampleDTO(
            id=uuid.uuid4(),
            name="test",
            url="https://test.com",
            location="test location",
        )

    def read_multi(
        self, filters=None, page_size=100, page_number=1, order_by="-created_at"
    ) -> PaginatedData[BaseModel]:
        logger.info("StubbedRepository read multi called")
        return PaginatedData(
            results=[
                ExampleDTO(
                    id=uuid.uuid4(),
                    name="test",
                    url="https://test.com",
                    location="test location",
                )
            ],
            total=1,
        )

    def update(self, id, obj_in: BaseModel, merge_objects: bool = False) -> BaseModel:
        logger.info("StubbedRepository update called")
        return ExampleDTO(
            id=uuid.uuid4(),
            name="test",
            url="https://test.com",
            location="test location",
        )

    def delete(self, id) -> None:
        logger.info("StubbedRepository delete called")


class StubbedUOW(UOW):
    @property
    def example(self) -> Repository:
        return StubbedExampleRepository()


def get_uow() -> Generator[UOW, None, None]:
    yield StubbedUOW(db_url="test")
