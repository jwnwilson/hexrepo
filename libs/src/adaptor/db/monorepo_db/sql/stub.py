import logging
import uuid
from collections.abc import Generator
from typing import Any, Dict, Optional

from pydantic import BaseModel

from monorepo_db import UOW, PaginatedData, Repository
from monorepo_db.interface import PaginatedData

logger = logging.getLogger(__name__)


class StubbedRepository(Repository):
    """Fake repository for testing"""

    model_dto: BaseModel

    def _generate_fake_dto(self, obj_in: Optional[BaseModel] = None) -> BaseModel:
        raise NotImplementedError
        # Example below

        # return self.model_dto(
        #     id=uuid.uuid4(),
        #     name="test",
        #     url="https://test.com",
        #     location="test location",
        # )

    def create(self, obj_in: BaseModel) -> BaseModel:
        logger.info("StubbedRepository create called")
        return self._generate_fake_dto(obj_in)

    def read(self, id: uuid.UUID) -> BaseModel:
        logger.info("StubbedRepository read called")
        return self._generate_fake_dto()

    def read_multi(
        self, filters: Optional[Dict[str, Any]]=None, page_size: int=100, page_number: int=1, order_by: str="-created_at"
    ) -> PaginatedData[BaseModel]:
        logger.info("StubbedRepository read multi called")
        return PaginatedData(
            results=[self._generate_fake_dto()],
            total=1,
        )

    def update(self, id: uuid.UUID, obj_in: BaseModel, merge_objects: bool = False) -> BaseModel:
        logger.info("StubbedRepository update called")
        return self._generate_fake_dto()

    def delete(self, id: uuid.UUID) -> None:
        logger.info("StubbedRepository delete called")
