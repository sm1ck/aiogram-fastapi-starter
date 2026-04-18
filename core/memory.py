"""Minimal 3-layer memory (recent Redis + placeholder for vector / summary).

For production semantic memory, see the HoneyChat architecture overview:
https://github.com/sm1ck/honeychat
"""
import json
import time

from core.redis_client import redis_client


RECENT_TTL_SECONDS = 86400 * 7
MAX_RECENT = 20


class Memory:
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        self.recent_key = f"mem:recent:{user_id}"

    async def append(self, role: str, content: str) -> None:
        item = json.dumps({"role": role, "content": content, "ts": time.time()})
        await redis_client.zadd(self.recent_key, {item: time.time()})
        await redis_client.zremrangebyrank(self.recent_key, 0, -MAX_RECENT - 1)
        await redis_client.expire(self.recent_key, RECENT_TTL_SECONDS)

    async def recent(self) -> list[dict]:
        raw = await redis_client.zrange(self.recent_key, 0, -1)
        return [json.loads(r) for r in raw]

    async def build_context(self, user_message: str) -> list[dict]:
        """Build message array for LLM. Extend with ChromaDB semantic retrieval."""
        messages = await self.recent()
        messages.append({"role": "user", "content": user_message})
        return [{"role": m["role"], "content": m["content"]} for m in messages]
