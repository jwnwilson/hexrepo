import uuid
from typing import Dict, Optional

from starlette.types import Receive, Scope, Send

from hexrepo_log.log import log_manager


class LogMiddleware:
    def __init__(self, app, header_name: str = "X-Request-ID"):
        self.app = app
        self.header_name = header_name

    def _get_correlation_id(self, scope: Scope) -> str:
        headers: Dict = dict(scope["headers"])
        correlation_id_bytes: Optional[bytes] = headers.get(
            str.encode(self.header_name.lower()), None
        )
        if correlation_id_bytes:
            return correlation_id_bytes.decode("utf-8")
        else:
            return str(uuid.uuid4())

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            return await self.app(scope, receive, send)

        correlation_id: str = self._get_correlation_id(scope)

        with log_manager(correlation_id=correlation_id):
            await self.app(scope, receive, send)
