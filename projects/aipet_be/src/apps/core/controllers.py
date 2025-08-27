from typing import Any, Dict

from django.http import HttpRequest
from django.middleware.csrf import get_token
from ninja import Schema
from ninja_extra import ControllerBase, api_controller, http_get
from ninja_extra.permissions import AllowAny


class CsrfTokenResponseSchema(Schema):
    """Schema for CSRF token response."""

    csrf_token: str


@api_controller("/csrf", auth=None, tags=["Security"], permissions=[AllowAny])
class CsrfController(ControllerBase):
    """Controller for CSRF token operations."""

    @http_get("/token", response=CsrfTokenResponseSchema)
    def get_csrf_token(self, request: HttpRequest) -> Dict[str, Any]:
        """
        Get CSRF token for the current session.

        Returns a CSRF token that can be used for subsequent requests.
        This endpoint is accessible without authentication.
        """
        csrf_token = get_token(request)
        return {"csrf_token": csrf_token}
