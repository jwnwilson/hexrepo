from abc import ABC
from typing import Any, Dict, Optional, TypeVar, Generic

from pydantic import BaseModel
from sqlalchemy.orm import Session

ModelDTO = TypeVar("ModelDTO", bound=BaseModel)


class PaginatedData(BaseModel, Generic[ModelDTO]):
    results: list[ModelDTO]
    total: int = 0
    page_size: int = 100
    page_number: int = 1


class Repository(ABC):
    def create(self, obj_in: Any) -> Any:
        raise NotImplementedError

    def read(self, id: Any) -> ModelDTO | None:  # type: ignore
        raise NotImplementedError

    def update(self, id: Any) -> ModelDTO | None:  # type: ignore
        raise NotImplementedError

    def delete(self, id: Any) -> ModelDTO | None:  # type: ignore
        raise NotImplementedError

    def read_multi(
        self,
        filters: Any = None,
        page_size: int = 100,
        page_number: int = 1,
        order_by: str = "-created_at",
        query_type: str = "base",
        fields: str = "base",
    ) -> PaginatedData:
        raise NotImplementedError

    def get_offset(self, page_size, page_number):
        return (page_number - 1) * page_size

    def paginate(self, query, page_number, page_size):
        raise NotImplementedError

    def search(self, search_param: dict, page_size=100, page_number=1) -> PaginatedData:
        raise NotImplementedError


class UOW(ABC):
    def __init__(self, session: Session, required_filters: Optional[Dict] = None):
        self._session: Session = session
        self._required_filters: Optional[Dict] = required_filters

    def set_required_filters(self, required_filters: Dict):
        self._required_filters = required_filters

    @property
    def example(self) -> Repository:
        raise NotImplementedError

    # Used for testing
    def create_all(self):
        raise NotImplementedError

    def drop_all(self):
        raise NotImplementedError
