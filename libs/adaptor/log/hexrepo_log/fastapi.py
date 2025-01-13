
from typing import Dict
import uuid
from hexrepo_log.log import trim_exceptions
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
        with logger.contextualize(correlation_id=correlation_id):
            try:
                await self.app(scope, receive, send)
            except Exception as exc:
                trim_exceptions(exc)
