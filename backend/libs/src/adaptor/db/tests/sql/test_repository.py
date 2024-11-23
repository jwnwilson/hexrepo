from typing import Dict
import uuid

import pytest
from monorepo_db.interface import UOW
from monorepo_db.sql.models.example import ExampleDTO, ExampleCreateDTO, ExampleUpdateDTO
from monorepo_db.exception import IntegrityError, RecordNotFound


def test_repository_create_company(uow: UOW):
    example_create: ExampleDTO = uow.example.create(
        ExampleCreateDTO(name="Test Co", url="https://test.com", id=uuid.uuid4())
    )
    example_get: ExampleDTO = uow.example.read(example_create.id)

    assert example_create == example_get


def test_repository_create_duplicate_id(
    uow: UOW
):
    with pytest.raises(IntegrityError):
        for x in range(2):
            uow.example.create(
                ExampleCreateDTO(
                    name="example1", url="https://test.com"
                )
            )


def test_repository_read_err_if_not_found(uow: UOW):
    with pytest.raises(RecordNotFound):
        id_not_repo = uuid.uuid4()
        uow.example.read(id=id_not_repo)


def test_repository_read_multi(uow: UOW, example_records):
    read_multi: ExampleDTO = uow.example.read_multi()

    assert read_multi.total == len(example_records)


def test_repository_read_multi_filter_in(uow: UOW, example_records: Dict[str, ExampleDTO]):
    assert len(example_records) == 2

    read_multi: ExampleDTO = uow.example.read_multi(
        filters={"id__in": [list(example_records.values())[0].id]}
    )

    assert read_multi.total == 1
    assert len(read_multi.results) == 1


def test_repository_update(uow: UOW):
    create: ExampleDTO = uow.example.create(
        ExampleCreateDTO(name="Initial Co", url="https://test.com")
    )
    update: ExampleDTO = uow.example.update(
        id=create.id, obj_in=ExampleUpdateDTO(name="Update Ex")
    )
    get: ExampleDTO = uow.example.read(update.id)
    assert update == get


def test_repository_update_err_if_not_found(
    uow: UOW,
):
    with pytest.raises(RecordNotFound):
        id_not_repo = uuid.uuid4()
        uow.example.update(
            id=id_not_repo, obj_in=ExampleUpdateDTO(name="Update Co")
        )


def test_repository_delete(uow: UOW):
    create = uow.example.create(
        ExampleCreateDTO(name="Delete Co", url="https://test.com")
    )
    uow.example.delete(create.id)
    with pytest.raises(RecordNotFound):
        uow.example.read(create.id)


def test_repository_delete_err_if_not_found(
    uow: UOW,
):
    with pytest.raises(RecordNotFound):
        uow.example.delete(uuid.uuid4())
