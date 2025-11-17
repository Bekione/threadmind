from __future__ import annotations
from celery import Celery

from app.utils.config import settings


celery = Celery(
    "threadmind",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.queue.tasks"],
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=settings.TZ,
    enable_utc=True,
)

