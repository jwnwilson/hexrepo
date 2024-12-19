from collections.abc import Generator
from typing import Any
from unittest.mock import Mock


def get_uow() -> Generator[Any, None, None]:
    yield Mock()
