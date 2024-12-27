from monorepo_db.interface import UOW
from monorepo_db.sql.models.example import (
    ExampleCreateDTO,
    ExampleDTO,
)


def test_mongo_create_company(uow_mongo: UOW) -> None:
    example_create: ExampleDTO = uow_mongo.example.create(
        ExampleCreateDTO(name="Test Co", url="https://test.com")
    )
    example_get: ExampleDTO = uow_mongo.example.read(example_create.id)

    assert example_create == example_get
