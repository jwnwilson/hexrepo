import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

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

    def __init__(self, client: MongoClient, table: str, required_filters: Optional[FilterParam] = None):
        self.client: MongoClient = client
        self.default_filters: Optional[FilterParam] = required_filters
        self.db: str = client.get_database().name
        self.table: str = table
        self._collection: Optional[Collection] = None

    @property
    def collection(self) -> Collection:
        if self._collection:
            return self._collection
        self._collection = self.client[self.db][self.table]
        return self._collection
    
    def _list_to_dto(self, items: List[Dict[str, Any]]) -> List[ModelDTO]:
        return [self.model_dto(**item.__dict__) for item in items]

    def create(self, obj_in: ModelDTO) -> ModelDTO:
        data_id: str = str(UUID())
        mongo_data = {**obj_in, **{"_id": data_id}}
        try:
            self.collection.insert_one(mongo_data)
            return self.read(record_id=data_id)
        except Exception as error:
            logger.info(f"Error creating record. Error: {error}")
            raise

    def read(self, record_id: UUID) -> ModelDTO:
        record: Optional[dict] = self.collection.find_one({"uuid": record_id})
        if not record:
            raise RecordNotFound(f"Record not found uuid: '{record_id}'")
        return self.model_dto(**record)
    
    def read_multi(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        page_size: int = 100,
        page_number: int = 1,
        order_by: str = "-created_at"
    ) -> List[dict]:
        collection_data = self.collection.find(filters)
        if page_size:
            data = data.limit(page_size)
        results: List[ModelDTO] = self._list_to_dto(collection_data)
        return PaginatedData(
            results=results, total=len(results), page_size=page_size, page_number=page_number
        )

    def update(self, record_id: UUID, obj_in: UpdateModelDTO, merge_objects: bool = False) -> ModelDTO:
        collection = self.client[self.db][table]
        record: Optional[dict] = collection.find_one({"id": record_id})
        if not record:
            raise RecordNotFound(f"Record not found uuid: '{record_id}'")

        record.update(obj_in)
        query = {"id": record_id}
        updated_record: Dict[str, Any] = collection.replace_one(
            query, record, upsert=True
        ).raw_result
        return self.model_dto(**updated_record)
    
    def delete(self, record_id: str):
        self.collection.delete_one({"uuid": record_id})

    def create_table(self):
        collection = self.client[self.db][self.table]
        return collection
    
    def delete_table(self):
        self.collection.drop()
