from aiogram import Router

from bot.handlers.chat import router as chat_router
from bot.handlers.start import router as start_router

router = Router(name="handlers")
router.include_router(start_router)
router.include_router(chat_router)
