from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import SQLRepository
from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.user import CompanyDTO


class CompanyTable(Base):
    __tablename__ = "company"

    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    website: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    def __str__(self) -> str:
        return f"{self.name} | {self.id}"


class CompanyRepository(SQLRepository):
    model = CompanyTable
    model_dto = CompanyDTO
