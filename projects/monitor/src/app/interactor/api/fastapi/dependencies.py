from collections.abc import Generator
from unittest.mock import Mock

def get_uow() -> Generator[UOW, None, None]:
    yield Mock()
