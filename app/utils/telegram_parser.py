from __future__ import annotations
import re
import asyncio
from typing import Any, Dict, List, Optional, Tuple, Union

from app.utils.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

URL_RE = re.compile(r"https?://t\.me/(?P<c>c/)?(?P<channel>[A-Za-z0-9_\-]+)/(?P<message>\d+)")


def parse_telegram_url(url: str) -> Tuple[str, int]:
    match = URL_RE.search(url.strip())
    if not match:
        raise ValueError("Unsupported Telegram URL format")
    channel = match.group("channel")
    message_id = int(match.group("message"))
    # Normalize t.me/c/<internal>/<msg_id> to -100<internal>
    if match.group("c") and channel.isdigit():
        channel = f"-100{channel}"
    return channel, message_id


def extract_from_forwarded(ptb_message: Any) -> Optional[Tuple[str, int]]:
    """Extract channel_id and message_id from a forwarded message.
    
    Handles multiple PTB message attribute patterns for forwarded posts.
    """
    try:
        # Pattern 1: forward_from_chat + forward_from_message_id (standard)
        fwd_chat = getattr(ptb_message, "forward_from_chat", None)
        fwd_msg_id = getattr(ptb_message, "forward_from_message_id", None)
        if fwd_chat and fwd_msg_id:
            channel_id = getattr(fwd_chat, "username", None) or str(getattr(fwd_chat, "id"))
            return str(channel_id), int(fwd_msg_id)
        
        # Pattern 2: forward_origin (Telegram Bot API 6.5+)
        fwd_origin = getattr(ptb_message, "forward_origin", None)
        if fwd_origin:
            # ForwardOriginChannel
            if hasattr(fwd_origin, "chat") and hasattr(fwd_origin, "message_id"):
                chat = fwd_origin.chat
                channel_id = getattr(chat, "username", None) or str(getattr(chat, "id"))
                return str(channel_id), int(fwd_origin.message_id)
        
        # Pattern 3: reply_to_message with forward info
        reply_msg = getattr(ptb_message, "reply_to_message", None)
        if reply_msg:
            fwd_chat = getattr(reply_msg, "forward_from_chat", None)
            fwd_msg_id = getattr(reply_msg, "forward_from_message_id", None)
            if fwd_chat and fwd_msg_id:
                channel_id = getattr(fwd_chat, "username", None) or str(getattr(fwd_chat, "id"))
                return str(channel_id), int(fwd_msg_id)
    except Exception as e:
        logger.debug({"event": "extract_forwarded_error", "error": str(e)})
    
    return None


def _telethon_available() -> bool:
    try:
        import telethon  # noqa: F401
        return bool(settings.TELEGRAM_API_ID and settings.TELEGRAM_API_HASH and settings.TELEGRAM_SESSION)
    except Exception:
        return False


async def _fetch_thread_messages_async(channel_id: str, message_id: int) -> List[Dict[str, Any]]:
    from telethon import TelegramClient
    from telethon.sessions import StringSession
    from telethon.tl.functions.channels import GetFullChannelRequest
    from telethon.errors import RPCError

    # Prepare client per call (simpler and safe in Celery workers)
    client = TelegramClient(StringSession(settings.TELEGRAM_SESSION), settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)
    await client.connect()
    messages: List[Dict[str, Any]] = []
    try:
        # Resolve channel entity (username or id)
        entity_input: Union[str, int] = int(channel_id) if channel_id.lstrip("-+").isdigit() else channel_id
        channel = await client.get_entity(entity_input)

        # Fetch root post
        post = await client.get_messages(channel, ids=message_id)
        if post and (post.message or getattr(post, "raw_text", None)):
            text = post.message or getattr(post, "raw_text", "") or ""
            uname = getattr(post, "post_author", None) or getattr(channel, "username", None) or getattr(channel, "title", None)
            messages.append(
                {
                    "id": int(post.id),
                    "user_id": int(getattr(getattr(post, "from_id", None), "user_id", 0) or 0),
                    "username": str(uname) if uname else None,
                    "is_owner": True,
                    "text": text,
                }
            )

        # Find linked discussion group and iterate comments
        try:
            full = await client(GetFullChannelRequest(channel))
            linked_id = getattr(full.full_chat, "linked_chat_id", None)
        except RPCError:
            linked_id = None

        if linked_id:
            linked = await client.get_entity(linked_id)
            # Fetch replies to the root post in the linked group
            async for msg in client.iter_messages(
                linked,
                reply_to=message_id,
                limit=settings.TELEGRAM_FETCH_LIMIT,
                reverse=True,
            ):
                if not (msg and (msg.message or getattr(msg, "raw_text", None))):
                    continue
                # Try to resolve sender username lazily
                uname = None
                try:
                    sender = await msg.get_sender()
                    uname = getattr(sender, "username", None) or getattr(sender, "first_name", None)
                except Exception:
                    pass
                messages.append(
                    {
                        "id": int(msg.id),
                        "user_id": int(getattr(msg, "sender_id", 0) or 0),
                        "username": uname,
                        "is_owner": False,
                        "text": msg.message or getattr(msg, "raw_text", "") or "",
                    }
                )

        return messages
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass


def fetch_thread_messages(channel_id: str, message_id: int) -> List[Dict[str, Any]]:
    """Fetch real discussion thread messages.

    - Uses Telethon with a service user session (not the bot) to read channel posts and their discussion comments.
    - Works for public channels with public discussion groups. For private content, the service account must have access.
    - If Telethon is not configured, falls back to a minimal single-message thread based on the root post context.
    """
    if _telethon_available():
        try:
            return asyncio.run(_fetch_thread_messages_async(channel_id, message_id))
        except Exception as e:
            logger.exception({"event": "telethon_fetch_failed", "channel_id": channel_id, "message_id": message_id, "error": str(e)})
            if settings.TELEGRAM_REQUIRE_REAL_FETCH:
                raise
    else:
        if settings.TELEGRAM_REQUIRE_REAL_FETCH:
            raise RuntimeError("Telethon not configured (TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION)")

    # Fallback: minimal mock from provided identifiers (kept to avoid hard failures)
    logger.warning({"event": "fallback_mock_thread", "channel_id": channel_id, "message_id": message_id})
    base_text = (
        f"Thread for channel {channel_id}, message {message_id}. "
        "Real Telegram fetching is not configured; returning a minimal placeholder."
    )
    return [
        {
            "id": int(message_id),
            "user_id": 0,
            "username": str(channel_id),
            "is_owner": True,
            "text": base_text,
        }
    ]
