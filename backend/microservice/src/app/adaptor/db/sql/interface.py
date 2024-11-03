from abc import ABC
from typing import TypeVar
from uuid import UUID

from pytest import Session
from sqlalchemy import Select
from pydantic import BaseModel

from .models.base_model import Base

BaseSQLModel = Base
ModelDTOType = type[BaseModel]
ModelDTO = TypeVar("ModelDTO", bound=BaseModel)


class Query(ABC):
    def __init__(self, model: BaseSQLModel, model_dto: ModelDTOType, session: Session):
        self.model: BaseSQLModel = model
        self.model_dto: ModelDTOType = model_dto
        self.session: Session = session
        
    def query_multi(self) -> Select:
        # Query to return list of entities
        raise NotImplementedError
    
    def query_single(self, id: UUID) -> Select:
        # Query to retun a single entity by id
        raise NotImplementedError
    
    def query_total(self) -> int:
        # Query to return total number of entities
        raise NotImplementedError
    
    def parse_dto(self, dto: ModelDTO) -> BaseSQLModel:
        # logic to query db and add relationship data to db model
        raise NotImplementedError
    
    def update_relationships(self, db_obj: BaseSQLModel, dto: ModelDTO) -> BaseSQLModel:
        # logic to update relationships during update logic
        raise NotImplementedError
    