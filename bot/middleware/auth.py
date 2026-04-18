from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User


class AuthMiddleware(BaseMiddleware):
    """Resolves or creates the user by Telegram ID.

    In production, call your DB here and attach the user row to `data["user"]`.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        # TODO: replace with actual DB upsert
        data["db_user"] = {"id": user.id, "tier": "free"}
        return await handler(event, data)
