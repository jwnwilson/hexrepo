from typing import TYPE_CHECKING, Any

from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import DefaultQuery, SQLRepository
from sqlalchemy import UUID, ForeignKey, Index, Select, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.user import PermissionDTO

if TYPE_CHECKING:
    from .group import GroupTable
    from .permission import PermissionTable
    from .user import UserTable


# Joining table to link permissions to groups
class PermissionGroupsTable(Base):
    __tablename__ = "permission_groups"
    __versioned__ = {}

    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permission.id"))
    group_id: Mapped[UUID] = mapped_column(ForeignKey("group.id"))


# Joining table to link permissions to users
class PermissionUsersTable(Base):
    __tablename__ = "permission_users"
    __versioned__ = {}

    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permission.id"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))


class PermissionTable(Base):
    __tablename__ = "permission"
    __versioned__ = {}

    name: Mapped[str] = mapped_column(String, unique=True)
    groups: Mapped[list["GroupTable"]] = relationship(
        "GroupTable", secondary=PermissionGroupsTable.__table__, overlaps="groups"
    )
    users: Mapped[list["UserTable"]] = relationship(
        "UserTable", secondary=PermissionUsersTable.__table__, overlaps="users"
    )

    def __str__(self) -> str:
        return f"{self.name} | {self.id}"

    __table_args__ = (Index("permission_name_idx", "name"),)


class PermissionQuery(DefaultQuery):
    def query_select(self) -> Select[Any]:
        from .permission import PermissionTable

        # Query to return list of entities
        return (
            select(self.model)
            .outerjoin(PermissionTable.groups)
            .outerjoin(PermissionTable.users)
        )


class PermissionRepository(SQLRepository):
    model = PermissionTable
    model_dto = PermissionDTO

    def _model_to_dto(self, row):
        return PermissionDTO(
            id=row.id,
            name=row.name,
            groups=[{"id": str(g.id)} for g in row.groups],
            users=[{"id": str(u.id)} for u in row.users],
        )
