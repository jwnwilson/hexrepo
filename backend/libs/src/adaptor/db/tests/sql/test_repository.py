import uuid

import pytest
from monorepo_db.sql.uow import BaseSqlUOW
from monorepo_db.interface import UOW
from monorepo_db.sql.models.example import ExampleDTO, CreateExampleDTO


def test_repository_create_company(uow: UOW):
    example_create: ExampleDTO = uow.example.create(
        CreateExampleDTO(name="Test Co", url="https://test.com", id=uuid.uuid4())
    )
    example_get: ExampleDTO = uow.example.read(example_create.id)

    assert example_create == example_get


# def test_repository_create_company_duplicate_id(
#     repositories: SQLRepositories, create_company
# ):
#     with pytest.raises(IntegrityError):
#         repositories.company.create(
#             CompanyDTO(
#                 name="Company", url=create_company[0].url, id=create_company[0].id
#             )
#         )


# def test_repository_create_company_duplicate_name(
#     repositories: SQLRepositories, create_company
# ):
#     with pytest.raises(IntegrityError):
#         repositories.company.create(
#             CompanyDTO(
#                 name=create_company[0].name, url="https://dupe.co", id=uuid.uuid4()
#             )
#         )


# def test_repository_read_err_if_company_not_found(repositories: SQLRepositories):
#     with pytest.raises(RecordNotFound):
#         id_not_repo = uuid.uuid4()
#         repositories.company.read(id=id_not_repo)


# def test_repository_read_multi(repositories: SQLRepositories, create_company):
#     company_read_multi: CompanyDTO = repositories.company.read_multi()

#     assert company_read_multi.total == len(create_company)


# def test_repository_read_multi_filter_in(repositories: SQLRepositories, create_company):
#     assert len(create_company) == 2

#     company_read_multi: CompanyDTO = repositories.company.read_multi(
#         filters={"id__in": [create_company[0].id]}
#     )

#     assert company_read_multi.total == 1
#     assert len(company_read_multi.results) == 1


# def test_repository_update_company(repositories: SQLRepositories):
#     company_create = repositories.company.create(
#         CompanyDTO(name="Initial Co", url="https://test.com", id=uuid.uuid4())
#     )
#     company_update: CompanyDTO = repositories.company.update(
#         id=company_create.id, obj_in=CompanyUpdateDTO(name="Update Co")
#     )
#     company_get: CompanyDTO = repositories.company.read(company_create.id)
#     assert company_update == company_get


# def test_repository_update_company_err_if_company_not_found(
#     repositories: SQLRepositories,
# ):
#     with pytest.raises(RecordNotFound):
#         id_not_repo = uuid.uuid4()
#         repositories.company.update(
#             id=id_not_repo, obj_in=CompanyUpdateDTO(name="Update Co")
#         )


# def test_repository_delete_company(repositories: SQLRepositories):
#     company_create = repositories.company.create(
#         CompanyDTO(name="Delete Co", url="https://test.com", id=uuid.uuid4())
#     )
#     repositories.company.delete(company_create.id)
#     with pytest.raises(RecordNotFound):
#         repositories.company.read(company_create.id)


# def test_repository_delete_company_err_if_company_not_found(
#     repositories: SQLRepositories,
# ):
#     with pytest.raises(RecordNotFound):
#         repositories.company.delete(uuid.uuid4())
