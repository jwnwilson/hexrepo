import logging
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.collection import Collection

from ...exception import RecordNotFound
from ...interface import (
    ModelDTO,
    ModelDTOType,
    PaginatedData,
    Repository,
    UpdateModelDTO,
)

logger = logging.getLogger(__name__)

FilterParam = Dict[str, Any]


class MongoRepository(Repository):
    model_dto: ModelDTOType = BaseModel

    def __init__(
        self,
        client: MongoClient,
        table: str,
        required_filters: Optional[FilterParam] = None,
    ):
        self.client: MongoClient = client
        self.default_filters: Optional[FilterParam] = required_filters
        self.db: str = client.get_database().name
        self.table: str = table
        self._collection: Optional[Collection] = None

    @property
    def collection(self) -> Collection:
        if self._collection is not None:
            return self._collection
        self._collection = self.client[self.db][self.table]
        return self._collection

    def _list_to_dto(self, items: List[Dict[str, Any]]) -> List[ModelDTO]:
        return [self.model_dto(**item) for item in items]

    def create(self, obj_in: ModelDTO) -> ModelDTO:
        data_id: str = str(uuid4())
        mongo_data = {**obj_in.model_dump(), **{"_id": data_id}}
        try:
            self.collection.insert_one(mongo_data)
            return self.read(id=data_id)
        except Exception as error:
            logger.info(f"Error creating record. Error: {error}")
            raise

    def read(self, id: UUID) -> ModelDTO:
        record: Optional[dict] = self.collection.find_one({"_id": str(id)})
        if not record:
            raise RecordNotFound(f"Record not found id: '{id}'")
        record["id"] = record.pop("_id")
        return self.model_dto(**record)

    def generate_filters(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if filters is None:
            return {}
        new_filters: Dict[str, Any] = {}
        for filter in filters:
            if "__in" in filter:
                new_filters[filter.replace("__in", "")] = {"$in": filters[filter]}
            else:
                new_filters[filter] = filters[filter]
        if "id" in new_filters:
            new_filters["_id"] = new_filters.pop("id")
        return new_filters

    def read_multi(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page_size: int = 100,
        page_number: int = 1,
        order_by: str = "-created_at",
    ) -> PaginatedData[ModelDTO]:
        collection_data = self.collection.find(self.generate_filters(filters))
        if page_size:
            collection_data = collection_data.limit(page_size)
        record_data = []
        for record in collection_data:
            record["id"] = record.pop("_id")
            record_data.append(record)
        results: List[ModelDTO] = self._list_to_dto(record_data)
        return PaginatedData(
            results=results,
            total=len(results),
            page_size=page_size,
            page_number=page_number,
        )

    def update(
        self, id: UUID, obj_in: UpdateModelDTO, merge_objects: bool = False
    ) -> ModelDTO:
        record: Optional[Dict[str, Any]] = self.collection.find_one({"_id": str(id)})
        if not record:
            raise RecordNotFound(f"Record not found id: '{id}'")

        record.update(obj_in.model_dump(exclude_unset=True))
        query = {"_id": str(id)}
        self.collection.replace_one(query, record, upsert=True)
        record["id"] = record.pop("_id")
        return self.model_dto(**record)

    def delete(self, id: UUID):
        self.read(id)
        self.collection.delete_one({"_id": str(id)})

    def create_table(self):
        collection = self.client[self.db][self.table]
        return collection

    def delete_table(self):
        self.collection.drop()
