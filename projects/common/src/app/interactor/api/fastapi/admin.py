import json
from datetime import datetime
from typing import Any

import wtforms
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from hexrepo_cloud.auth.cognito.auth_adaptor import CognitoAuthAdapter
from hexrepo_cloud.auth.interface import AuthAdapter, UserLogin
from hexrepo_db.sql.config import get_sql_db_url
from hexrepo_task.interactor.event.app import resolve_dependencies
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.adaptor.db.sql.models.company import CompanyTable
from app.adaptor.db.sql.models.feature_flag import FeatureFlagTable
from app.adaptor.db.sql.models.group import GroupTable
from app.adaptor.db.sql.models.permission import PermissionTable
from app.adaptor.db.sql.models.user import UserTable
from app.adaptor.db.sql.uow import SqlUOW
from app.config import config
from app.domain.user import UserManager
from app.interactor.dependencies import get_jwt_token, get_user_manager


class BaseModelView(ModelView):
    def get_user_permissions(self, request: Request) -> list[str]:
        assert "user" in request.session, "User not found"
        permissions = []
        try:
            permissions = [x["name"] for x in request.session["user"]["permissions"]]
        except KeyError:
            pass
        return permissions

    def is_visible(self, request: Request) -> bool:
        return "superadmin" in self.get_user_permissions(request)

    def is_accessible(self, request: Request) -> bool:
        return "superadmin" in self.get_user_permissions(request)

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
    column_details_exclude_list = ["versions"]

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
    column_details_exclude_list = ["versions"]

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
    ]


class CompanyAdmin(BaseModelView, model=CompanyTable):
    name = "Company"
    name_plural = "Companies"
    icon = "fa-solid fa-building"

    column_searchable_list = [CompanyTable.name]

    column_list = [
        CompanyTable.name,
        CompanyTable.id,
    ]


def on_auth_error(request: Request, exc: Exception):
    return JSONResponse({"error": str(exc)}, status_code=401)


class AdminAuth(AuthenticationBackend):
    @property
    def auth(self) -> AuthAdapter:
        return CognitoAuthAdapter()

    async def login(self, request: Request) -> bool:
        # Check this gets cleaned up propery
        form = await request.form()
        username, password = form["username"], form["password"]
        # Validate username/password credentials
        try:
            access_token: str = self.auth.login(
                UserLogin(username=username, password=password)
            )
        except Exception:
            raise HTTPException(
                status_code=403,
                detail="Invalid username, password or unverified account",
            )
        # And update session
        request.session.update(
            {
                "token": access_token,
            }
        )

        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    @resolve_dependencies
    async def authenticate(
        self, request: Request, user_manager: UserManager = Depends(get_user_manager)
    ) -> bool:
        token: str = request.session.get("token")
        if not token:
            return False
        # Verify jwt token
        jwt = get_jwt_token.verify_jwt_token(token)
        username = jwt.claims["username"]
        if "user" not in request.session:
            user = user_manager.get_user(username)
            request.session.update(
                {
                    "user": json.loads(user.model_dump_json()),
                }
            )
        return True


def setup_admin(app: FastAPI):
    engine = SqlUOW(db_url=get_sql_db_url()).session_manager._engine
    authentication_backend: AdminAuth = AdminAuth(secret_key=config.SESSION_SECRET)
    admin: Admin = Admin(
        app,
        engine,
        favicon_url="https://jwnwilson.co.uk/images/headshot_500.png",
        authentication_backend=authentication_backend,
    )

    admin.add_view(UserAdmin)
    admin.add_view(GroupAdmin)
    admin.add_view(PermissionAdmin)
    admin.add_view(FeatureFlagAdmin)
    admin.add_view(CompanyAdmin)
