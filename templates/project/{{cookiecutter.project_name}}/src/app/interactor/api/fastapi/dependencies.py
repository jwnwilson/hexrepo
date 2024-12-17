from collections.abc import Generator
{% if cookiecutter.use_db == "y" %}
from monorepo_db import UOW
from monorepo_db.sql import get_sql_db_url

from app.adaptor.db.sql import SqlUOW
{% else %}
from unittest.mock import Mock
{% endif %}

def get_uow() -> Generator[UOW, None, None]:
    {% if cookiecutter.use_db == "y" %}
    uow = SqlUOW(db_url=get_sql_db_url())
    with uow.transaction():
        yield uow
    {% else %}
    yield Mock()
    {% endif %}
