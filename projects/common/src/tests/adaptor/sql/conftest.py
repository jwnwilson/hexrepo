import pytest
from pytest_alembic.config import Config
from hexrepo_db.sql.session import DatabaseSessionManager


@pytest.fixture
def alembic_config(alembic_engine):
    """Override this fixture to configure the exact alembic context setup required."""
    return Config.from_raw_config({"sqlalchemy.url": str(alembic_engine.url)})


@pytest.fixture
def alembic_engine(session_maker: DatabaseSessionManager, drop_tables):
    """Override this fixture to provide pytest-alembic powered tests with a database handle."""
    return session_maker.engine
