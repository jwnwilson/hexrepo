from datetime import datetime
from typing import Any

from app.domain.user import get_user
import wtforms
from sqladmin import Admin, ModelView
from starlette.requests import Request
from sqladmin.authentication import AuthenticationBackend
from fastapi import Depends, FastAPI, HTTPException
from hexrepo_cloud.auth.interface import AuthAdapter, UserLogin

from app.adaptor.db.sql.models.company import CompanyTable
from app.adaptor.db.sql.models.feature_flag import FeatureFlagTable
from app.adaptor.db.sql.models.group import GroupTable
from app.adaptor.db.sql.models.permission import PermissionTable
from app.adaptor.db.sql.models.user import UserTable
from app.adaptor.db.sql.uow import SqlUOW
from app.config import config
from app.interactor.dependencies import get_auth, get_uow_ro


class BaseModelView(ModelView):
    def is_visible(self, request: Request) -> bool:
        assert request.user, "User not found"
        return "superadmin" in request.user.permissions

    def is_accessible(self, request: Request) -> bool:
        assert request.user, "User not found"
        return "superadmin" in request.user.permissions
    
    form_widget_args = dict(
        created_at=dict(readonly=True), updated_at=dict(readonly=True)
    )
    form_args = dict(
        created_at=dict(default=datetime.now()), updated_at=dict(default=datetime.now())
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
        UserTable.groups,
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
        UserTable.updated_at,
    ]

    form_overrides = dict(email=wtforms.EmailField)

    form_ajax_refs = {
        "groups": {
            "fields": ("name",),
            "order_by": "created_at",
        },
        "permissions": {
            "fields": ("name",),
            "order_by": "created_at",
        },
    }


class GroupAdmin(BaseModelView, model=GroupTable):
    name = "Group"
    name_plural = "Groups"
    icon = "fa-solid fa-user-group"

    column_searchable_list = [GroupTable.name]

    column_list = [GroupTable.name, GroupTable.id]

    form_ajax_refs = {
        "permissions": {
            "fields": ("name",),
            "order_by": "created_at",
        },
        "users": {
            "fields": ("id", "username", "email"),
            "order_by": "created_at",
        },
    }


class PermissionAdmin(BaseModelView, model=PermissionTable):
    name = "Permission"
    name_plural = "Permissions"
    icon = "fa-solid fa-lock"

    column_searchable_list = [PermissionTable.name]

    column_list = [PermissionTable.name, PermissionTable.id]

    form_ajax_refs = {
        "groups": {
            "fields": ("name",),
            "order_by": "created_at",
        },
        "users": {
            "fields": ("name",),
            "order_by": "created_at",
        },
    }


class FeatureFlagAdmin(BaseModelView, model=FeatureFlagTable):
    name = "Feature Flag"
    name_plural = "Feature Flags"
    icon = "fa-solid fa-flag"

    column_searchable_list = [FeatureFlagTable.name]

    column_list = [
        FeatureFlagTable.name,
        FeatureFlagTable.id,
        FeatureFlagTable.company_id,
    ]

    form_ajax_refs = {
        "company": {
            "fields": ("name",),
            "order_by": "created_at",
        }
    }


class CompanyAdmin(BaseModelView, model=CompanyTable):
    name = "Company"
    name_plural = "Companies"
    icon = "fa-solid fa-building"

    column_searchable_list = [CompanyTable.name]

    column_list = [
        CompanyTable.name,
        CompanyTable.id,
    ]


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        breakpoint()
        # Check this gets cleaned up propery
        auth_gen = get_auth()
        auth: AuthAdapter = next(auth_gen)
        form = await request.form()
        username, password = form["username"], form["password"]

        # Validate username/password credentials
        try:
            resp = auth.login(UserLogin(
                username=username,
                password=password
            ))
        except Exception as e:
            raise HTTPException(status_code=403, detail="Invalid username or password")
        # And update session
        request.session.update({
            "token": resp["access_token"],
            "username": username,
        })

        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        breakpoint()
        auth_gen = get_auth()
        uow_gen = get_uow_ro()
        auth: AuthAdapter = next(auth_gen)
        uow: SqlUOW = next(uow_gen)
        token: str = request.session.get("token")
        username: str = request.session.get("username")

        if not token:
            return False

        auth.verify(token)
        request.user = get_user(uow, username)
        return True


def setup_admin(app: FastAPI):
    engine = SqlUOW(db_url=config.DB_URL).session_manager._engine
    authentication_backend: AdminAuth = AdminAuth(secret_key=config.ADMIN_SECRET)
    admin: Admin = Admin(
        app,
        engine,
        favicon_url="https://jwnwilson.co.uk/images/headshot_500.png",
        authentication_backend=authentication_backend
    )

    admin.add_view(UserAdmin)
    admin.add_view(GroupAdmin)
    admin.add_view(PermissionAdmin)
    admin.add_view(FeatureFlagAdmin)
    admin.add_view(CompanyAdmin)
