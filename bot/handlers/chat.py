from aiogram import Router
from aiogram.types import Message

from core.llm import chat_completion
from core.memory import Memory

router = Router(name="chat")


@router.message()
async def handle_message(message: Message) -> None:
    user_id = message.from_user.id
    memory = Memory(user_id)

    history = await memory.build_context(message.text or "")
    reply = await chat_completion(history, user_tier="free")

    await memory.append(role="user", content=message.text or "")
    await memory.append(role="assistant", content=reply)

    await message.answer(reply)
