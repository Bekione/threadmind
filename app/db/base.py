from __future__ import annotations
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

Base = declarative_base()

# Lazy initialization to avoid loading settings during migrations
_engine = None
_SessionLocal = None


def _get_engine():
    global _engine
    if _engine is None:
        from app.utils.config import settings
        _engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)
    return _engine


def _get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=_get_engine(), autocommit=False, autoflush=False, expire_on_commit=False, future=True)
    return _SessionLocal


# For backward compatibility, expose as module-level callables
engine = _get_engine
SessionLocal = _get_session_local


def get_db() -> Generator[Session, None, None]:
    db = _get_session_local()()
    try:
        yield db
    finally:
        db.close()
