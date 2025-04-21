from typing import Any, Dict

import pytest

from app.adaptor.db.interface import UOW, Repository
from app.domain.user import EnvironmentCreateDTO
from app.domain.feature_flags import FeatureFlagCreateDTO

DTO_REPO_MAP = {
    FeatureFlagCreateDTO: "feature_flag",
}


@pytest.fixture
def create_environments(uow: UOW) -> None:
    """Create test environments."""
    for env in ["dev", "staging", "production"]:
        uow.environment.create(
            EnvironmentCreateDTO(
                name=env,
                config={"test_key": "value"},
            )
        )


@pytest.fixture
def test_data_generator(uow: UOW) -> Dict[str, Any]:
    def generator(create_dto):
        def get_repo(create_dto):
            if type(create_dto) in DTO_REPO_MAP:
                return getattr(uow, DTO_REPO_MAP[type(create_dto)])
            for attr in uow.__class__.__dict__.keys():
                if isinstance(getattr(uow, attr), Repository):
                    if type(create_dto) is getattr(uow, attr).model_dto:
                        return getattr(uow, attr)
            raise NotImplementedError(
                f"Test data generation failed: Repository for {create_dto.__class__.__name__} not found"
            )

        repo: Repository = get_repo(create_dto)
        resp = repo.create(create_dto)
        return resp

    return generator
