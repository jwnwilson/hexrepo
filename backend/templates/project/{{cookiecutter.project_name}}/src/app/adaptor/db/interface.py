from abc import ABC
import contextlib
from typing import Any, Dict, Generator, Optional, TypeVar, Generic
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session

ModelDTO = TypeVar("ModelDTO", bound=BaseModel)


class PaginatedData(BaseModel, Generic[ModelDTO]):
    results: list[ModelDTO]
    total: int = 0
    page_size: int = 100
    page_number: int = 1


class Repository(ABC):
    def create(self, obj_in: ModelDTO) -> Any:
        raise NotImplementedError

    def read(self, id: UUID) -> ModelDTO | None:  # type: ignore
        raise NotImplementedError

    def update(self, id: UUID) -> ModelDTO | None:  # type: ignore
        raise NotImplementedError

    def delete(self, id: UUID) -> ModelDTO | None:  # type: ignore
        raise NotImplementedError

    def read_multi(
        self,
        filters: Optional[Dict] = None,
        page_size: int = 100,
        page_number: int = 1,
        order_by: str = "-created_at",
        query_type: str = "base",
        fields: str = "base",
    ) -> PaginatedData:
        raise NotImplementedError

    def get_offset(self, page_size: int, page_number: int):
        return (page_number - 1) * page_size

    def paginate(self, query, page_number, page_size):
        raise NotImplementedError

    def search(self, search_param: dict, page_size=100, page_number=1) -> PaginatedData:
        raise NotImplementedError


class UOW(ABC):
    def __init__(self, db_url: str, required_filters: Optional[Dict] = None):
        self._db_url: str = db_url
        self._required_filters: Optional[Dict] = required_filters

    def set_required_filters(self, required_filters: Dict):
        self._required_filters = required_filters

    @contextlib.contextmanager
    def transaction(self) -> Generator[Session, None, None]:
        raise NotImplementedError

    @property
    def example(self) -> Repository:
        raise NotImplementedError

    # Used for testing
    def create_all(self):
        raise NotImplementedError

    def drop_all(self):
        raise NotImplementedError
