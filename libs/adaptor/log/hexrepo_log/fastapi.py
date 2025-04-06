import uuid
from typing import Dict
from loguru import logger
from starlette.types import Receive, Scope, Send

from hexrepo_log.log import log_manager


class LogMiddleware:
    def __init__(self, app, header_name: str = "X-Request-ID"):
        self.app = app
        self.header_name = header_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            return await self.app(scope, receive, send)
        headers: Dict = dict(scope["headers"])
        correlation_id_bytes: bytes = headers.get(str.encode(self.header_name.lower()), None) or str(uuid.uuid4())
        correlation_id: str = correlation_id_bytes.decode("utf-8")
        with log_manager(correlation_id=correlation_id):
            await self.app(scope, receive, send)
