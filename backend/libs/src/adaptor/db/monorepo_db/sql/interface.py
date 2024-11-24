from abc import ABC
from typing import Any
from uuid import UUID

from sqlalchemy import Row, Select
from sqlalchemy.orm import Session

from ..interface import ModelDTO, ModelDTOType, UpdateModelDTO
from .models.base_model import Base

BaseSQLModel = Base


class Query(ABC):
    def __init__(self, model: BaseSQLModel, model_dto: ModelDTOType, session: Session):
        self.model: BaseSQLModel = model
        self.model_dto: ModelDTOType = model_dto
        self.session: Session = session

    def query_multi(self) -> Select[Any]:
        # Query to return list of entities
        raise NotImplementedError

    def query_single(self, id: UUID) -> Select[Any]:
        # Query to retun a single entity by id
        raise NotImplementedError

    def query_total(self) -> Select[Any]:
        # Query to return total number of entities
        raise NotImplementedError

    def parse_dto(self, dto: ModelDTO) -> BaseSQLModel:
        # logic to query db and add relationship data to db model
        raise NotImplementedError

    def update_relationships(self, db_obj: Row[Any], dto: ModelDTO) -> BaseSQLModel:
        # logic to update relationships during update logic
        raise NotImplementedError
