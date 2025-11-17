from __future__ import annotations
from typing import List, Dict, Any

from app.utils.logger import get_logger
from app.utils.config import settings

from .provider_openai import OpenAIProvider
from .provider_gemini import GeminiProvider
from .highlight_detector import extract_highlights_local
from .formatter import format_output


logger = get_logger(__name__)


class AIEngine:
    """Unified interface with provider fallback."""

    def __init__(self) -> None:
        self.providers = []
        # Order matters: OpenAI -> Gemini
        if OpenAIProvider.is_configured():
            self.providers.append(OpenAIProvider())
        if GeminiProvider.is_configured():
            self.providers.append(GeminiProvider())

    def generate_summary(self, text: str) -> str:
        last_err: Exception | None = None
        for p in self.providers:
            try:
                return p.summarize(text)
            except Exception as e:
                last_err = e
                logger.warning({"event": "provider_failed", "provider": p.name, "error": str(e)})
        # Fallback: simple local summarization (first N sentences)
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        short = ". ".join(sentences[:5])
        return short if short else text[:500]

    def extract_highlights(self, text: str) -> List[str]:
        for p in self.providers:
            try:
                return p.highlights(text)
            except Exception as e:
                logger.warning({"event": "provider_highlights_failed", "provider": p.name, "error": str(e)})
        return extract_highlights_local(text)

    def format_output(self, summary: str, highlights: List[str]) -> Dict[str, Any]:
        return format_output(summary, highlights)
