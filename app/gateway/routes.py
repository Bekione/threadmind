from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.utils.logger import get_logger
from app.utils.rate_limit import rate_limiter
from app.db.base import get_db
from app.db import crud
from app.db.models import JobStatus
from app.queue.celery_app import celery
from .schemas import IngestRequest, IngestResponse, JobResult
from .validators import validate_ingest_payload


router = APIRouter()
logger = get_logger(__name__)


@router.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest, db: Session = Depends(get_db)):
    # Rate limit per user
    allowed, reason = rate_limiter.check(req.telegram_id)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=f"Rate limit exceeded: {reason}")

    channel_id, message_id = validate_ingest_payload(req.telegram_id, req.channel_id, req.message_id, req.url)

    user = crud.get_or_create_user(db, req.telegram_id)
    crud.increment_user_request_count(db, user)

    job = crud.create_job(db, user, channel_id, message_id)

    # Enqueue Celery task (use default queue consumed by workers)
    celery.send_task("process_thread", args=[job.id, channel_id, message_id])

    logger.info({"event": "ingest", "job_id": job.id, "user_id": user.id, "channel_id": channel_id, "message_id": message_id})
    return IngestResponse(job_id=job.id, status="queued")


@router.get("/result/{job_id}", response_model=JobResult)
def get_result(job_id: str, db: Session = Depends(get_db)):
    job = crud.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return JobResult(
        status=job.status.value,
        job_id=job.id,
        channel_id=job.channel_id,
        message_id=job.message_id,
        created_at=job.created_at,
        completed_at=job.completed_at,
        summary=job.summary,
        highlights=job.highlights,
        token_usage=job.token_usage,
        cost=float(job.cost) if job.cost is not None else None,
    )


@router.get("/healthz")
def health() -> dict:
    return {"status": "ok"}
