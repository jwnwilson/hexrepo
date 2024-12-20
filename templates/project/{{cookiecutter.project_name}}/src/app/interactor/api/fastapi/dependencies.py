import logging
import uuid
from collections.abc import Generator
from pydantic import BaseModel
{% if cookiecutter.use_db == "y" %}
from monorepo_db import UOW
from monorepo_db.sql import get_sql_db_url

from app.adaptor.db.sql import SqlUOW
{% else %}
from monorepo_db import UOW, Repository
from monorepo_db.sql.stub import StubbedRepository

from app.domain.example import ExampleDTO
{% endif %}

logger = logging.getLogger(__name__)


{% if cookiecutter.use_db == "y" %}
def get_uow() -> Generator[UOW, None, None]:
    uow = SqlUOW(db_url=get_sql_db_url())
    with uow.transaction():
        yield uow
{% else %}
class StubbedExampleRepository(StubbedRepository):
    model_dto: ExampleDTO = ExampleDTO

    def _generate_fake_dto(self, obj_in: BaseModel = None) -> BaseModel:
        return self.model_dto(
            id=uuid.uuid4(),
            name="test",
            url="https://test.com",
            location="test location",
        )


class StubbedUOW(UOW):
    @property
    def example(self) -> Repository:
        return StubbedExampleRepository()


def get_uow() -> Generator[UOW, None, None]:
    yield StubbedUOW(db_url="test")
{% endif %}
