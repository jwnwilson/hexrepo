from typing import TYPE_CHECKING, Any, Type

from hexrepo_db.sql.interface import Query
from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import DefaultQuery, SQLRepository
from sqlalchemy import UUID, Boolean, ForeignKey, Select, String, Text, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.user import UserPermissionDTO

from .group import PermissionUsersTable, UserGroupsTable

if TYPE_CHECKING:
    from .company import CompanyTable
    from .group import GroupTable
    from .permission import PermissionTable


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
        "PermissionTable", secondary=PermissionUsersTable.__table__, overlaps="users"
    )
    groups: Mapped[list["GroupTable"]] = relationship(
        "GroupTable", secondary=UserGroupsTable.__table__, overlaps="users"
    )

    def __str__(self) -> str:
        return f"{self.username} | {self.email} | {self.id}"


class UserPermissionQuery(DefaultQuery):
    def query_select(self) -> Select[Any]:
        from .user import UserTable

        # Query to return list of entities
        return (
            select(self.model)
            .outerjoin(UserTable.permissions)
            .outerjoin(UserTable.groups)
            .outerjoin(UserTable.company)
        )


class UserRepository(SQLRepository):
    model = UserTable
    model_dto = UserPermissionDTO
    query_logic: Type[Query] = UserPermissionQuery

    def _model_to_dto(self, row):
        return UserPermissionDTO(
            id=row.id,
            username=row.username,
            email=row.email,
            name=row.name,
            cognito_id=row.cognito_id,
            verified=row.verified,
            permissions=[{"id": p.id, "name": p.name} for p in row.permissions],
            groups=[{"id": p.id, "name": p.name} for p in row.groups],
            company=row.company.id if row.company else None,
        )
