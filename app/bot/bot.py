from __future__ import annotations
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram import BotCommand

from app.utils.config import settings
from app.utils.logger import setup_logging
from .handlers import start_handler, help_handler, summarize_handler, error_handler


async def post_init(app: Application) -> None:
    # You can set commands here if needed
    await app.bot.set_my_commands([
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show help"),
        BotCommand("summarize", "Summarize a Telegram post thread"),
    ])


def main() -> None:
    setup_logging()
    if not settings.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    application = (
        ApplicationBuilder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))

    # /summarize command or any message containing a link / forwarded post
    application.add_handler(CommandHandler("summarize", summarize_handler))
    link_filter = (filters.TEXT & filters.Regex(r"(https?://)?t\\.me/"))
    fwd_or_link = (filters.FORWARDED | link_filter) & ~filters.COMMAND
    application.add_handler(MessageHandler(fwd_or_link, summarize_handler))

    application.add_error_handler(error_handler)

    application.run_polling(drop_pending_updates=True, allowed_updates=None)


if __name__ == "__main__":
    main()
