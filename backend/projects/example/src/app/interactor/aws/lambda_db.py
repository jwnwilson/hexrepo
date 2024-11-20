import logging

from monorepo_db.sql.alembic import update_db
from .secrets import get_db_url_from_aws_secret

# Initialize you log configuration using the base class
logging.basicConfig(level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)


def handler(event, context):
    db_url: str = get_db_url_from_aws_secret()
    update_db(db_url)
