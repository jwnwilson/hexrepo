from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, AsyncGenerator

from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch.helpers import async_bulk

from app.config import config

from .interface import ElasticsearchInterface

logger = logging.getLogger(__name__)


class ElasticsearchClient(ElasticsearchInterface):
    """Async Elasticsearch 8.x client. Install: pip install 'elasticsearch>=8,<9'"""

    def __init__(
        self,
        index: str,
        hosts: list[str] | None = None,
        username: str | None = None,
        password: str | None = None,
        api_key: str | None = None,
        ca_certs: str | None = None,
        verify_certs: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(index)
        self._hosts = hosts or [config.ELASTICSEARCH_URL]
        self._username = username
        self._password = password
        self._api_key = api_key
        self._ca_certs = ca_certs
        self._verify_certs = verify_certs
        self._extra_kwargs = kwargs
        self._client: AsyncElasticsearch | None = None

    # ---------- Connection ----------

    async def connect(self) -> None:
        auth_kwargs: dict[str, Any] = {}
        if self._api_key:
            auth_kwargs["api_key"] = self._api_key
        elif self._username and self._password:
            auth_kwargs["basic_auth"] = (self._username, self._password)
        if self._ca_certs:
            auth_kwargs["ca_certs"] = self._ca_certs

        self._client = AsyncElasticsearch(
            self._hosts,
            verify_certs=self._verify_certs,
            **auth_kwargs,
            **self._extra_kwargs,
        )
        logger.info("Connected to Elasticsearch at %s", self._hosts)

    async def disconnect(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Disconnected from Elasticsearch")

    async def ping(self) -> bool:
        return bool(await self._es.ping())

    # ---------- Index Management ----------

    async def create_index(
        self, mappings: dict | None = None, settings: dict | None = None
    ) -> dict:
        kwargs: dict[str, Any] = {}
        if mappings:
            kwargs["mappings"] = mappings
        if settings:
            kwargs["settings"] = settings
        response = await self._es.indices.create(index=self.index, **kwargs)
        logger.info("Created index '%s'", self.index)
        return response.body

    async def delete_index(self) -> dict:
        response = await self._es.indices.delete(index=self.index)
        logger.info("Deleted index '%s'", self.index)
        return response.body

    async def index_exists(self) -> bool:
        return bool(await self._es.indices.exists(index=self.index))

    async def list_indices(self, pattern: str = "*") -> list[str]:
        response = await self._es.cat.indices(index=pattern, h="index", format="json")
        return [entry["index"] for entry in response.body]

    # ---------- Document CRUD ----------

    async def index_document(self, document: dict, doc_id: str | None = None) -> dict:
        response = await self._es.index(index=self.index, id=doc_id, document=document)
        logger.debug("Indexed document id=%s in '%s'", response["_id"], self.index)
        return response.body

    async def get_document(self, doc_id: str) -> dict:
        try:
            return (await self._es.get(index=self.index, id=doc_id)).body
        except NotFoundError:
            raise KeyError(f"Document '{doc_id}' not found in index '{self.index}'")

    async def update_document(self, doc_id: str, updates: dict) -> dict:
        response = await self._es.update(index=self.index, id=doc_id, doc=updates)
        logger.debug("Updated document id=%s in '%s'", doc_id, self.index)
        return response.body

    async def delete_document(self, doc_id: str) -> dict:
        response = await self._es.delete(index=self.index, id=doc_id)
        logger.debug("Deleted document id=%s from '%s'", doc_id, self.index)
        return response.body

    # ---------- Bulk Operations ----------

    async def bulk_index(self, documents: list[dict]) -> dict:
        actions = [
            {"_index": self.index, "_id": doc.pop("_id", None), "_source": doc}
            for doc in documents
        ]
        success, errors = await async_bulk(self._es, actions, raise_on_error=False)
        logger.info(
            "Bulk indexed %d documents into '%s' (%d errors)",
            success,
            self.index,
            len(errors),
        )
        return {"indexed": success, "errors": errors}

    async def bulk_delete(self, doc_ids: list[str]) -> dict:
        actions = [
            {"_op_type": "delete", "_index": self.index, "_id": doc_id}
            for doc_id in doc_ids
        ]
        success, errors = await async_bulk(self._es, actions, raise_on_error=False)
        logger.info(
            "Bulk deleted %d documents from '%s' (%d errors)",
            success,
            self.index,
            len(errors),
        )
        return {"deleted": success, "errors": errors}

    async def bulk_index_jsonl(self, path: str | Path, batch_size: int = 5000) -> dict:
        from app.interactor.event.temporal.activities import iter_jsonl

        total_indexed, total_errors = 0, []

        async for batch in iter_jsonl(path, batch_size):
            actions = [
                {"_index": self.index, "_id": doc.pop("_id", None), "_source": doc}
                for doc in batch
            ]
            success, errors = await async_bulk(self._es, actions, raise_on_error=False)
            total_indexed += success
            total_errors.extend(errors)
            logger.info(
                "Indexed %d documents from '%s' (%d errors so far)",
                total_indexed,
                path,
                len(total_errors),
            )

        return {"indexed": total_indexed, "errors": total_errors}

    # ---------- Search ----------

    async def search(
        self,
        query: dict,
        size: int = 10,
        from_: int = 0,
        sort: list[dict] | None = None,
        source: list[str] | bool | None = None,
    ) -> dict:
        kwargs: dict[str, Any] = {"query": query, "size": size, "from": from_}
        if sort:
            kwargs["sort"] = sort
        if source is not None:
            kwargs["source"] = source
        return (await self._es.search(index=self.index, **kwargs)).body

    async def count(self, query: dict | None = None) -> int:
        kwargs = {"query": query} if query else {}
        return int((await self._es.count(index=self.index, **kwargs))["count"])

    async def scroll(
        self,
        query: dict,
        scroll_ttl: str = "2m",
        size: int = 1000,
    ) -> AsyncGenerator[dict, None]:
        kwargs: dict[str, Any] = {
            "query": query,
            "size": size,
            "sort": [{"_id": "asc"}],
        }
        while True:
            response = (await self._es.search(index=self.index, **kwargs)).body
            hits = response["hits"]["hits"]
            if not hits:
                break
            for hit in hits:
                yield hit
            kwargs["search_after"] = hits[-1]["sort"]

    # ---------- Aggregations ----------

    async def aggregate(self, aggregations: dict, query: dict | None = None) -> dict:
        kwargs: dict[str, Any] = {"aggs": aggregations, "size": 0}
        if query:
            kwargs["query"] = query
        return (await self._es.search(index=self.index, **kwargs)).body.get(
            "aggregations", {}
        )

    # ---------- Cluster / Health ----------

    async def cluster_health(self) -> dict:
        return (await self._es.cluster.health()).body

    async def get_index_stats(self) -> dict:
        return (await self._es.indices.stats(index=self.index)).body

    # ---------- Internal ----------

    @property
    def _es(self) -> AsyncElasticsearch:
        if self._client is None:
            raise RuntimeError(
                "Not connected. Call connect() first (or use as an async context manager)."
            )
        return self._client
