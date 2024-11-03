from abc import ABC
from typing import TypeVar
from uuid import UUID

from sqlalchemy import Select
from pydantic import BaseModel

from .models.base_model import Base

BaseSQLModel = Base
ModelDTOType = type[BaseModel]
ModelDTO = TypeVar("ModelDTO", bound=BaseModel)


class Query(ABC):
    def query_multi(self) -> Select:
        # Query to return list of entities
        raise NotImplementedError
    
    def query_single(self, id: UUID) -> Select:
        # Query to retun a single entity by id
        raise NotImplementedError
    
    def query_total(self) -> int:
        # Query to return total number of entities
        raise NotImplementedError
    
    def parse_db_model(self, dto: ModelDTO) -> BaseSQLModel:
        # logic to query db and add relationship data to db model
       raise NotImplementedError