
from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import SQLRepository
from app.domain.user import CompanyDTO


class CompanyTable(Base):
    __tablename__ = "company"

    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)    
    website: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class CompanyRepository(SQLRepository):
    model = CompanyTable
    model_dto = CompanyDTO
