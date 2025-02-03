
from typing import Any
from sqlalchemy import UUID, Column, ForeignKey, Select, String, Table, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import DefaultQuery, SQLRepository
from app.domain.user import PermissionDTO


# Joining table to link permissions to groups
class PermissionGroupsTable(Base):
    __tablename__ = "permission_groups"

    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permission.id"))
    group_id: Mapped[UUID] = mapped_column(ForeignKey("group.id"))


# Joining table to link permissions to users
class PermissionUsersTable(Base):
    __tablename__ = "permission_users"

    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permission.id"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))


class PermissionTable(Base):
    __tablename__ = "permission"

    name: Mapped[str] = mapped_column(String)
    groups: Mapped[list["GroupTable"]] = relationship(
        "GroupTable",
        secondary=PermissionGroupsTable.__table__,
        overlaps="groups"
    )
    users: Mapped[list["UserTable"]] = relationship(
        "UserTable",
        secondary=PermissionUsersTable.__table__,
        overlaps="users"
    )

    def __str__(self) -> str:
        return f"{self.name} | {self.id}"


class PermissionQuery(DefaultQuery):
    def update_relationships(self, db_obj, dto):
        return super().update_relationships(db_obj, dto)
    
    def query_multi(self) -> Select[Any]:
        from .permission import PermissionTable
        # Query to return list of entities
        default_query = select(self.model).outerjoin(PermissionTable.groups).outerjoin(PermissionTable.users)
        query = self._apply_default_filters(default_query)
        # Load relationships
        return query


class PermissionRepository(SQLRepository):
    model = PermissionTable
    model_dto = PermissionDTO

    def _model_to_dto(self, row):
        return PermissionDTO(
            id=row.id,
            name=row.name,
            groups=[str(g.id) for g in row.groups],
            users=[str(u.id) for u in row.users],
        )
