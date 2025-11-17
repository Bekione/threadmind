from __future__ import annotations
from fastapi import HTTPException, status

from app.utils.telegram_parser import parse_telegram_url


def validate_ingest_payload(telegram_id: int, channel_id: str | None, message_id: int | None, url: str | None) -> tuple[str, int]:
    if url:
        try:
            c, m = parse_telegram_url(url)
            return c, m
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Telegram URL")
    if not channel_id or not message_id or message_id <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing channel_id or message_id")
    return channel_id, message_id
