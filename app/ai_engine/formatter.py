from __future__ import annotations
import re
from typing import Any, Dict, List


def _markdown_to_html(text: str) -> str:
    """Convert markdown formatting to HTML for Telegram."""
    # Convert ### headers to <b>
    text = re.sub(r"^### (.+)$", r"<b>\1</b>", text, flags=re.MULTILINE)
    # Convert ## headers to <b>
    text = re.sub(r"^## (.+)$", r"<b>\1</b>", text, flags=re.MULTILINE)
    # Convert # headers to <b>
    text = re.sub(r"^# (.+)$", r"<b>\1</b>", text, flags=re.MULTILINE)
    # Convert **bold** to <b>bold</b>
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Convert *italic* to <i>italic</i>
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    # Convert `code` to <code>code</code>
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    # Convert - bullet points (keep as is, just ensure newlines)
    return text


def format_output(summary: str, highlights: List[str]) -> Dict[str, Any]:
    return {
        "summary": summary,
        "highlights": highlights,
    }


def format_for_telegram(summary: str, highlights: List[str]) -> str:
    """Format summary and highlights for Telegram with HTML markup."""
    # Convert markdown summary to HTML
    html_summary = _markdown_to_html(summary)
    
    lines = [
        "✨ <b>Thread Summary</b>",
        "",
        html_summary,
        "",
        "<b>Highlights</b>",
    ]
    for h in highlights:
        lines.append(f"• {h}")
    return "\n".join(lines)
