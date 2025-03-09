from typing import Any, Dict

import pytest

from app.adaptor.db.interface import UOW, Repository


@pytest.fixture
def test_data_generator(uow: UOW) -> Dict[str, Any]:
    def generator(create_dto):
        def get_repo(create_dto):
            for attr in uow.__class__.__dict__.keys():
                if isinstance(getattr(uow, attr), Repository):
                    if type(create_dto) is getattr(uow, attr).model_dto:
                        return getattr(uow, attr)
            raise NotImplementedError(f"Test data generation failed: Repository for {create_dto.__class__.__name__} not found")

        repo: Repository = get_repo(create_dto)
        return repo.create(create_dto)

    return generator
