from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.utils.logger import setup_logging
from app.utils.config import settings
from .routes import router


setup_logging()

app = FastAPI(title="ThreadMind API", version="0.1.0")

# CORS permissive for MVP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root() -> dict:
    return {"name": "threadmind", "env": settings.ENV}
