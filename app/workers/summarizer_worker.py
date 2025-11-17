"""Entry point module for worker-specific bootstrapping if needed.

Celery workers are launched via: celery -A app.queue.celery_app.celery worker
This module ensures tasks are importable if directly executed.
"""

from app.queue.tasks import process_thread  # noqa: F401
