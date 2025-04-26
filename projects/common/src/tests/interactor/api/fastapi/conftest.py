import pytest

from app.adaptor.db.sql.models.environment import EnvironmentTable


@pytest.fixture
def feature_flag_env_data():
    return {"env": "dev", "enabled": True, "overrides": {"user_id": "123"}}


@pytest.fixture
def setup_environments(uow):
    """Fixture to create test environments in the database"""
    environments = [
        {"name": "dev", "config": {"type": "development"}},
        {"name": "staging", "config": {"type": "staging"}},
        {"name": "prod", "config": {"type": "production"}},
    ]

    for env in environments:
        environment = EnvironmentTable(**env)
        uow.session.add(environment)
    uow.session.commit()
    return environments


@pytest.fixture
def feature_flag_data():
    return {"name": "test_flag", "enabled": True}
