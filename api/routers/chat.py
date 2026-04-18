from fastapi import APIRouter
from pydantic import BaseModel

from core.llm import chat_completion
from core.memory import Memory

router = APIRouter()


class ChatRequest(BaseModel):
    user_id: int
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/message", response_model=ChatResponse)
async def send_message(req: ChatRequest) -> ChatResponse:
    memory = Memory(req.user_id)
    context = await memory.build_context(req.message)
    reply = await chat_completion(context, user_tier="free")
    await memory.append(role="user", content=req.message)
    await memory.append(role="assistant", content=reply)
    return ChatResponse(reply=reply)
