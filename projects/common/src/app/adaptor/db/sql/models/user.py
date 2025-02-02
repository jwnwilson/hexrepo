
from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import SQLRepository
from app.domain.user import UserPermissionDTO


class UserTable(Base):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(Text, nullable=False, unique=True)    
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String)
    cognito_id: Mapped[str] = mapped_column(String, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)


class UserRepository(SQLRepository):
    model = UserTable
    model_dto = UserPermissionDTO
