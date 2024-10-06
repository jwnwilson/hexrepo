import os
from collections.abc import Generator

from app.adapter.db import SQLALchemyAdapter
from app.ports.db import DbAdapter

DB_URL = os.environ["DB_URL"]


def get_db() -> Generator[DbAdapter, None, None]:
    adapter = SQLALchemyAdapter(DB_URL)
    with adapter.transaction():
        yield adapter
