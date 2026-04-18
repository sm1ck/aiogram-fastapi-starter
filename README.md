# aiogram + FastAPI Starter

> Production-grade starter for building a Telegram AI bot with a shared FastAPI backend. Includes aiogram (async Telegram bot), FastAPI (REST API), Redis (FSM + caching), ChromaDB (vector memory), OpenRouter (multi-LLM routing), and docker-compose wiring. Patterns extracted from [HoneyChat](https://honeychat.bot) ([@HoneyChatAIBot](https://t.me/HoneyChatAIBot)).

## Why this starter

Most Telegram bot tutorials stop at "echo bot in 20 lines." Production AI bots need:

- **Async everything** — Telegram polling, DB queries, HTTP calls to LLM/TTS/image APIs
- **FSM storage in Redis** (not in-memory) so restarts don't lose state
- **Shared backend** with a web app (REST API for mobile / web / future Mini App)
- **LLM routing** — different models for different user tiers, retry on 429/500
- **Vector memory** — recalling relevant past conversations semantically
- **Rate limiting** — per-user, tier-aware
- **Cost guards** — daily spend budgets, fail-closed

This starter skips 5–7 days of boilerplate and gives you the production skeleton used by [HoneyChat](https://github.com/sm1ck/honeychat) (Telegram AI companion with 10K+ active users).

## Stack

- **aiogram** — async Telegram Bot API framework
- **FastAPI** — REST backend, shared between bot and web clients
- **SQLAlchemy async** (+ asyncpg driver) — PostgreSQL ORM
- **Redis** — FSM storage, rate-limit counters, Celery broker
- **ChromaDB** — vector memory for semantic recall
- **Celery** — background jobs (summarization, image gen, notifications)
- **OpenRouter** — single API for 100+ LLMs (Qwen, Gemini, Claude, etc.)
- **tenacity** — retries with exponential backoff on external APIs
- **loguru** — structured logging

## Directory structure

```
.
├── bot/                   # aiogram Telegram bot
│   ├── main.py            # dispatcher setup, middleware chain
│   ├── handlers/          # message and callback handlers
│   └── middleware/        # auth, rate limit, plan injection
├── api/                   # FastAPI REST backend
│   ├── main.py            # app factory, CORS, lifespan
│   ├── routers/           # /auth, /user, /chat, /gen
│   └── deps.py            # dependency-injected JWT auth
├── core/                  # shared business logic
│   ├── llm.py             # OpenRouter wrapper with retries
│   ├── memory.py          # Redis + ChromaDB memory
│   └── cost_tracker.py    # Redis-backed daily spend counters
├── db/
│   ├── models.py          # SQLAlchemy ORM
│   └── database.py        # async engine + session factory
├── workers/
│   └── tasks.py           # Celery app + periodic schedule
├── config/
│   └── settings.py        # pydantic BaseSettings, loads from .env
├── docker-compose.yml     # bot + api + postgres + redis + chromadb + celery
├── .env.example
└── requirements.txt
```

## Quick start

```bash
git clone https://github.com/sm1ck/aiogram-fastapi-starter.git my-bot
cd my-bot
cp .env.example .env
# Fill in: BOT_TOKEN, OPENROUTER_API_KEY, POSTGRES_PASSWORD
docker compose up -d
```

First message to your bot should echo back through the full stack:
Telegram → aiogram → middleware chain → handler → LLM via OpenRouter → response.

## Included patterns

### 1. Middleware chain

```
Auth → Rate Limit → Plan Inject → Cost Guard → Handler
```

- **Auth** resolves or creates the user by Telegram ID
- **Rate Limit** checks per-user Redis counter with sliding window
- **Plan Inject** attaches the user's current subscription tier to context
- **Cost Guard** blocks new messages if the daily cost hard-stop is reached

### 2. LLM routing with fallback

```python
async def chat(user, messages):
    model = pick_model_for_tier(user.tier)
    try:
        return await openrouter_chat(model, messages)
    except RateLimitError:
        return await openrouter_chat(fallback_model, messages)
```

Paired with `tenacity` for per-request retries. See [core/llm.py](core/llm.py).

### 3. 3-layer memory

| Layer | Storage | Retrieval |
|---|---|---|
| Recent | Redis sorted set | Last 20 by timestamp |
| Semantic | ChromaDB | Top-K embeddings by similarity |
| Summary | PostgreSQL | Static roll-up when context overflows |

See [core/memory.py](core/memory.py).

### 4. Shared auth (Telegram + web)

JWT issued on Telegram auth (via bot command or Login Widget) works the same as email/OAuth JWTs from the FastAPI side. Single users table, multiple providers. The HoneyChat multi-auth case study in [sm1ck/snapshotvoter](https://github.com/sm1ck/snapshotvoter/blob/main/docs/case-studies/honeychat-multi-auth.md) has the full pattern.

### 5. Cost tracking

Redis counter per day + per user:

```python
await redis.pipeline()\
    .incrbyfloat(f"costs:daily:{today}", amount)\
    .incrbyfloat(f"costs:user:{uid}:{today}", amount)\
    .expire(f"costs:user:{uid}:{today}", 86400 * 7)\
    .execute()
```

Sub-millisecond, atomic, fail-closed if Redis is down (returns `inf` → blocks generation).

## What's NOT included

By design, this starter is a skeleton. You will need to add:

- **Payments** (Telegram Stars / CryptoBot / Paddle / Stripe) — see the TON payments case study in [sm1ck/layerzero-aptos](https://github.com/sm1ck/layerzero-aptos/blob/main/docs/case-studies/honeychat-ton-payments.md)
- **Web frontend** (Next.js / Astro) if you want a companion web app
- **Image/Video generation** (fal.ai, ComfyUI, Kling)
- **TTS** (Inworld, ElevenLabs, gTTS)
- **Your actual business logic**

## Used in production

- [HoneyChat](https://honeychat.bot) — Telegram AI companion ([@HoneyChatAIBot](https://t.me/HoneyChatAIBot)). Uses the exact middleware chain, memory layers, and LLM routing from this starter.

*If you ship something using this starter, open a PR to add it here.*

## Related

- [aiogram docs](https://docs.aiogram.dev)
- [FastAPI docs](https://fastapi.tiangolo.com)
- [OpenRouter models](https://openrouter.ai/models)
- [awesome-telegram-ai-bots](https://github.com/sm1ck/awesome-telegram-ai-bots) — broader list of tools

## License

MIT. Do what you want.

---

**Maintainer**: [@sm1ck](https://github.com/sm1ck) · [t.me/haruto_j](https://t.me/haruto_j)
