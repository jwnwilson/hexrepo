import contextlib
import logging
import os
from typing import Dict, List, Optional

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from hex_lib.ports.db import DbAdapter, ListParams
from hex_lib.ports.user import UserData

from ..exceptions import DuplicateRecord, RecordNotFound

logger = logging.getLogger(__name__)


class MongoDbAdapter(DbAdapter):
    # Cache mongo clients for performance
    clients: Dict[str, MongoClient] = {}

    def __init__(self, config: dict, user: UserData, *args, **kwargs):
        self.config = config
        self.user = user
        self._configure_db()

    @contextlib.contextmanager
    def transaction_context_manager(self):
        with self.client.start_session() as session:
            with session.start_transaction():
                yield

    def _configure_db(self):
        uri = "mongodb://%s:%s@%s:27017/%s?retryWrites=true&w=majority" % (
            self.config.get("user", os.environ["MONGO_USER"]),
            self.config.get("password", os.environ["MONGO_PASSWORD"]),
            self.config.get("host", os.environ["MONGO_HOST"]),
            self.config.get("db_name", os.environ["MONGO_DB_NAME"]),
        )
        self.db = self.config.get("db_name", os.environ["MONGO_DB_NAME"])

        # Cache mongo clients to avoid performance issues
        db_client_key = uri + self.db
        if not self.clients.get(db_client_key):
            self.client: MongoClient = MongoClient(uri)
            self.clients[db_client_key] = self.client
        else:
            self.client: MongoClient = self.clients[db_client_key]

    def list(self, table: str, params: ListParams) -> List[dict]:
        collection = self.client[self.db][table]
        filters = {}
        if params.filters:
            filters.update(params.filters)

        data = collection.find(filters)
        if params.limit:
            data = data.limit(params.limit)
        list_data: List[dict] = [x for x in data]

        return list_data

    def read(self, table: str, record_id: str) -> dict:
        collection = self.client[self.db][table]
        record: Optional[dict] = collection.find_one({"uuid": record_id})
        if not record:
            raise RecordNotFound(f"Record not found uuid: '{record_id}'")
        return record

    def create(self, table: str, record_data: dict) -> dict:
        collection = self.client[self.db][table]
        mongo_data = {**record_data, **{"_id": record_data["uuid"]}}
        try:
            collection.insert_one(mongo_data)
            record: dict = self.read(table, record_id=record_data["uuid"])
            return record
        except DuplicateKeyError:
            uuid = record_data.get("uuid")
            error = f"Duplicate record uuid: '{uuid}'"
            logger.info(error)
            raise DuplicateRecord(error)

    def delete(self, table: str, record_id: str):
        collection = self.client[self.db][table]
        collection.delete_one({"uuid": record_id})

    def update(self, table: str, record_id: str, record_data: dict) -> dict:
        collection = self.client[self.db][table]
        record: Optional[dict] = collection.find_one({"uuid": record_id})
        if not record:
            raise RecordNotFound(f"Record not found uuid: '{record_id}'")

        query = {"uuid": record_id}
        record.update(record_data)
        updated_record: dict = collection.replace_one(
            query, record, upsert=True
        ).raw_result
        return updated_record

    def create_table(self, table: str, **kwargs):
        collection = self.client[self.db][table]
        return collection
