import logging
from typing import Any, Dict, List, Optional, Type, Union
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import Row, Select, asc, desc, func, select
from sqlalchemy.exc import IntegrityError as SQLIntegrityError
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.orm import Session
from sqlalchemy.orm.collections import InstrumentedList

from ..exception import IntegrityError, RecordNotFound
from ..interface import (
    ModelDTO,
    ModelDTOType,
    PaginatedData,
    Repository,
    UpdateModelDTO,
)
from .interface import BaseSQLModel, Query, SQLModelType

logger = logging.getLogger()


class DefaultQuery(Query):
    def __init__(
        self,
        model: SQLModelType,
        model_dto: ModelDTOType,
        session: Session,
        default_filters: Optional[Dict[str, Any]] = None,
    ):
        self.model: SQLModelType = model
        self.model_dto: ModelDTOType = model_dto
        self.session: Session = session
        self.default_filters: Optional[Dict[str, Any]] = default_filters

    def _apply_default_filters(self, query: Select[Any]) -> Select[Any]:
        if self.default_filters:
            for key, value in self.default_filters.items():
                query = query.where(getattr(self.model, key) == value)
        return query

    def query_select(self) -> Select[Any]:
        # Base select / join query for this model
        return select(self.model)

    def query_multi(self) -> Select[Any]:
        # Query to return list of entities
        default_query = self.query_select()
        default_query = self._apply_default_filters(default_query)
        # Load relationships
        return default_query

    def query_single(self, id: UUID) -> Select[Any]:
        # Query to retun a single entity by id
        return self.query_multi().where(self.model.id == id)

    def query_total(self) -> Select[Any]:
        # Query to return total number of entities
        query_total: Select[Any] = select(func.count()).select_from(self.model)
        return self._apply_default_filters(query_total)

    def parse_dto(self, dto: ModelDTO) -> Any:
        # logic to convert pydantic DTO to db model and add FK relationship data if needed
        db_obj: BaseSQLModel = self.model(**dto.model_dump())  # type: ignore
        return db_obj

    def update_relationships(
        self, db_obj: Union[Row[Any], BaseSQLModel], dto: ModelDTO, create: bool = False
    ) -> Row[Any] | BaseSQLModel:
        # logic to update FK relationships during update logic
        # Find intrumentedLists
        relationships: List[str] = [
            attr
            for attr in dir(db_obj)
            if getattr(db_obj, attr).__class__.__name__ == "InstrumentedList"
        ]
        # For each instrumentedList check for diff against dto
        for relationship in relationships:
            # If diff, update relationship
            dto_ids: List[str] = [str(r["id"]) for r in getattr(dto, relationship)]
            # If creating, no need to check for diff
            if create:
                db_ids: List[str] = []
            else:
                db_ids: List[str] = [str(r.id) for r in getattr(db_obj, relationship)]
            id_diff: bool = set(db_ids) != set(dto_ids)
            if id_diff:
                # Get relationship table
                relationship_table = getattr(db_obj.__class__, relationship)
                # Get relationship model
                relationship_model: BaseSQLModel = (
                    relationship_table.property.mapper.class_
                )
                # Get new relationship objects
                new_relationships = (
                    self.session.query(relationship_model)
                    .filter(relationship_model.id.in_(dto_ids))
                    .all()
                )
                # Update relationship
                setattr(db_obj, relationship, new_relationships)
        return db_obj


class SQLRepository(Repository):
    model: Any = BaseSQLModel
    model_dto: ModelDTOType = BaseModel
    query_logic: Type[Query] = DefaultQuery

    def __init__(
        self,
        session: Session,
        required_filters: Optional[Dict[str, Any]] = None,
    ):
        self._session: Session = session
        self._required_filters = required_filters
        self.query: Query = self.query_logic(
            self.model, self.model_dto, self.session, default_filters=required_filters
        )

    @property
    def session(self) -> Session:
        return self._session

    def _query_single(self, id: UUID) -> Any:
        try:
            query: Select[Any] = self.query.query_single(id)
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

    def _get_total(self, filters: Optional[Dict[str, Any]] = None) -> int:
        query: Select[Any] = self.query.query_total()
        if filters:
            query = self._filter(query, filters)
        return int(self.session.scalar(query))

    def _query_to_dto(self, query: Select[Any]) -> List[BaseModel]:
        query_result = self.session.execute(query)
        return [self._model_to_dto(row) for row in query_result.scalars()]

    def _model_to_dto(self, row: Union[BaseSQLModel, Row[Any]]) -> BaseModel:
        return self.model_dto(**row.__dict__)

    def _filter(
        self,
        query: Select[Any],
        filters: Dict[str, Any],
    ) -> Select[Any]:
        for key in filters:
            if key.endswith("__in"):
                model_attr = getattr(self.model, key.split("__")[0])
                query = query.filter(model_attr.in_(filters[key]))
            else:
                query = query.where(getattr(self.model, key) == filters[key])

        return query

    def _order(
        self,
        query: Select[Any],
        order_by: Optional[str] = None,
    ) -> Select[Any]:
        if order_by is not None:
            direction = desc if order_by.startswith("-") else asc
            query = query.order_by(direction(order_by.lstrip("-")))
            return query
        else:
            return query

    def _update_db_model_attrs(
        self, db_obj: Row[Any], obj_in: ModelDTO, merge_objects: bool
    ) -> None:
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
            is_object_attr = isinstance(current_value, dict) and isinstance(value, dict)
            # Merge the existing dict with new data - favours new data
            if is_object_attr and merge_objects:
                merged_value: Dict[str, Any] = {**current_value, **value}  # type: ignore
                setattr(db_obj, key, merged_value)
            else:
                setattr(db_obj, key, getattr(obj_in, key))

    def create(self, obj_in: ModelDTO) -> BaseModel:
        db_obj: Any = self.query.parse_dto(obj_in)
        self.query.update_relationships(db_obj, obj_in, create=True)
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

    def read(self, id: UUID) -> BaseModel:
        query_result = self._query_single(id)
        try:
            return self._model_to_dto(query_result)
        except IndexError:
            raise RecordNotFound(
                f"Model: {self.model.__name__}, Record: {id}, not found"
            )

    def read_multi(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page_size: int = 100,
        page_number: int = 1,
        order_by: str = "-created_at",
    ) -> PaginatedData[ModelDTO]:
        query = self.query.query_multi()
        if filters:
            query = self._filter(query, filters)
        query = self._order(query, order_by)
        total = self._get_total(filters)
        query = self.paginate(query, page_number, page_size)
        results: List[BaseModel] = self._query_to_dto(query)
        return PaginatedData(
            results=results, total=total, page_size=page_size, page_number=page_number
        )

    def update(
        self, id: UUID, obj_in: UpdateModelDTO, merge_objects: bool = False
    ) -> BaseModel:
        existing_obj: Row[Any] = self._query_single(id)
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

    def delete(self, id: UUID) -> None:
        result = self._query_single(id)
        self.session.delete(result)
        self.session.flush()

    def _get_offset(self, page_size: int, page_number: int) -> int:
        return (page_number - 1) * page_size

    def paginate(
        self, query: Select[Any], page_number: int, page_size: int
    ) -> Select[Any]:
        if page_size > 0 and page_number >= 1:
            offset: int = self._get_offset(page_size, page_number)
            query = query.offset(offset).limit(page_size)

        return query
