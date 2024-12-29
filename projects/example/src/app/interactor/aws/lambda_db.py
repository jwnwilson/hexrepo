import logging

from hexrepo_db.sql.alembic import update_db

# Initialize you log configuration using the base class
logging.basicConfig(level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)


def handler(event, context):
    update_db()
