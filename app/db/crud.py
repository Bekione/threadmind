from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from .models import User, Job, JobStatus


def get_or_create_user(db: Session, telegram_id: int) -> User:
    user = db.query(User).filter(User.telegram_id == telegram_id).one_or_none()
    if user:
        user.last_seen_at = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    user = User(telegram_id=telegram_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def increment_user_request_count(db: Session, user: User) -> None:
    user.request_count += 1
    db.add(user)
    db.commit()


def create_job(db: Session, user: User, channel_id: str, message_id: int) -> Job:
    job = Job(user_id=user.id, channel_id=channel_id, message_id=message_id, status=JobStatus.pending)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def update_job_status(db: Session, job_id: str, status: JobStatus) -> Optional[Job]:
    job = db.query(Job).filter(Job.id == job_id).one_or_none()
    if not job:
        return None
    job.status = status
    if status in (JobStatus.done, JobStatus.failed):
        job.completed_at = datetime.utcnow()
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def set_job_result(
    db: Session,
    job_id: str,
    summary: str,
    highlights: dict,
    token_usage: int,
    cost: float,
    status: JobStatus = JobStatus.done,
) -> Optional[Job]:
    job = db.query(Job).filter(Job.id == job_id).one_or_none()
    if not job:
        return None
    job.summary = summary
    job.highlights = highlights
    job.token_usage = token_usage
    job.cost = cost
    job.status = status
    job.completed_at = datetime.utcnow()
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job_by_id(db: Session, job_id: str) -> Optional[Job]:
    return db.query(Job).filter(Job.id == job_id).one_or_none()
