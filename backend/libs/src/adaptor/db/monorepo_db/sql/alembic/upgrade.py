import logging
import os

from alembic import command
from alembic.config import Config

logger = logging.getLogger(__name__)


def update_db():
    logger.info(f"Running DB migrations")
    alembic_cfg = Config("alembic.ini")

    try:
        command.upgrade(alembic_cfg, "head")
    except Exception as err:
        logger.error(f"Error running DB migrations. {err}")
        raise
    logger.info(f"DB migrations complete")