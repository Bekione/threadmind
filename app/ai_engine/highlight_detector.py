from __future__ import annotations
from typing import List
import re


IMPORTANT_RE = re.compile(r"\b(important|update|fix|issue|resolved|note|urgent|warning)\b", re.I)


def score_sentence(sent: str) -> int:
    score = 0
    score += 2 if IMPORTANT_RE.search(sent) else 0
    score += 1 if len(sent) > 60 else 0
    score += min(3, len(set(re.findall(r"[A-Za-z]{5,}", sent))))
    return score


def extract_highlights_local(text: str, k: int = 7) -> List[str]:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    ranked = sorted(sentences, key=score_sentence, reverse=True)
    return ranked[:k]
