import json
from enum import Enum
from logging import getLogger
from typing import Any, Callable, List, Optional, Type, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.types import DecoratedCallable
from pydantic import BaseModel

from monorepo_db.exception import IntegrityError, InvalidArgument, RecordNotFound
from monorepo_db.interface import PaginatedData, UOW, Repository


logger = getLogger()


class CrudRouter(APIRouter):
    """
    Dynamically create Create Read Update and Delete methods for our UOW

    Lots of concepts and ideas stolen from this project:
    https://github.com/awtkns/fastapi-crudrouter

    Has the ability to be overriden with regular router functons e.g.

    router_v1 = CrudRouter(
        db_dependency=get_repos,
        repository="company",
        methods=["CREATE", "READ", "UPDATE", "DELETE"],
        response_schema=CompanyDTO,
        create_schema=CreateCompanyDTO,
        update_schema=UpdateCompanyDTO,
    )

    @router_v1.get("/")
    def override_read_multi():
        return "test"
    """

    response_schema: Type[BaseModel]
    create_schema: Type[BaseModel]
    update_schema: Type[BaseModel]

    def __init__(
        self,
        db_dependency: Callable,
        repository: str,
        response_schema: Type[BaseModel],
        methods: List[str],
        create_schema: Type[BaseModel],
        update_schema: Type[BaseModel],
        prefix: Optional[str] = None,
        tags: Optional[List[Union[str, Enum]]] = None,
        paginate: Optional[int] = None,
        **kwargs: Any,
    ):
        self.db_dependency: Callable = db_dependency
        self.repository: str = repository
        self.methods = methods or ["READ"]

        self.response_schema: Type[BaseModel] = response_schema
        self.create_schema: Type[BaseModel] = create_schema
        self.update_schema: Type[BaseModel] = update_schema

        prefix = prefix or ""

        super().__init__(prefix=prefix, tags=tags, redirect_slashes=True, **kwargs)
        self._setup_routes()

    def _setup_routes(self):
        if "CREATE" in self.methods:
            assert self.create_schema
            self.add_api_route(
                "/",
                self._create(),
                methods=["POST"],
                response_model=self.response_schema,
            )
        if "READ" in self.methods:
            self.add_api_route(
                "/{id}",
                self._read(),
                methods=["GET"],
                response_model=self.response_schema,
            )

            self.add_api_route(
                "/",
                self._read_multi(),
                methods=["GET"],
                response_model=PaginatedData[self.response_schema],
            )
        if "UPDATE" in self.methods:
            assert self.update_schema
            self.add_api_route(
                "/{id}",
                self._update(),
                methods=["PATCH"],
                response_model=self.response_schema,
            )
        if "DELETE" in self.methods:
            self.add_api_route(
                "/{id}",
                self._delete(),
                methods=["DELETE"],
                status_code=204,
                response_class=Response,
            )

    @property
    def router(self):
        return self

    def _create(self) -> Callable:
        def create_record(
            obj_in: self.create_schema,  # type: ignore
            uow: UOW = Depends(self.db_dependency),
        ) -> self.response_schema:  # type: ignore
            try:
                repository: Repository = getattr(uow, self.repository)
                result = repository.create(obj_in)
            except IntegrityError as e:
                raise HTTPException(status_code=400, detail=str(e))
            else:
                return result

        return create_record

    def _read(self) -> Callable:
        def read_record(
            id: UUID,
            uow: UOW = Depends(self.db_dependency),
        ) -> self.response_schema:  # type: ignore
            try:
                repository: Repository = getattr(uow, self.repository)
                result: BaseModel = repository.read(id)
            except RecordNotFound as e:
                raise HTTPException(status_code=404, detail=str(e))
            else:
                return result

        return read_record

    def _read_multi(self) -> Callable:
        def read_multiple_records(
            uow: UOW = Depends(self.db_dependency),
            filters: str | None = "{}",
            page_size: int = 0,
            page_number: int = 1,
            order_by: str = "-created_at",
        ) -> PaginatedData:  # type: ignore
            repository: Repository = getattr(uow, self.repository)
            try:
                filters = json.loads(filters)
                return repository.read_multi(
                    filters=filters,
                    page_size=page_size,
                    page_number=page_number,
                    order_by=order_by,
                )
            except InvalidArgument as err:
                raise HTTPException(status_code=400, detail=str(err))

        return read_multiple_records

    def _update(self) -> Callable:
        def update_record(
            id: UUID,
            obj_in: self.update_schema,  # type: ignore
            uow: UOW = Depends(self.db_dependency),
        ) -> self.response_schema:  # type: ignore
            try:
                repository: Repository = getattr(uow, self.repository)
                result = repository.update(id, obj_in)
            except RecordNotFound as e:
                raise HTTPException(status_code=404, detail=str(e))
            except IntegrityError as e:
                raise HTTPException(status_code=400, detail=str(e))
            else:
                return result

        return update_record

    def _delete(self) -> Callable:
        def delete_record(
            id: UUID,
            uow: UOW = Depends(self.db_dependency),
        ):
            try:
                repository: Repository = getattr(uow, self.repository)
                return repository.delete(id)
            except RecordNotFound as e:
                raise HTTPException(status_code=404, detail=str(e))

        return delete_record

    def remove_api_route(self, path: str, methods: List[str]) -> None:
        """
        Used when overriding default routes above, will remove registered
        route to allow a new one to override it.
        """
        methods_ = set(methods)

        for route in self.routes:
            if (
                route.path == f"{self.prefix}{path}"  # type: ignore
                and route.methods == methods_  # type: ignore
            ):
                self.routes.remove(route)

    def get(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["GET"])
        return super().get(path, *args, **kwargs)

    def post(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["POST"])
        return super().post(path, *args, **kwargs)

    def patch(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["PATCH"])
        return super().patch(path, *args, **kwargs)

    def put(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["PUT"])
        return super().put(path, *args, **kwargs)

    def delete(
        self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["DELETE"])
        return super().delete(path, *args, **kwargs)
