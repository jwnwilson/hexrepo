import contextlib
from abc import ABC
from typing import Any, Dict, Generator, Generic, Optional, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel

ModelDTO = TypeVar("ModelDTO", bound=BaseModel)
UpdateModelDTO = TypeVar("UpdateModelDTO", bound=BaseModel)
ModelDTOType = Type[BaseModel]


class PaginatedData(BaseModel, Generic[ModelDTO]):
    results: list[ModelDTO]
    total: int = 0
    page_size: int = 100
    page_number: int = 1


class Repository(ABC):
    def create(self, obj_in: ModelDTO) -> Any:
        raise NotImplementedError

    def read(self, id: UUID) -> Any:
        raise NotImplementedError

    def update(
        self, id: UUID, obj_in: UpdateModelDTO, merge_objects: bool = False
    ) -> Any:
        raise NotImplementedError

    def delete(self, id: UUID) -> None:
        raise NotImplementedError

    def read_multi(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page_size: int = 100,
        page_number: int = 1,
        order_by: str = "-created_at",
    ) -> PaginatedData[BaseModel]:
        raise NotImplementedError

    def search(
        self, search_param: Dict[str, str], page_size: int = 100, page_number: int = 1
    ) -> PaginatedData[BaseModel]:
        raise NotImplementedError


class UOW(ABC):
    def __init__(self, db_url: str, required_filters: Optional[Dict[str, str]] = None):
        self._db_url: str = db_url
        self._required_filters: Optional[Dict[str, str]] = required_filters

    def set_required_filters(self, required_filters: Dict[str, str]) -> None:
        self._required_filters = required_filters

    @contextlib.contextmanager
    def transaction(self) -> Generator[Any, None, None]:
        raise NotImplementedError

    # Used for testing
    def create_all(self) -> None:
        raise NotImplementedError

    def drop_all(self) -> None:
        raise NotImplementedError


class ExampleUOW(UOW):
    @property
    def example(self) -> Repository:
        raise NotImplementedError
