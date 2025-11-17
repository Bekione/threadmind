from __future__ import annotations
import time
from typing import Tuple
import redis

from .config import settings
from .logger import get_logger


logger = get_logger(__name__)


class RateLimiter:
    """Simple Redis token bucket per user for minute and hour windows."""

    def __init__(self, redis_url: str | None = None) -> None:
        self.redis = redis.from_url(redis_url or settings.REDIS_URL, decode_responses=True)
        self.per_minute = settings.RATE_LIMIT_PER_MINUTE
        self.per_hour = settings.RATE_LIMIT_PER_HOUR

    def _key(self, user_id: int, window: str) -> str:
        return f"ratelimit:{user_id}:{window}"

    def check(self, user_id: int) -> Tuple[bool, str]:
        now = int(time.time())
        minute_key = self._key(user_id, "m")
        hour_key = self._key(user_id, "h")

        pipe = self.redis.pipeline()
        # minute bucket
        pipe.incr(minute_key, 1)
        pipe.expire(minute_key, 60)
        # hour bucket
        pipe.incr(hour_key, 1)
        pipe.expire(hour_key, 3600)
        m_count, _, h_count, _ = pipe.execute()

        if int(m_count) > self.per_minute:
            return False, "per-minute limit exceeded"
        if int(h_count) > self.per_hour:
            return False, "per-hour limit exceeded"
        return True, "ok"


rate_limiter = RateLimiter()
