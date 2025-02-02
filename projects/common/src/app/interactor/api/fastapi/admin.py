from datetime import datetime
from typing import Any
from fastapi import FastAPI
from sqladmin import Admin, ModelView
from starlette.requests import Request
import wtforms

from app.config import config
from app.adaptor.db.sql.uow import SqlUOW
from app.adaptor.db.sql.models.user import UserTable
from app.adaptor.db.sql.models.group import GroupTable
from app.adaptor.db.sql.models.permission import PermissionTable



class BaseModelView(ModelView):
    form_widget_args = dict(
        created_at=dict(readonly=True),
        updated_at=dict(readonly=True)
    )
    form_args = dict(
        created_at=dict(default=datetime.now()),
        updated_at=dict(default=datetime.now())
    )

    column_sortable_list = ["created_at"]

    async def on_model_change(
        self, data: dict, model: Any, is_created: bool, request: Request
    ) -> None:
        """Perform some actions before a model is created or updated.
        By default does nothing.
        """
        data["updated_at"] = datetime.now().replace(microsecond=0)


class UserAdmin(BaseModelView, model=UserTable):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    column_searchable_list = [UserTable.username, UserTable.email]

    column_list = [
        UserTable.username,
        UserTable.email,
        UserTable.id,
    ]
    form_columns = [
        UserTable.username,
        UserTable.email,
        UserTable.name,
        UserTable.cognito_id,
        UserTable.verified,
        UserTable.permissions,
        UserTable.groups
    ]
    column_details_list = [
        UserTable.id,
        UserTable.username,
        UserTable.email,
        UserTable.name,
        UserTable.cognito_id,
        UserTable.verified,
        UserTable.permissions,
        UserTable.groups,
        UserTable.created_at,
        UserTable.updated_at
    ]

    form_overrides = dict(
        email=wtforms.EmailField
    )

    form_ajax_refs = {
        "groups": {
            "fields": ("name",),
            "order_by": "created_at",
        },
        "permissions": {
            "fields": ("name",),
            "order_by": "created_at",
        }
    }


class GroupAdmin(BaseModelView, model=GroupTable):
    name = "Group"
    name_plural = "Groups"
    icon = "fa-solid fa-user-group"

    column_searchable_list = [GroupTable.name]

    column_list = [
        GroupTable.name,
        GroupTable.id
    ]

    form_ajax_refs = {
        "permissions": {
            "fields": ("name",),
            "order_by": "created_at",
        },
        "users": {
            "fields": ("id","username", "email"),
            "order_by": "created_at",
        }
    }


class PermissionAdmin(BaseModelView, model=PermissionTable):
    name = "Permission"
    name_plural = "Permissions"
    icon = "fa-solid fa-lock"

    column_searchable_list = [PermissionTable.name]

    column_list = [
        PermissionTable.name,
        PermissionTable.id
    ]

    form_ajax_refs = {
        "groups": {
            "fields": ("name",),
            "order_by": "created_at",
        },
        "users": {
            "fields": ("name",),
            "order_by": "created_at",
        }
    }


def setup_admin(app: FastAPI):
    engine = SqlUOW(db_url=config.DB_URL).session_manager._engine
    admin: Admin = Admin(
        app,
        engine,
        favicon_url="https://jwnwilson.co.uk/images/headshot_500.png"
    )

    admin.add_view(UserAdmin)
    admin.add_view(GroupAdmin)
    admin.add_view(PermissionAdmin)
