import logging
import os

from alembic import command
from alembic.config import Config

logger = logging.getLogger(__name__)


def update_db(db_url: str):
    logger.info(f"Running DB migrations on {db_url}")
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    try:
        command.upgrade(alembic_cfg, "head")
    except Exception as err:
        logger.error(f"Error running DB migrations on {db_url}. {err}")
        raise
    logger.info(f"DB migrations complete on {db_url}")