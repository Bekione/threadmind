from __future__ import annotations
import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    DateTime,
    Enum,
    ForeignKey,
    Text,
    JSON,
    Numeric,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base


class JobStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    failed = "failed"
    done = "done"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    request_count: Mapped[int] = mapped_column(Integer, default=0)

    jobs = relationship("Job", back_populates="user")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    channel_id: Mapped[str] = mapped_column(String(255), nullable=False)
    message_id: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.pending, nullable=False)

    summary: Mapped[Optional[str]] = mapped_column(Text)
    highlights: Mapped[Optional[dict]] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    token_usage: Mapped[int] = mapped_column(Integer, default=0)
    cost: Mapped[Optional[float]] = mapped_column(Numeric(10, 4))

    user = relationship("User", back_populates="jobs")
