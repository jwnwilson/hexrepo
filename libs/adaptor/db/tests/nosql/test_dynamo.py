from monorepo_db.interface import UOW
from monorepo_db.sql.models.example import (
    ExampleCreateDTO,
    ExampleDTO,
)


def test_dynamodb_create_company(uow_dynamo: UOW) -> None:
    example_create: ExampleDTO = uow_dynamo.example.create(
        ExampleCreateDTO(name="Test Co", url="https://test.com")
    )
    example_get: ExampleDTO = uow_dynamo.example.read(example_create.id)

    assert example_create == example_get
