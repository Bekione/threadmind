from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    telegram_id: int = Field(..., description="Telegram user id")
    channel_id: str = Field(..., description="Channel id or username")
    message_id: int = Field(..., ge=1, description="Message id in channel")
    url: Optional[str] = Field(None, description="Optional Telegram message URL")


class IngestResponse(BaseModel):
    job_id: str
    status: str = "queued"


class JobResult(BaseModel):
    status: str
    job_id: str
    channel_id: str
    message_id: int
    created_at: datetime
    completed_at: Optional[datetime]
    summary: Optional[str]
    highlights: Optional[Dict[str, Any]]
    token_usage: int
    cost: Optional[float]


class ErrorResponse(BaseModel):
    detail: str
