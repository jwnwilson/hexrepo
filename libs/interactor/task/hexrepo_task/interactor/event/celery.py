
from typing import Any
from celery import Celery
from pydantic import BaseModel

from hexrepo_task.interactor.event.celery_pydantic import pydantic_celery


class CeleryConfig(BaseModel):
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    REGION: str


def create_celery_app(celery_config: CeleryConfig, celery_kwargs: dict[str, Any] | None = None, broker_transport_options: dict[str, Any] | None = None) -> Celery:
    celery_kwargs = celery_kwargs or {}
    broker_transport_options = broker_transport_options or {}
    celery_app = Celery(
        "tasks",
        broker=celery_config.CELERY_BROKER_URL,
        backend=celery_config.CELERY_RESULT_BACKEND,
        **celery_kwargs
    )
    pydantic_celery(celery_app)
    celery_app.conf.broker_transport_options = {"region": celery_config.REGION} | broker_transport_options
    return celery_app