from __future__ import annotations
from typing import Any, Dict
from decimal import Decimal

from app.queue.celery_app import celery
from app.utils.logger import get_logger
from app.utils.telegram_parser import fetch_thread_messages
from app.ai_engine.pipeline_summarizer import PipelineSummarizer
from app.db.base import SessionLocal
from app.db.crud import update_job_status, set_job_result
from app.db.models import JobStatus


logger = get_logger(__name__)


@celery.task(name="process_thread")
def process_thread(job_id: str, channel_id: str, message_id: int) -> Dict[str, Any]:
    db = SessionLocal()()  # SessionLocal is now a function that returns the sessionmaker
    try:
        logger.info({"event": "task_start", "job_id": job_id, "channel_id": channel_id, "message_id": message_id})
        update_job_status(db, job_id, JobStatus.processing)

        messages = fetch_thread_messages(channel_id, message_id)
        pipeline = PipelineSummarizer()
        formatted, payload = pipeline.run(messages)

        # Simple token and cost estimation
        total_chars = sum(len(m.get("text", "")) for m in messages)
        token_usage = int(total_chars / 4)
        cost = float(Decimal(token_usage) * Decimal("0.000002"))  # mock cost

        set_job_result(
            db,
            job_id=job_id,
            summary=payload["summary"],
            highlights={"items": payload["highlights"], "formatted": formatted},
            token_usage=token_usage,
            cost=cost,
            status=JobStatus.done,
        )

        logger.info({"event": "task_done", "job_id": job_id, "token_usage": token_usage, "cost": cost})
        return {"status": "done", "job_id": job_id}
    except Exception as e:
        logger.exception({"event": "task_failed", "job_id": job_id, "error": str(e)})
        update_job_status(db, job_id, JobStatus.failed)
        return {"status": "failed", "job_id": job_id, "error": str(e)}
    finally:
        db.close()
