import json
from datetime import datetime
from typing import Any

import anyio
from sqlalchemy import select
import wtforms
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from hexrepo_cloud.auth.cognito.auth_adaptor import CognitoAuthAdapter
from hexrepo_cloud.auth.interface import AuthAdapter, UserLogin
from hexrepo_db.sql.config import get_sql_db_url
from hexrepo_task.interactor.event.app import resolve_dependencies
from sqladmin import Admin, ModelView
from sqladmin._queries import Query
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.adaptor.db.sql.models.company import CompanyTable
from app.adaptor.db.sql.models.environment import EnvironmentTable
from app.adaptor.db.sql.models.feature_flag import FeatureFlagEnvTable, FeatureFlagTable
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


class PatchedQuery(Query):
    # Patching bug in delete method on eager joins
    def _delete_sync(self, pk, request):
        with self.model_view.session_maker() as session:
            obj = (
                session.execute(self._get_delete_stmt(pk)).unique().scalar_one_or_none()
            )
            anyio.from_thread.run(self.model_view.on_model_delete, obj, request)
            session.delete(obj)
            session.commit()
            anyio.from_thread.run(self.model_view.after_model_delete, obj, request)


class FeatureFlagAdmin(BaseModelView, model=FeatureFlagTable):
    name = "Feature Flag"
    name_plural = "Feature Flags"
    icon = "fa-solid fa-flag"

    column_searchable_list = [FeatureFlagTable.name]

    column_list = [
        FeatureFlagTable.name,
        FeatureFlagTable.id,
    ]

    form_ajax_refs = {
        "environments": {
            "fields": ("env",),
            "order_by": "created_at",
        }
    }

    async def delete_model(self, request: Request, pk: Any) -> None:
        await PatchedQuery(self).delete(pk, request)

    async def after_model_change(self, data, model, is_created, request):
        if is_created:
            with self.session_maker() as session:
                # Get the feature flag object
                env_list = session.execute(select(EnvironmentTable)).all()
                if not env_list:
                    raise ValueError(
                        "No environments found in the database, please create environments for feature flags"
                    )
                # Create the feature flag env objects
                for env in env_list:
                    feature_flag_env = FeatureFlagEnvTable(
                        env=env[0].name,
                        enabled=False,
                        feature_flag_id=model.id,
                    )
                    session.add(feature_flag_env)
                session.commit()


class FeatureFlagEnvAdmin(BaseModelView, model=FeatureFlagEnvTable):
    name = "Feature Flag Environment"
    name_plural = "Feature Flag Environments"
    icon = "fa-solid fa-flag"

    column_searchable_list = [FeatureFlagEnvTable.env, "feature_flag.name"]

    column_list = [
        FeatureFlagEnvTable.env,
        FeatureFlagEnvTable.id,
        "feature_flag.name",
        FeatureFlagEnvTable.enabled,
    ]

    form_ajax_refs = {
        "feature_flag": {
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


class Environment(BaseModelView, model=EnvironmentTable):
    name = "Environment"
    name_plural = "Environments"
    icon = "fa-solid fa-cloud"

    column_searchable_list = [EnvironmentTable.name]

    column_list = [
        EnvironmentTable.name,
        EnvironmentTable.id,
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
    admin.add_view(FeatureFlagEnvAdmin)
    admin.add_view(CompanyAdmin)
    admin.add_view(Environment)
