from typing import Any, Callable, List, Optional, Type

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.ports.db import DbAdapter, Repository


class PaginatedData(BaseModel):
    data: Any
    total: int
    page: int
    page_number: int


class CrudRouter:
    response_schema: Type[BaseModel]
    create_schema: Type[BaseModel]
    update_schema: Type[BaseModel]

    def __init__(
        self,
        db_dependency: Callable,
        respository: str,
        response_schema: Type[BaseModel],
        methods: List[str],
        create_schema: Type[BaseModel],
        update_schema: Type[BaseModel],
    ):
        self.db_dependency: Callable = db_dependency
        self.repository: str = respository
        self.methods = methods or ["READ"]

        self.response_schema: Type[BaseModel] = response_schema
        self.create_schema: Type[BaseModel] = create_schema
        self.update_schema: Type[BaseModel] = update_schema

        self._router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        if "CREATE" in self.methods:
            assert self.create_schema
            self._router.add_api_route(
                "/",
                self.create(),
                methods=["POST"],
                response_model=self.response_schema,
            )
        if "READ" in self.methods:
            self._router.add_api_route(
                "/{id}",
                self.read(),
                methods=["GET"],
                response_model=self.response_schema,
            )

            self._router.add_api_route(
                "/",
                self.read_multi(),
                methods=["GET"],
                response_model=PaginatedData,
            )
        if "UPDATE" in self.methods:
            assert self.update_schema
            self._router.add_api_route(
                "/{id}",
                self.update(),
                methods=["PATCH"],
                response_model=self.response_schema,
            )
        if "DELETE" in self.methods:
            self._router.add_api_route(
                "/{id}",
                self.delete(),
                methods=["DELETE"],
            )

    @property
    def router(self):
        return self._router

    def create(self) -> Callable:
        def create_record(
            obj_in: self.create_schema,  # type: ignore
            db: DbAdapter = Depends(self.db_dependency),
        ) -> self.response_schema:  # type: ignore
            repositry: Repository = getattr(db, self.repository)
            return repositry.create(obj_in)

        return create_record

    def read(self) -> Callable:
        def read_record(
            id: str,
            db: DbAdapter = Depends(self.db_dependency),
        ) -> self.response_schema:  # type: ignore
            repositry: Repository = getattr(db, self.repository)
            return repositry.read(id)

        return read_record

    def read_multi(self) -> Callable:
        def read_multiple_records(
            db: DbAdapter = Depends(self.db_dependency),
        ) -> PaginatedData:  # type: ignore
            repositry: Repository = getattr(db, self.repository)
            return repositry.read_multi()

        return read_multiple_records

    def update(self) -> Callable:
        def update_record(
            id: str,
            obj_in: self.update_schema,  # type: ignore
            db: DbAdapter = Depends(self.db_dependency),
        ) -> self.response_schema:  # type: ignore
            repositry: Repository = getattr(db, self.repository)
            return repositry.update(id, obj_in)

        return update_record

    def delete(self) -> Callable:
        def delete_record(
            id: str,
            db: DbAdapter = Depends(self.db_dependency),
        ):
            repositry: Repository = getattr(db, self.repository)
            return repositry.delete(id)

        return delete_record
