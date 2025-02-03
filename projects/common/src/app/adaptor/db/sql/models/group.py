
from typing import Any
from sqlalchemy import UUID, Column, ForeignKey, Select, String, Table, Text, Boolean, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import DefaultQuery, SQLRepository
from app.domain.user import GroupPermissionDTO
from .permission import PermissionGroupsTable, PermissionUsersTable as PermissionUsersTable


# Joining table to link groups to users
class UserGroupsTable(Base):
    __tablename__ = "user_groups"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    group_id: Mapped[UUID] = mapped_column(ForeignKey("group.id"))


class GroupTable(Base):
    __tablename__ = "group"

    name: Mapped[str] = mapped_column(String)
    users: Mapped[list["UserTable"]] = relationship(
        "UserTable",
        secondary=UserGroupsTable.__table__,
        overlaps="users"
    )
    permissions: Mapped[list["PermissionTable"]] = relationship(
        "PermissionTable",
        secondary=PermissionGroupsTable.__table__,
        overlaps="groups"
    )

    def __str__(self) -> str:
        return f"{self.name} | {self.id}"


class UserPermissionQuery(DefaultQuery):
    def update_relationships(self, db_obj, dto):
        return super().update_relationships(db_obj, dto)
    
    def query_multi(self) -> Select[Any]:
        from .group import GroupTable
        # Query to return list of entities
        default_query = select(self.model).outerjoin(GroupTable.permissions).outerjoin(GroupTable.users)
        query = self._apply_default_filters(default_query)
        # Load relationships
        return query


class GroupRepository(SQLRepository):
    model = GroupTable
    model_dto = GroupPermissionDTO

    def _model_to_dto(self, row):
        return GroupPermissionDTO(
            id=row.id,
            name=row.name,
            permissions=[str(p.id) for p in row.permissions],
            users=[str(u.id) for u in row.users]
        )
