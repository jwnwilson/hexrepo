
from sqlalchemy import UUID, ForeignKey, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import SQLRepository
from app.domain.user import UserPermissionDTO
from .group import UserGroupsTable, PermissionUsersTable


# Need materialized view on user with permissions for quick auth queries
class UserTable(Base):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(Text, nullable=False, unique=True)    
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String)
    cognito_id: Mapped[str] = mapped_column(String, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("company.id"), nullable=True)
    company: Mapped["CompanyTable"] = relationship("CompanyTable")
    permissions: Mapped[list["PermissionTable"]] = relationship(
        "PermissionTable",
        secondary=PermissionUsersTable.__table__,
        overlaps="users"
    )
    groups: Mapped[list["GroupTable"]] = relationship(
        "GroupTable",
        secondary=UserGroupsTable.__table__,
        overlaps="users"
    )

    def __str__(self) -> str:
        return f"{self.username} | {self.email} | {self.id}"

class UserRepository(SQLRepository):
    model = UserTable
    model_dto = UserPermissionDTO
