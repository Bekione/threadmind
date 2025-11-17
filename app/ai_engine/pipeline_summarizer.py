from __future__ import annotations
from typing import Any, Dict, List, Tuple

from app.utils.logger import get_logger
from . import AIEngine
from .formatter import format_for_telegram


logger = get_logger(__name__)


class PipelineSummarizer:
    def __init__(self) -> None:
        self.engine = AIEngine()

    def concatenate_messages(self, messages: List[Dict[str, Any]]) -> str:
        joined = []
        for m in messages:
            author = m.get("username") or str(m.get("user_id"))
            prefix = "[OWNER]" if m.get("is_owner") else "[MEMBER]"
            joined.append(f"{prefix} {author}: {m.get('text','')}")
        return "\n".join(joined)

    def cluster_messages(self, messages: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        # Simple size-based chunking for MVP
        chunk, chunks, n = [], [], 0
        for m in messages:
            chunk.append(m)
            n += 1
            if n % 5 == 0:
                chunks.append(chunk)
                chunk = []
        if chunk:
            chunks.append(chunk)
        return chunks

    def detect_roles(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Heuristic: first message is owner, others are members unless flagged
        for idx, m in enumerate(messages):
            m["is_owner"] = bool(m.get("is_owner") or idx == 0)
        return messages

    def run(self, messages: List[Dict[str, Any]]) -> Tuple[str, Dict[str, Any]]:
        msgs = self.detect_roles(messages)
        text = self.concatenate_messages(msgs)
        summary = self.engine.generate_summary(text)
        highlights = self.engine.extract_highlights(text)
        formatted = format_for_telegram(summary, highlights)
        return formatted, {"summary": summary, "highlights": highlights}
