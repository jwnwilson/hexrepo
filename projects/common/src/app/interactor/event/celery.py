from celery import Celery
from hexrepo_task.interactor.event.celery import create_celery_app, CeleryConfig

from app.config import config

celery_config = CeleryConfig(
    CELERY_BROKER_URL=config.CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND=config.CELERY_RESULT_BACKEND,
    REGION=config.REGION,
)
celery_app: Celery = create_celery_app(celery_config)
