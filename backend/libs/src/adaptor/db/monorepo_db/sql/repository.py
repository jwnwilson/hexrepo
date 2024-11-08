import logging
from typing import Any, Dict, Optional

from pydantic import UUID4, BaseModel
from sqlalchemy import UUID, Row, Select, asc, desc, func, select
from sqlalchemy.exc import IntegrityError as SQLIntegrityError
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.orm import Session
from sqlalchemy.orm.collections import InstrumentedList

from ..interface import PaginatedData, Repository
from ..exception import IntegrityError, RecordNotFound
from .session import DatabaseSessionManager
from .interface import Query, BaseSQLModel, ModelDTOType, ModelDTO

logger = logging.getLogger()


class DefaultQuery(Query):
    def __init__(self, model: BaseSQLModel, model_dto: ModelDTOType, session: Session):
        self.model: BaseSQLModel = model
        self.model_dto: ModelDTOType = model_dto
        self.session: Session = session

    def query_multi(self) -> Select:
        # Query to return list of entities
        return select(self.model)
    
    def query_single(self, id: UUID) -> Select:
        # Query to retun a single entity by id
        return self.query_multi().where(self.model.id == id)
    
    def query_total(self) -> int:
        # Query to return total number of entities
        return select(func.count()).select_from(self.model)
    
    def parse_dto(self, dto: ModelDTO) -> BaseSQLModel:
        # logic to convert pydantic DTO to db model and add FK relationship data if needed
        db_obj = self.model(**dto.model_dump())
        return db_obj
    
    def update_relationships(self, db_obj: BaseSQLModel, dto: ModelDTO) -> BaseSQLModel:
        # logic to update FK relationships during update logic
        return db_obj


class SQLRepository(Repository):
    # Refactor me to remove inhertance and fix bugs
    model: Any = BaseSQLModel
    model_dto: ModelDTOType = BaseModel

    def __init__(self, session_manager: DatabaseSessionManager, required_filters: Optional[Dict] = None, query: Optional[Query] = None):
        self._session_manager: DatabaseSessionManager = session_manager
        self._required_filters = required_filters
        self.query: Query = query or DefaultQuery(self.model, self.model_dto, self.session)

    @property
    def session(self) -> Session:
        return self._session_manager.session

    def _query_single(self, id: UUID) -> Row:
        try:
            query: Select = self.query.query_single(id)
            results = self.session.execute(query).one_or_none()
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

    def _get_total(self, filters: Optional[Dict] = None):
        query = self.query.query_total()
        if filters:
            query = self._filter(query, filters)
        return self.session.scalar(query)

    def _query_to_dto(self, query):
        query_result = self.session.execute(query)
        return [self._model_to_dto(row) for row in query_result.scalars()]

    def _model_to_dto(self, row):
        return self.model_dto(**row.__dict__)
    
    def _filter(
        self,
        query: Select,
        filters: Dict[str, Any],
    ) -> Select:
        for key in filters:
            if key.endswith("__in"):
                model_attr = getattr(self.model, key.split("__")[0])
                query = query.filter(model_attr.in_(filters[key]))
            else:
                query = query.where(getattr(self.model, key) == filters[key])

        return query

    def _order(
        self,
        query: Select,
        order_by: Optional[str] = None,
    ) -> Select:
        if order_by is not None:
            direction = desc if order_by.startswith("-") else asc
            query = query.order_by(direction(order_by.lstrip("-")))
            return query
        else:
            return query
    
    def _update_db_model_attrs(self, db_obj: BaseSQLModel, obj_in: ModelDTO, merge_objects: bool):
        """Update db_obj with new data from obj_in, if merge_objects is True, merge the dictionary
        attrs and replace the existing data with the new data.

        Args:
            db_obj (BaseSQLModel): existing db model to update
            obj_in (ModelDTO): new data
            merge_objects (bool): if true merge data, if false replace data
        """
        # Merge new data with existing data
        for key, value in obj_in.model_dump(exclude_unset=True).items():
            # Avoid updating relationships as they are handled in parse_dto
            if type(getattr(db_obj, key)) is InstrumentedList:
                continue
            current_value = getattr(db_obj, key, None)
            is_object_attr = isinstance(current_value, dict) and isinstance(
                value, dict
            )
            # Merge the existing dict with new data - favours new data
            if is_object_attr and merge_objects:
                merged_value = {**current_value, **value}
                setattr(db_obj, key, merged_value)
            else:
                setattr(db_obj, key, getattr(obj_in, key))

    def create(self, obj_in: ModelDTO) -> ModelDTO:
        db_obj: BaseSQLModel = self.query.parse_dto(obj_in)
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
        query_result = self._query_single(id)
        try:
            return self._model_to_dto(query_result)
        except IndexError:
            raise RecordNotFound(
                f"Model: {self.model.__name__}, Record: {id}, not found"
            )

    def read_multi(
        self,
        filters: Optional[Dict] = None,
        page_size: int = 100,
        page_number: int = 1,
        order_by: str = "-created_at",
    ) -> PaginatedData:
        query = self.query.query_multi()
        if filters:
            query = self._filter(query, filters)
        query = self._order(query, order_by)
        total = self._get_total(filters)
        query = self.paginate(query, page_number, page_size)
        results = self._query_to_dto(query)
        return PaginatedData(
            results=results, total=total, page_size=page_size, page_number=page_number
        )

    def update(self, id: UUID4, obj_in: ModelDTO, merge_objects=False) -> ModelDTO:
        existing_obj: BaseSQLModel = self._query_single(id)
        self._update_db_model_attrs(existing_obj, obj_in, merge_objects)
        self.query.update_relationships(existing_obj, obj_in)
                
        try:
            self.session.flush()
        except IntegrityError as err:
            logger.warning(
                f"DB integrity Error updating: {self.__class__.__name__}: {id}, er: {err}"
            )
            self.session.rollback()
            raise IntegrityError(err)
        self.session.refresh(existing_obj)
        return self._model_to_dto(existing_obj)

    def delete(self, id: UUID4) -> bool:
        result = self._query_single(id)
        self.session.delete(result)
        self.session.flush()

    def _get_offset(self, page_size: int, page_number: int):
        return (page_number - 1) * page_size

    def paginate(self, query: Select, page_number: int, page_size: int) -> Select:
        if page_size > 0 and page_number >= 1:
            offset: int = self._get_offset(page_size, page_number)
            query = query.offset(offset).limit(page_size)

        return query
