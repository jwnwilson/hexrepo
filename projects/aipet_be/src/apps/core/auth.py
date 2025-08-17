from typing import Any, Optional

from asgiref.sync import sync_to_async
from django.conf import settings
from django.http import HttpRequest

from ninja.security.apikey import APIKeyCookie
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.exceptions import AuthenticationFailed, InvalidToken
from ninja_jwt.settings import api_settings

from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _


class SessionAuthAsync(APIKeyCookie):
    "Reusing Django session authentication"

    param_name: str = settings.SESSION_COOKIE_NAME

    async def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[Any]:
        user = await request.auser()
        if user.is_authenticated:
            return user

        return None
    

class JWTAuthAsync(JWTAuth):
    async def authenticate(self, request: HttpRequest, token: str) -> Any:
        return await self.jwt_authenticate(request, token)
    
    @sync_to_async
    def get_user(self, validated_token) -> AbstractUser:
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError as e:
            raise InvalidToken(
                _("Token contained no recognizable user identification")
            ) from e

        try:
            user = self.user_model.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except self.user_model.DoesNotExist as e:
            raise AuthenticationFailed(_("User not found")) from e

        if not user.is_active:
            raise AuthenticationFailed(_("User is inactive"))

        return user