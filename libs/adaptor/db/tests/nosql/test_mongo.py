import uuid
from typing import Any, Dict, Optional

import pytest

from monorepo_db.exception import RecordNotFound
from monorepo_db.interface import UOW, PaginatedData
from monorepo_db.sql.models.example import (
    ExampleCreateDTO,
    ExampleDTO,
    ExampleUpdateDTO,
)


def test_mongo_create_company(uow_mongo: UOW) -> None:
    example_create: ExampleDTO = uow_mongo.example.create(
        ExampleCreateDTO(name="Test Co", url="https://test.com")
    )
    example_get: ExampleDTO = uow_mongo.example.read(example_create.id)

    assert example_create == example_get


def test_mongo_read_err_if_not_found(uow_mongo: UOW) -> None:
    with pytest.raises(RecordNotFound):
        id_not_repo = uuid.uuid4()
        uow_mongo.example.read(id=id_not_repo)


def test_mongo_read_multi(
    uow_mongo: UOW, example_records_mongo: Dict[str, ExampleDTO]
) -> None:
    read_multi: PaginatedData[Any] = uow_mongo.example.read_multi()

    assert read_multi.total == len(example_records_mongo)


def test_mongo_read_multi_filter_in(
    uow_mongo: UOW, example_records_mongo: Dict[str, ExampleDTO]
) -> None:
    assert len(example_records_mongo) == 2

    read_multi: PaginatedData[Any] = uow_mongo.example.read_multi(
        filters={"id__in": [str(list(example_records_mongo.values())[0].id)]}
    )

    assert read_multi.total == 1
    assert len(read_multi.results) == 1


def test_mongo_update(uow_mongo: UOW) -> None:
    create: ExampleDTO = uow_mongo.example.create(
        ExampleCreateDTO(name="Initial Co", url="https://test.com")
    )
    update: Optional[ExampleDTO] = uow_mongo.example.update(
        id=create.id, obj_in=ExampleUpdateDTO(name="Update Ex")
    )
    assert update is not None
    get: Optional[ExampleDTO] = uow_mongo.example.read(update.id)
    assert update == get


def test_mongo_update_err_if_not_found(
    uow_mongo: UOW,
) -> None:
    with pytest.raises(RecordNotFound):
        id_not_repo = uuid.uuid4()
        uow_mongo.example.update(
            id=id_not_repo, obj_in=ExampleUpdateDTO(name="Update Co")
        )


def test_mongo_delete(uow_mongo: UOW) -> None:
    create = uow_mongo.example.create(
        ExampleCreateDTO(name="Delete Co", url="https://test.com")
    )
    uow_mongo.example.delete(create.id)
    with pytest.raises(RecordNotFound):
        uow_mongo.example.read(create.id)


def test_mongo_delete_err_if_not_found(
    uow_mongo: UOW,
) -> None:
    with pytest.raises(RecordNotFound):
        uow_mongo.example.delete(uuid.uuid4())
