from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="start")


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    await message.answer(
        "👋 Hi! I'm a starter Telegram AI bot.\n\n"
        "Send me any message and I'll reply via the configured LLM."
    )
