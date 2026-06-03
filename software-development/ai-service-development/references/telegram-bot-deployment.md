# Telegram Bot Deployment

**Modular project structure (adapted from donbarbos template, see Approach A in SKILL.md):**
```
telegram-bot-platform/
├── bot/
│   ├── core/
│   │   ├── config.py      # pydantic-settings + .env
│   │   └── loader.py      # Bot, Dispatcher, storage init
│   ├── handlers/
│   │   ├── __init__.py    # get_handlers_router() aggregator
│   │   ├── start.py       # /start
│   │   ├── services.py    # /services — catalog
│   │   ├── ask.py         # /ask + free text → AI
│   │   ├── help.py        # /help
│   │   └── admin.py       # Admin commands
│   ├── services/
│   │   ├── __init__.py
│   │   └── ai.py          # Gemini API (google-genai)
│   ├── middlewares/
│   │   └── __init__.py
│   ├── __init__.py
│   └── __main__.py        # Entry: python -m bot
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml (or requirements.txt)
└── .env
```

## Preferred: Docker + Gemini API (no OpenCode)

### Dockerfile (simple)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "-m", "bot"]
```

### docker-compose.yml (no volume mounts)
```yaml
services:
  bot:
    build: .
    container_name: ai-agent-bot
    restart: unless-stopped
    env_file: .env
```

### Gemini API integration (google-genai, NOT google-generativelanguage)
```python
from google import genai
from bot.core.config import settings

class AIService:
    def __init__(self) -> None:
        self.client = None
        if settings.GEMINI_API_KEY:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def ask(self, prompt: str) -> str | None:
        if not self.client:
            return "AI disabled — add GEMINI_API_KEY"
        response = await self.client.aio.models.generate_content(
            model=settings.GEMINI_MODEL or "gemini-2.0-flash",
            contents=prompt,
        )
        return response.text
```

Package: `pip install google-genai`
Async method: `client.aio.models.generate_content()` — note the `aio` sub-client.
Model: `gemini-2.0-flash` (default, fast, free tier available).

### Environment variables
```
BOT_TOKEN=<telegram bot token>
GEMINI_API_KEY=<Google AI Studio key>
GEMINI_MODEL=gemini-2.0-flash
DEBUG=False
ADMIN_IDS=<comma-separated Telegram IDs>
```

### Build & run
```bash
cd telegram-bot-platform
docker compose up -d --build
docker logs ai-agent-bot -f
docker compose down
```

## Legacy: OpenCode CLI bot (use only if Gemini unavailable)
See `references/opencode-cli-integration.md` for the old approach.
- Volume-mount `/root/.opencode/bin/opencode` in docker-compose
- Volume-mount `/root/.local/share/opencode` for SQLite persistence
- Requires `asyncio.to_thread()` wrapper for blocking subprocess calls
- Single-file bot (`aiogram_bot.py`) — NOT the user's preferred approach

### async subprocess.run in aiogram handlers
OpenCode CLI `run` is blocking (up to 120s). In aiogram's async event loop, wrap the call with `asyncio.to_thread()`:

```python
import asyncio

class AIProvider:
    async def ask(self, prompt: str) -> str | None:
        import asyncio
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                ["opencode", "run", "--model", "opencode/deepseek-v4-flash-free", prompt],
                capture_output=True, text=True, timeout=120,
                env={**os.environ, "OPENCODE_NO_TUI": "1"},
            )
            # ... then read from SQLite DB
        except subprocess.TimeoutExpired:
            ...
```

Without `asyncio.to_thread()`, the blocking subprocess call freezes the entire bot polling loop (no message processing until opencode finishes).

### Parse mode: ALWAYS use None for AI-generated content
AI models frequently return broken Markdown (unclosed `**`, unmatched `*`, stray `_`). With `parse_mode=ParseMode.MARKDOWN`, this causes TelegramBadRequest errors.

**Fix on Bot init:**
```python
from aiogram.client.default import DefaultBotProperties
bot = Bot(token=token, default=DefaultBotProperties(parse_mode=None))
```

If you need formatting, sanitise the AI output before sending. Sending AI output as plain text is the safest approach.

### Verifying the bot is running
```bash
# Check container status
docker ps --filter name=ai-agent-bot

# Check logs
docker logs ai-agent-bot

# Test API (use token from .env)
source .env && curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getMe"
# → {"ok":true,"result":{"username":"ai_agent_service_bot",...}}

# If getUpdates returns 409 → bot IS actively polling (good!)
source .env && curl -s -o /dev/null -w "%{http_code}" "https://api.telegram.org/bot${BOT_TOKEN}/getUpdates?timeout=1"
# → 409 (expected when bot is polling)
```

## Fallback: Raw process (no Docker)

### Startup
```bash
cd /path/to/telegram-ai-bot
export $(grep -v '^#' .env | xargs)
PATH="$PATH:/root/.opencode/bin" OPENCODE_NO_TUI=1 python3 aiogram_bot.py
```

Via Hermes terminal:
```python
terminal(background=True, command="cd /path && PATH=\"$PATH:/root/.opencode/bin\" OPENCODE_NO_TUI=1 python3 aiogram_bot.py")
```

### Token handling
- Hermes security scanner replaces `***` and `...` in tool outputs, mangling bot tokens.
- **Write token to `.env` file once** via Python or printf (disk copy stays clean).
- **Never pass token in command-line args** — read from file at runtime via `source .env` or `export $(grep -v '^#' .env | xargs)`.
- **Verify**: `source .env && echo ${#BOT_TOKEN}` should print 46 (Telegram bot token length).

### Kill all bot processes (non-Docker)
When debugging 409 conflicts, check for MULTIPLE scripts polling the same token:
```bash
ps aux | grep python3 | grep -E "aiogram_bot|ai_telegram_bot|start_bot|telegram" | grep -v grep
```
Kill all:
```bash
pkill -f "aiogram_bot\\|ai_telegram_bot\\|start_bot"
# or
kill -9 $(pgrep -f "aiogram_bot|ai_telegram_bot|start_bot") 2>/dev/null
```
Clear Telegram stale session:
```bash
source .env && curl -s "https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook?drop_pending_updates=true"
```

## 409 Conflict troubleshooting

### Normal 409 (bot is working)
When you call `getUpdates` manually while the bot is polling, Telegram returns 409. This is **expected** — it means the bot IS alive and connected.

### Problematic 409 (persistent errors in bot logs)
If the bot's own logs show 409 errors repeatedly, another process is polling the same token.

**Causes:**
1. Two+ different scripts (e.g. `start_bot.py` AND `aiogram_bot.py`) both polling
2. Old process not killed before starting new one
3. Docker container + host process running simultaneously

**Fix order:**
1. Kill ALL bot processes outside Docker
2. Kill Docker container: `docker compose down`
3. Clear Telegram session: `deleteWebhook?drop_pending_updates=true`
4. Verify clean: `getUpdates?timeout=0` → should return 200 with `[]`
5. Restart ONLY one instance (Docker or raw, not both)

## aiogram vs python-telegram-bot comparison

| Aspect | aiogram 3.x | python-telegram-bot (PTB) |
|--------|-------------|---------------------------|
| Async | Native (asyncio) | Wrapper (sync + async) |
| Handler style | Decorator `@dp.message()` | Class-based `add_handler()` |
| 409 handling | Silent recover | Logs ERROR traceback |
| Dependencies | Minimal (aiohttp) | Heavy (httpx, apscheduler) |
| Chat action | `ChatActionSender` context mgr | `reply_chat_action()` method |
| Parse mode | `DefaultBotProperties` on Bot init | `parse_mode` per-message or default |
| Template | `templates/ai-telegram-bot.py` (aiogram) | Archived |

When user preference is aiogram, ALWAYS use aiogram, never PTB.
