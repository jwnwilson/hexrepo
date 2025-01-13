
from typing import Dict
import uuid
from hexrepo_log.log import log_manager
from loguru import logger
from starlette.types import Receive, Scope, Send


class LogMiddleware:
    def __init__(self, app, header_name: str = "X-Request-ID"):
        self.app = app
        self.header_name = header_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            return await self.app(scope, receive, send)
        headers: Dict = dict(scope["headers"])
        correlation_id: str = headers.get(self.header_name, None) or str(uuid.uuid4())
        with log_manager(correlation_id=correlation_id) as logger:
            await self.app(scope, receive, send)
