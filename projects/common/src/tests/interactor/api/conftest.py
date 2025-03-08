from typing import Any, Dict

import pytest

from app.adaptor.db.interface import UOW
from app.domain.user import CompanyDTO


@pytest.fixture
def test_data_generator(uow: UOW) -> Dict[str, Any]:
    def generator(create_dto):
        def get_repo_name(create_dto):
            if isinstance(create_dto, CompanyDTO):
                return "company"
            return "feature_flag"
        repo = get_repo_name(create_dto)
        return getattr(uow, repo).create(create_dto)
    return generator