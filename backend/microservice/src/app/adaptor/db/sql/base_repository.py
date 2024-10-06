import logging
from typing import Any, Dict, Literal, Optional, TypeVar

from app.ports.db.repository import PaginatedData, Repository
from pydantic import UUID4, BaseModel
from sqlalchemy import asc, desc, func, select
from sqlalchemy.exc import IntegrityError as SQLIntegrityError
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.orm import Session
from sqlalchemy.orm.collections import InstrumentedList

from ..exception import IntegrityError, RecordNotFound, SessionNotInitialised
from .models.base import Base

BaseSQLModel = Base
ModelDTOType = type[BaseModel]
ModelDTO = TypeVar("ModelDTO", bound=BaseModel)
logger = logging.getLogger()


class SQLRepository(Repository):
    model: Any = BaseSQLModel
    model_dto: ModelDTOType = BaseModel

    def __init__(self, session: Session, required_filters: Optional[Dict] = None):
        self._session = session
        self._required_filters = required_filters

    @property
    def session(self) -> Session:
        if not self._session:
            raise SessionNotInitialised
        return self._session

    def _create_engine(self):
        logger.debug("Setting up a new database engine.")
        return self._create_engine(self.database_uri, **self.engine_args)

    def _get_query(self):
        return select(self.model)

    def _get_query_by_id(self, id):
        return self._get_query().where(self.model.id == id)

    def _query_one_or_none_by_id(self, id) -> Any:
        try:
            results = self.session.execute(self._get_query_by_id(id)).one_or_none()
        # Should this be logged here, or allowed to bomb out the request with a 500?
        except MultipleResultsFound:
            logger.warning(
                f"Model: {self.model.__name__}, ID: {id}, multiple records found"
            )
        if not results:
            raise RecordNotFound(
                f"Model: {self.model.__name__}, Record: {id}, not found"
            )
        return results[0]

    def _query_one_or_none_by_multiple_fields(self, **kwargs) -> Any:
        try:
            query = self._get_query()
            for k, v in kwargs.items():
                query = query.where(getattr(self.model, k) == v)
            results = self.session.execute(query).one_or_none()
        except MultipleResultsFound:
            logger.warning(
                f"Model: {self.model.__name__}, multiple records found matching {kwargs}"
            )
        if not results:
            raise RecordNotFound(
                f"Model: {self.model.__name__}, no record found matching {kwargs}"
            )
        return results[0]

    def _get_total(self, query, filters: Optional[Dict] = None):
        query = select(func.count()).select_from(self.model)
        if filters:
            query = self._filter(query, filters)
        return self.session.scalar(query)

    def _query_to_dto(self, query):
        query_result = self.session.execute(query)
        return [self._model_to_dto(row) for row in query_result.scalars()]

    def _model_to_dto(self, row):
        return self.model_dto(**row.__dict__)

    def _handle_relationships(self, obj_in: ModelDTO, db_obj: BaseSQLModel):
        # For many to many relationships to work we need to replace
        # UUIDs with actual objects from the db
        # To be implemented in sub classes if needed
        pass

    def create(self, obj_in: ModelDTO) -> ModelDTO:
        db_obj = self.model(**obj_in.model_dump())
        self._handle_relationships(obj_in, db_obj)
        try:
            self.session.add(db_obj)
            self.session.flush()
        except SQLIntegrityError as err:
            logger.warning(
                f"DB integrity Error creating: {self.__class__.__name__}, er: {err}"
            )
            self.session.rollback()
            raise IntegrityError(err.orig)
        self.session.refresh(db_obj)
        return self._model_to_dto(db_obj)

    def read(self, id: UUID4) -> ModelDTO:
        query_result = self._query_one_or_none_by_id(id)
        try:
            return self._model_to_dto(query_result)
        except IndexError:
            raise RecordNotFound(
                f"Model: {self.model.__name__}, Record: {id}, not found"
            )

    def _filter(
        self,
        query,
        filters: Dict[str, Any],
    ):
        for key in filters:
            if key.endswith("__in"):
                model_attr = getattr(self.model, key.split("__")[0])
                query = query.filter(model_attr.in_(filters[key]))
            else:
                query = query.where(getattr(self.model, key) == filters[key])

        return query

    def _order(
        self,
        query,
        order_by: Optional[str] = None,
    ):
        if order_by is not None:
            direction = desc if order_by.startswith("-") else asc
            query = query.order_by(direction(order_by.lstrip("-")))
            return query
        else:
            return query

    def read_multi(
        self,
        filters: Optional[Dict] = None,
        page_size: int = 100,
        page_number: int = 1,
        order_by: str = "-created_at",
    ) -> PaginatedData:
        query = self._get_query()
        if filters:
            query = self._filter(query, filters)
        query = self._order(query, order_by)
        total = self._get_total(query, filters)
        query = self.paginate(query, page_number, page_size)
        results = self._query_to_dto(query)
        return PaginatedData(
            results=results, total=total, page_size=page_size, page_number=page_number
        )

    def update(self, id: UUID4, obj_in: ModelDTO, merge_objects=False) -> ModelDTO:
        result = self._query_one_or_none_by_id(id)
        # to ensure updated values that were not in payload remain the same
        for key, value in obj_in.model_dump(exclude_unset=True).items():
            current_value = getattr(result, key, None)
            setting_object_values = isinstance(current_value, dict) and isinstance(
                value, dict
            )
            # Merge the existing dictionary field with new data - favours new data
            if merge_objects and setting_object_values:
                merged_value = {**current_value, **value}
                setattr(result, key, merged_value)
            # Avoid updating relationships as they are handled separately
            elif type(getattr(result, key)) is not InstrumentedList:
                setattr(result, key, getattr(obj_in, key))
        self._handle_relationships(obj_in, result)
        try:
            self.session.flush()
        except IntegrityError as err:
            logger.warning(
                f"DB integrity Error updating: {self.__class__.__name__}: {id}, er: {err}"
            )
            self.session.rollback()
            raise IntegrityError(err)
        self.session.refresh(result)
        return self._model_to_dto(result)

    def delete(self, id: UUID4) -> bool:
        result = self._query_one_or_none_by_id(id)
        self.session.delete(result)
        self.session.flush()

    def _get_offset(self, page_size: int, page_number: int):
        return (page_number - 1) * page_size

    def paginate(self, query, page_number: int, page_size: int):
        if page_size > 0 and page_number >= 1:
            offset = self._get_offset(page_size, page_number)
            query = query.offset(offset).limit(page_size)

        return query
