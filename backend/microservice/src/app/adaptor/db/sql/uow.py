from typing import Dict, Optional
from sqlalchemy.orm import Session

from ..interfaces.db import UOW

from .models.example import CompanyRepository
from .models.scorecard_config import ScorecardConfigRepository
from .models.category import CategoryRepository
from .models.product_taxonomy import ProductTaxRepository
from .models.generative import GenConfigRepository
from .models.feature_flag import FeatureFlagRepository


class SqlUOW(UOW):

    @property
    def example(self) -> CompanyRepository:
        return CompanyRepository(
            session=self._session, required_filters=self._required_filters
        )

    # Used for testing
    def create_all(self):
        from .models.base import Base

        Base.metadata.create_all(self._session.get_bind())

    def drop_all(self):
        from .models.base import Base

        Base.metadata.drop_all(self._session.get_bind())
