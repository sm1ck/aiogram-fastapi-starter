"""OpenRouter wrapper with tier-based model selection and retries."""
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings


TIER_MODELS = {
    "free": "qwen/qwen3-235b-a22b:free",
    "paid": "google/gemini-2.5-flash-lite",
}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def chat_completion(messages: list[dict], user_tier: str = "free") -> str:
    model = TIER_MODELS.get(user_tier, TIER_MODELS["free"])

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "HTTP-Referer": "https://github.com/sm1ck/aiogram-fastapi-starter",
                "X-Title": "aiogram-fastapi-starter",
            },
            json={
                "model": model,
                "messages": messages,
                "max_tokens": 512,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
