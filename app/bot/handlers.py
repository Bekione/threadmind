from __future__ import annotations
import asyncio
from typing import Optional, Tuple
import httpx
from telegram import Update
from telegram.ext import ContextTypes

from app.utils.config import settings
from app.utils.logger import get_logger
from app.utils.telegram_parser import parse_telegram_url, extract_from_forwarded


logger = get_logger(__name__)
API_URL = settings.API_GATEWAY_URL.rstrip("/")


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🧠 <b>Welcome to ThreadMind!</b>\n\n"
        "I summarize Telegram channel discussion threads using AI.\n\n"
        "<b>How to use:</b>\n"
        "• Forward a channel post to me\n"
        "• Or send a t.me link (e.g., https://t.me/channel/12345)\n"
        "• I'll fetch the discussion and generate a summary with highlights\n\n"
        "<b>Commands:</b>\n"
        "/help — Show available commands\n"
        "/summarize — Start summarization\n\n"
        "Built with ❤️ by @Groots23",
        parse_mode="HTML"
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "<b>ThreadMind Help</b>\n\n"
        "<b>Available Commands:</b>\n\n"
        "<b>/start</b> — Show welcome message\n\n"
        "<b>/summarize</b> — Summarize a thread\n"
        "  Usage: /summarize https://t.me/channel/12345\n\n"
        "<b>Forward a post</b>\n"
        "  Simply forward any channel post to me and I'll summarize it\n\n"
        "<b>What I do:</b>\n"
        "✨ Fetch discussion comments from the thread\n"
        "📝 Generate AI-powered summaries\n"
        "⭐ Extract key highlights\n"
        "📊 Show token usage and cost\n\n"
        "<b>Tips:</b>\n"
        "• Works best with public channels\n"
        "• Processing takes 10-30 seconds\n"
        "• Results are cached for 24 hours\n\n"
        "Built with ❤️ by @Groots23",
        parse_mode="HTML"
    )


def _extract_ids_from_update(update: Update) -> Optional[Tuple[str, int]]:
    msg = update.message
    if not msg:
        return None
    # Check forwarded
    fwd = extract_from_forwarded(msg)
    if fwd:
        return fwd
    # Check if user provided URL in arguments or message text
    text = msg.text or msg.caption or ""
    parts = text.split()
    for p in parts:
        if p.startswith("http") and "t.me" in p:
            try:
                return parse_telegram_url(p)
            except Exception:
                continue
    return None


async def summarize_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        ids = _extract_ids_from_update(update)
        if not ids:
            await update.message.reply_text(
            "❌ <b>No valid input detected</b>\n\n"
            "Please either:\n"
            "• Forward a channel post to me, or\n"
            "• Send a t.me link (e.g., https://t.me/channel/12345)\n\n"
            "Type /help for more info.",
            parse_mode="HTML"
        )
            return
        channel_id, message_id = ids
        telegram_id = update.effective_user.id if update.effective_user else 0

        payload = {"telegram_id": telegram_id, "channel_id": channel_id, "message_id": message_id}
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(f"{API_URL}/ingest", json=payload)
            if r.status_code != 200:
                await update.message.reply_text(f"Error: {r.text}")
                return
            data = r.json()
            job_id = data.get("job_id")

        await update.message.reply_text(
            f"⏳ <b>Processing your request…</b>\n\n"
            f"Job ID: <code>{job_id}</code>\n\n"
            f"This usually takes 10-30 seconds. Please wait…",
            parse_mode="HTML"
        )

        # Poll for result
        timeout = settings.BOT_POLL_TIMEOUT_SECONDS
        interval = settings.BOT_POLL_INTERVAL_SECONDS
        elapsed = 0

        while elapsed < timeout:
            await asyncio.sleep(interval)
            elapsed += interval
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.get(f"{API_URL}/result/{job_id}")
                if r.status_code != 200:
                    continue
                data = r.json()
                status_ = data.get("status")
                if status_ == "done":
                    highlights = data.get("highlights", {})
                    formatted = highlights.get("formatted")
                    if formatted:
                        await update.message.reply_html(formatted, disable_web_page_preview=True)
                    else:
                        await update.message.reply_text(data.get("summary") or "No summary.")
                    return
                elif status_ == "failed":
                    await update.message.reply_text(
                        "❌ <b>Processing failed</b>\n\n"
                        "The thread could not be summarized. This might be because:\n"
                        "• The channel is private\n"
                        "• The post doesn't exist\n"
                        "• The discussion group is not accessible\n\n"
                        "Please try with a different post or contact @Groots23",
                        parse_mode="HTML"
                    )
                    return
        await update.message.reply_text(
            "⏱️ <b>Still processing…</b>\n\n"
            "The thread is taking longer than expected. This might be due to:\n"
            "• Large discussion thread\n"
            "• Slow API response\n\n"
            "Try resubmitting the request or contact @Groots23 for support.",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.exception({"event": "bot_error", "error": str(e)})
        await update.message.reply_text(
            "❌ <b>An error occurred</b>\n\n"
            "Something went wrong while processing your request.\n"
            "Please try again or contact @Groots23 for support.",
            parse_mode="HTML"
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception({"event": "handler_exception", "update": str(update), "error": str(context.error)})
