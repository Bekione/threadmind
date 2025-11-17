from __future__ import annotations
from typing import List
from tenacity import retry, wait_exponential, stop_after_attempt

from app.utils.config import settings

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover
    genai = None  # type: ignore


class GeminiProvider:
    name = "gemini"

    @staticmethod
    def is_configured() -> bool:
        return bool(settings.GEMINI_API_KEY and genai is not None)

    def __init__(self) -> None:
        if not self.is_configured():
            raise RuntimeError("Gemini is not configured")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name)

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    def summarize(self, text: str) -> str:
        prompt = (
            "You are an expert at summarizing Telegram discussion threads. "
            "Summarize the following content into a concise, structured summary with 5-8 bullet points and a brief paragraph overview.\n\n"
            f"CONTENT:\n{text}\n\n"
        )
        resp = self.model.generate_content(prompt)
        return (resp.text or "").strip()

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    def highlights(self, text: str) -> List[str]:
        prompt = (
            "Extract 5-10 key actionable highlights from the following Telegram thread content. "
            "Return as a bullet list, each item concise.\n\n"
            f"CONTENT:\n{text}\n\n"
        )
        resp = self.model.generate_content(prompt)
        content = resp.text or ""
        lines = [l.strip("- ") for l in content.splitlines() if l.strip()]
        return [l for l in lines if l]
