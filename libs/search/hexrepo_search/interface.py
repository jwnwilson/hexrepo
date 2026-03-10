from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator


class ElasticsearchInterface(ABC):
    """Abstract async interface for Elasticsearch operations."""

    def __init__(self, index: str) -> None:
        self.index = index

    # ---------- Connection ----------

    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def ping(self) -> bool: ...

    # ---------- Index Management ----------

    @abstractmethod
    async def create_index(
        self, mappings: dict | None = None, settings: dict | None = None
    ) -> dict: ...

    @abstractmethod
    async def delete_index(self) -> dict: ...

    @abstractmethod
    async def index_exists(self) -> bool: ...

    @abstractmethod
    async def list_indices(self, pattern: str = "*") -> list[str]: ...

    # ---------- Document CRUD ----------

    @abstractmethod
    async def index_document(
        self, document: dict, doc_id: str | None = None
    ) -> dict: ...

    @abstractmethod
    async def get_document(self, doc_id: str) -> dict: ...

    @abstractmethod
    async def update_document(self, doc_id: str, updates: dict) -> dict: ...

    @abstractmethod
    async def delete_document(self, doc_id: str) -> dict: ...

    # ---------- Bulk Operations ----------

    @abstractmethod
    async def bulk_index(self, documents: list[dict]) -> dict: ...

    @abstractmethod
    async def bulk_delete(self, doc_ids: list[str]) -> dict: ...

    # ---------- Search ----------

    @abstractmethod
    async def search(
        self,
        query: dict,
        size: int = 10,
        from_: int = 0,
        sort: list[dict] | None = None,
        source: list[str] | bool | None = None,
    ) -> dict: ...

    @abstractmethod
    async def count(self, query: dict | None = None) -> int: ...

    @abstractmethod
    async def scroll(
        self, query: dict, scroll_ttl: str = "2m", size: int = 1000
    ) -> AsyncGenerator[dict, None]: ...

    # ---------- Aggregations ----------

    @abstractmethod
    async def aggregate(
        self, aggregations: dict, query: dict | None = None
    ) -> dict: ...

    # ---------- Cluster / Health ----------

    @abstractmethod
    async def cluster_health(self) -> dict: ...

    @abstractmethod
    async def get_index_stats(self) -> dict: ...

    # ---------- Async context manager ----------

    async def __aenter__(self) -> "ElasticsearchInterface":
        await self.connect()
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.disconnect()
