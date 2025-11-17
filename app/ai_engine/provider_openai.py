from __future__ import annotations
from typing import List
from tenacity import retry, wait_exponential, stop_after_attempt

from app.utils.config import settings

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency at runtime
    OpenAI = None  # type: ignore


class OpenAIProvider:
    name = "openai"

    @staticmethod
    def is_configured() -> bool:
        return bool(settings.OPENAI_API_KEY and OpenAI is not None)

    def __init__(self) -> None:
        if not self.is_configured():
            raise RuntimeError("OpenAI is not configured")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    def summarize(self, text: str) -> str:
        prompt = (
            "You are an expert at summarizing Telegram discussion threads. "
            "Summarize the following content into a concise, structured summary with 5-8 bullet points and a brief paragraph overview.\n\n"
            f"CONTENT:\n{text}\n\n"
        )
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=400,
        )
        return resp.choices[0].message.content.strip()  # type: ignore

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    def highlights(self, text: str) -> List[str]:
        prompt = (
            "Extract 5-10 key actionable highlights from the following Telegram thread content. "
            "Return as a bullet list, each item concise.\n\n"
            f"CONTENT:\n{text}\n\n"
        )
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300,
        )
        content = resp.choices[0].message.content or ""
        lines = [l.strip("- ") for l in content.splitlines() if l.strip()]
        return [l for l in lines if l]
