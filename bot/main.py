"""Telegram bot entry point.

Run: python -m bot.main
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from config.settings import settings
from bot.handlers import router as handlers_router
from bot.middleware.auth import AuthMiddleware
from bot.middleware.rate_limit import RateLimitMiddleware

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    storage = RedisStorage.from_url(settings.redis_url)
    bot = Bot(token=settings.bot_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=storage)

    dp.message.middleware(AuthMiddleware())
    dp.message.middleware(RateLimitMiddleware())
    dp.include_router(handlers_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
