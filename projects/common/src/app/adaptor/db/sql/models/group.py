from typing import TYPE_CHECKING, Any

from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import DefaultQuery, SQLRepository
from sqlalchemy import (
    UUID,
    ForeignKey,
    Select,
    String,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.user import GroupPermissionDTO

from .permission import PermissionGroupsTable
from .permission import PermissionUsersTable as PermissionUsersTable

if TYPE_CHECKING:
    from .group import GroupTable
    from .permission import PermissionTable
    from .user import UserTable


# Joining table to link groups to users
class UserGroupsTable(Base):
    __tablename__ = "user_groups"
    __versioned__ = {}

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    group_id: Mapped[UUID] = mapped_column(ForeignKey("group.id"))


class GroupTable(Base):
    __tablename__ = "group"
    __versioned__ = {}

    name: Mapped[str] = mapped_column(String)
    users: Mapped[list["UserTable"]] = relationship(
        "UserTable", secondary=UserGroupsTable.__table__, overlaps="users"
    )
    permissions: Mapped[list["PermissionTable"]] = relationship(
        "PermissionTable", secondary=PermissionGroupsTable.__table__, overlaps="groups"
    )

    def __str__(self) -> str:
        return f"{self.name} | {self.id}"


class UserPermissionQuery(DefaultQuery):
    def query_select(self) -> Select[Any]:
        from .group import GroupTable

        # Query to return list of entities
        return (
            select(self.model)
            .outerjoin(GroupTable.permissions)
            .outerjoin(GroupTable.users)
        )


class GroupRepository(SQLRepository):
    model = GroupTable
    model_dto = GroupPermissionDTO

    def _model_to_dto(self, row):
        return GroupPermissionDTO(
            id=row.id,
            name=row.name,
            permissions=[{"id": str(p.id)} for p in row.permissions],
            users=[{"id": str(u.id)} for u in row.users],
        )
