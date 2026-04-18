from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from core.redis_client import redis_client


RATE_LIMIT_PER_MIN = {"free": 60, "paid": 120}


class RateLimitMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("db_user") or {}
        tier = user.get("tier", "free")
        uid = user.get("id", 0)

        key = f"rl:{uid}:{int(__import__('time').time() // 60)}"
        count = await redis_client.incr(key)
        await redis_client.expire(key, 60)

        if count > RATE_LIMIT_PER_MIN.get(tier, 60):
            return None  # silently drop; or reply with rate-limit message
        return await handler(event, data)
