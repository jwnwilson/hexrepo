from typing import Dict, Optional
from sqlalchemy.orm import Session

from ..interfaces.db import UOW

from .models.example import ExampleRepository


class SqlUOW(UOW):

    @property
    def example(self) -> CompanyRepository:
        return CompanyRepository(
            session=self._session, required_filters=self._required_filters
        )

    # Used for testing
    def create_all(self):
        from .models.base_model import Base

        Base.metadata.create_all(self._session.get_bind())

    def drop_all(self):
        from .models.base_model import Base

        Base.metadata.drop_all(self._session.get_bind())
