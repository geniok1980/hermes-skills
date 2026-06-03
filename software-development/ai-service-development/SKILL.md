---
name: ai-service-development
description: Build, package, and sell AI agent services — Telegram bots, VK parsers, Freqtrade trading strategies. Full lifecycle from demand research to deployment and monetisation on Russian and international platforms.
---

# AI Service Development

Build sellable AI agent services. Covers the full lifecycle: demand research → build → package → deploy → sell.

## Platforms & Demand Research

### Russian platforms
| Platform | What to sell | How to monitor |
|----------|-------------|----------------|
| **zismo.biz** (forum/110, forum/16) | Telegram bots, parsers, SMM automation, scripts | Scan forum/110 (Вакансии) + forum/16 (Услуги) daily |
| **fl.ru** (category AI, Автоматизация бизнеса) | Trading strategies, AI agents, bots | Browse projects by category, search "бот", "автоматизация" |
| **kwork.ru** | Telegram bots, parsers, scripts | Browse "Разработка и IT → Скрипты, боты" |

### International platforms
| Platform | Where to look | Notes |
|----------|--------------|-------|
| **Reddit** | r/forhire, r/AI_Agents, r/sidehustle, r/freelance, r/beermoney, r/slavelabour | Sort by new. Blocked by anti-scraping — use browser or old.reddit.com |
| **YouTube** | Search "make money with AI agents 2026", "build AI agent for clients" | Use browser for search; filter by "Recently uploaded" |
| **Google Trends** | Compare "AI agents", "AI automation", "AI freelance" | Monitor rising queries. Rate-limited — use browser |
| **GitHub** | Topic:freqtrade, search for strategy repos | 51K stars on Freqtrade, 65+ strategy repos. README → referral to paid service |

### Daily research cron job pattern
```
cronjob(action='create',
    name='daily-ai-agent-earning-research',
    schedule='0 10 * * *',
    enabled_toolsets=['web', 'terminal'],
    model={'provider': 'opencode-go', 'model': 'deepseek-v4-flash'},
    prompt='''Проведи ежедневный ресерч...''')
```
Include Russian (zismo, fl.ru) + international (Reddit, YouTube, Trends) sources.
**CRITICAL: Always pin `model` with the exact provider+model from the current session.** Omitting it can cause "No LLM provider configured" at cron runtime because the cron runner resolves the provider independently. Pin at creation or update.

## Service Products

### Tier 1: Telegram Bots ($100-500)  *Быстрый вход, много заказов*
### Tier 2: Custom AI Agents ($500-3000)  *Маржа выше, конкурентов мало*
### Tier 3: Freqtrade Strategies ($200-2000)  *Готовый спрос, recurring*

### Monetisation models per tier
| Model | Tier | Description |
|-------|------|-------------|
| One-time build | 1, 2, 3 | Client pays once for the finished product |
| Retainer | 2, 3 | Monthly support: maintenance, updates, optimisation |
| Subscription | 3 | Signal subscription (Telegram bot sends trades) — $50-100/mo |
| Package | 3 | Bundle of 5-10 strategies with backtest reports — $200-500 |

### Product naming for sales posts
On Zismo.biz / FL.ru, frame services as solutions to specific problems, not as tech:
- "Нужен бот для сбора заявок с AI-ответами?" → Tier 1
- "Хотите автоматизировать SMM?" → Tier 2
- "Ищете рабочую стратегию для Freqtrade?" → Tier 3

See `references/product-line-business-plan.md` for the complete business plan (product tiers, pricing, sales channels, action plan).

### Tier 1 details: Telegram Bots ($100-500)

#### Step 0: GitHub research first (HARD RULE)
When a client requests a bot, **first search GitHub** for the best matching template. Do NOT start coding from scratch. User explicitly confirmed this workflow. See:
- `references/github-telegram-bot-templates.md` — full repo analysis
- `references/client-template-mapping.md` — which template for which client type
- `/root/ai-agent-services/bot-templates/` — pre-cloned templates

#### Approach A (MANDATORY): Clone + adapt a modular GitHub template

**⚠️ HARD RULE: NEVER write Telegram bots from scratch.** The user explicitly rejected single-file bots (like the old `templates/ai-telegram-bot.py`). Always clone a well-structured aiogram 3.x template from GitHub and adapt it. If you catch yourself writing `from aiogram import Bot, Dispatcher` in a blank file, stop — go clone a template first. This rule exists because the user fired the previous agent for producing single-file garbage.

Clone a well-structured aiogram 3.x template from GitHub and adapt it.

**Best templates (2026, ordered by preference):**

**For AI agent bot (our use case):**
| Repo | Stars | Why use |
|------|-------|---------|
| `Er1one/telegram-bot-template` | 8 | **PREFERRED** — cleanest modular structure (core/handlers/services/keyboards/middlewares/filters), easy to strip PostgreSQL/Redis/i18n |
| `donbarbos/telegram-bot-template` | 464 | Solid but heavy (Flask+Prometheus+Grafana) |
| `MassonNN/masson-aiogram-template` | 126 | Clean structure, built-in templates |

**For client service businesses (пирсинг, салоны, барбершопы):**
| Repo | Stars | Why use |
|------|-------|---------|
| `T4rk123/ManicureSalon-TelegramBot` | 1 | **BEST for service booking** — aiogram 3.x + SQLite + APScheduler. Booking with calendar, portfolio, reviews, pricing, location, waitlist, admin panel. Easy to rebrand for any service business. |
| `6atyrlan/logovo-barbershop-bot` | 0 | Minimal barbershop booking. Single-file, hardcoded data. Only useful as reference for booking flow. |

**For client goods/digital shops (накрутки, цифровые товары):**
| Repo | Stars | Why use |
|------|-------|---------|
| `DaniilDonskoy/Shop-bot` | 498 | **BEST for shop** — aiogram 2.x + SQLite. Catalog with categories, cart, wallet, delivery status, admin panel. Docker support. |
| `ilyarolf/AiogramShopBot` | 192 | **BEST for crypto shop** — aiogram 3.x + PostgreSQL + Redis + FastAPI. Crypto payments, referral system, full admin panel, SQLAdmin, i18n, Docker Compose. |

**IMPORTANT: ALWAYS research GitHub before starting a new bot.** User explicitly confirmed: first search GitHub for the best repo matching the client type, clone and adapt. The `/root/ai-agent-services/bot-templates/` directory contains pre-cloned templates ready for adaptation.

**Er1one stripping workflow (for AI agent bot):**
```bash
git clone https://github.com/Er1one/telegram-bot-platform.git
cd telegram-bot-platform
rm -rf bot/managers/redis_manager.py bot/managers/i18n_manager.py bot/routes/ bot/models/ bot/utils/ bot/locales/ bot/handlers/groups/ bot/handlers/private/settings.py bot/handlers/private/blocking.py bot/services/broadcast_service.py bot/middlewares/i18n_middleware.py bot/filters/admin.py bot/filters/chat_type.py bot/filters/content.py docker-compose.dev.yml docker-compose.prod.yml .env.example .coverage pytest.ini tests/ Makefile CLAUDE.md
```
Then rewrite: pyproject.toml (remove all db/web deps), core/config.py (pydantic-settings only), core/loader.py (MemoryStorage), main.py (polling), managers/database_manager.py (aiosqlite), services/ai.py (OpenCode), handlers/ (no i18n).

**For an AI agent bot, after cloning:**
1. Strip down to essentials: remove admin panel, monitoring, analytics
2. Replace database with SQLite (aiosqlite) or remove DB entirely for simple bots
3. Add AI service module (`bot/services/ai.py`)
4. Create handlers: start, services, ask, help, admin

**Modular project structure (adapted from Er1one template):**
```
telegram-bot-platform/
├── bot/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py       # pydantic-settings
│   │   ├── loader.py       # Bot + Dispatcher (MemoryStorage)
│   │   └── logging.py      # loguru
│   ├── filters/
│   │   └── __init__.py     # IsPrivateChat, IsAdmin
│   ├── handlers/
│   │   ├── __init__.py     # router aggregator
│   │   ├── errors_router.py
│   │   └── private/
│   │       ├── __init__.py
│   │       ├── start.py
│   │       ├── commands.py # /menu, /help, /ask, /admin
│   │       ├── menu.py     # callback handlers
│   │       └── free_text.py # catch-all AI
│   ├── keyboards/
│   │   ├── __init__.py
│   │   └── inline.py
│   ├── managers/
│   │   ├── __init__.py
│   │   └── database_manager.py  # aiosqlite
│   ├── middlewares/
│   │   ├── __init__.py
│   │   ├── user_middleware.py
│   │   └── antiflood_middleware.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai.py           # OpenCode (SQLite DB mode)
│   │   └── user_service.py
│   ├── __init__.py
│   └── main.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env
```

#### Approach B: Build from scratch (for simple bots)

**AI backend: Gemini API via google-genai (PREFERRED)**
```python
from google import genai
client = genai.Client(api_key=GEMINI_API_KEY)
response = await client.aio.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt,
)
return response.text
```
- Package: `pip install google-genai`
- Async API: `client.aio.models.generate_content()`
- Model: `gemini-2.0-flash` (default) — fast, free tier available
- Requires: `GEMINI_API_KEY` in .env

**AI backends (by priority):**
1. **OpenCode CLI (SQLite DB mode)** — PREFERRED for this user. Free models, no API key needed. Runs `opencode run --model <model> '<prompt>'`, reads response from `~/.local/share/opencode/opencode.db`. See `references/opencode-cli-integration.md`.
2. **Gemini API** (google-genai) — Alternative. Needs GEMINI_API_KEY. Import `from google import genai`, use `client.aio.models.generate_content()`.

**Framework: aiogram 3.x (MANDATORY)**
- **aiogram 3.x** only. python-telegram-bot is NOT accepted by this user.
- Install: `pip install aiogram>=3.10`
- Parse mode: ALWAYS `parse_mode=None` for AI-generated content. Set `DefaultBotProperties(parse_mode=None)` on Bot init. AI models frequently return broken Markdown.

Key aiogram patterns:
```python
from aiogram import Bot, Dispatcher, types, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionSender

bot = Bot(token=token, default=DefaultBotProperties(parse_mode=None))
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message) -> None:
    await message.answer("text")

@dp.message()
async def handle_all(message: types.Message) -> None:
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        response = await ai_service.ask(message.text)
    await message.answer(response)
```

**Docker deployment — installing OpenCode in the container:**
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip
# Install OpenCode + symlink to PATH
RUN curl -fsSL https://opencode.ai/install | bash && \
    ln -sf /root/.opencode/bin/opencode /usr/local/bin/opencode
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir aiogram>=3.22.0 pydantic-settings>=2.12.0 loguru>=0.7.3 aiosqlite>=0.20.0
COPY bot/ ./bot/
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app
CMD ["python", "bot/main.py"]
```

```yaml
# docker-compose.yml
services:
  bot:
    build:
      context: .
      dockerfile: bot/Dockerfile
    env_file: .env
    volumes:
      - bot_data:/app/data
      - /root/.local/share/opencode:/root/.local/share/opencode
    restart: unless-stopped

volumes:
  bot_data:
```

Build & run: `docker compose up -d --build bot`

### Tier 2: Custom AI Agents ($500-3000)
- SMM automation agent (posting + analytics + content gen)
- Email marketing agent with ML personalisation
- Web automation agent (RPA-style)
- Custom site parser (Scrapling/Selenium/Stealth)
### Tier 3: Freqtrade Strategies ($200-2000)

- Ready-made strategies with backtest results
- Custom strategy by TZ
- Strategy optimisation (hyperopt)
- Signal subscription (recurring $50-100/mo)
- **Strategy collection repos** — Search, clone and bundle top GitHub strategies into a single collection repo. See `references/freqtrade-strategy-collection.md` for the complete workflow.

## Freqtrade Strategy Setup

### Config pitfalls
The Freqtrade config must include these blocks or backtesting crashes:

```json
{
    "exchange": {
        "name": "binance",
        "pair_whitelist": ["BTC/USDT", "ETH/USDT"],
        "ccxt_config": {"rateLimit": 200}
    },
    "entry_pricing": {
        "price_side": "same",
        "use_order_book": false,
        "price_last_balance": 0.0
    },
    "exit_pricing": {
        "price_side": "ask",
        "use_order_book": false,
        "price_last_balance": 0.0
    }
}
```

`pair_whitelist` is a flat array, NOT `{"pairs": [...]}`. Missing `entry_pricing` or `exit_pricing` causes KeyError.

### Hyperopt
```bash
freqtrade hyperopt --strategy <Name> --config config.json --timeframe 5m --timerange <range> --hyperopt-loss SharpeHyperOptLoss --epochs 100
```
Requires `optuna` and `scikit-learn` installed in the same venv as freqtrade.

## VK Parser via Direct API

Use VK API directly (no browser/Scrapling needed). Only requires a VK service key:

```python
API_BASE = "https://api.vk.com/method/"
# call wall.get for posts, groups.getMembers for members, newsfeed.search for search
```

Rate limit: 3 requests/sec. Add `time.sleep(0.4)` every 3 calls.
See `/root/ai-agent-services/vk-parser-bot/vk_parser.py` for working implementation.

## Sale channels

| Channel | Best for | Action |
|---------|----------|--------|
| Zismo.biz | Боты, парсеры, SMM | Register → create service thread in forum/16 or forum/110 |
| FL.ru | Trading strategies, AI agents | Respond to matching projects |
| Telegram channels | Freqtrade signals | Post demo strategy results |
| GitHub README | Freqtrade strategies | Link README → paid strategy pack |
| Reddit r/forhire | International AI agents | Post offering "Build custom AI agents" |

## User preferences
- User wants MAXIMUM conciseness: no greetings, no sign-offs, no filler. State facts and results only.
- When asking the user for something (token, credentials, decision), first explain WHY it's needed and what it enables — user corrected this when asked for bot token without context.
- Deliver working artifacts with real tool output, not plans or descriptions.
- **Only aiogram 3.x** for Telegram bots. python-telegram-bot is rejected.
- **OpenCode CLI (SQLite DB mode)** is the preferred AI backend. Not Gemini API, not NDJSON parsing.
- **NEVER write Telegram bots from scratch.** Clone a modular aiogram 3.x template from GitHub (`Er1one/telegram-bot-template` preferred), strip PostgreSQL/Redis/i18n, add OpenCode AI integration. User fired the previous agent for producing single-file garbage — this is a hard rule.

### Pushing a cloned + adapted template to GitHub

When adapting a cloned template for a client, you need to replace the origin remote and push:

```bash
# 1. Remove original origin
git remote remove origin

# 2. Create repo on GitHub (if not already created)
gh repo create geniok1980/<repo-name> --public --source=. --push

# 3. If repo already exists from a previous attempt, just set remote and push
git remote add origin https://github.com/geniok1980/<repo-name>.git
git push -u origin main   # or master, depending on default branch
```

**Troubleshooting:**
- If `gh repo create` fails with "Name already exists", the repo was created but the remote wasn't set. Just `git remote add origin` and push.
- If default branch is `master` (like shop-bot), use `git push -u origin master`.
- The token comes from `~/.git-credentials` or `GITHUB_TOKEN` in `.env`.

### Pitfalls

### 0. Telegram bot token triggers security scanner
The Hermes security scanner replaces `***` and `...` patterns in tool outputs. A Telegram bot token (`123456:ABC...`) gets mangled in displayed output. To work around it:
- Write token to `.env` file once via Python — the actual file on disk has the real token; only the displayed copy gets replaced
- Set `export BOT_TOKEN=...` in shell before running the bot — the scanner only replaces in tool outputs, not in files
- Read token at runtime: `open('.env').read().split('BOT_TOKEN=')[1].split()[0]`
- Avoid echoing the token value in commands — use Python scripts that read the file internally

### 1. Cron job `run` action may silently fail
Calling `cronjob(action='run', job_id=X)` does NOT always update `last_run_at` or produce output — the subagent may error without surfacing it. Always check:
```bash
ls ~/.hermes/cron/output/<job_id>/
```
And read the error log. If `last_status: "error"`, check the output `.md` file for the traceback.

### 2. Model override in cron causes "No LLM provider configured"
If a cron job has `model: {provider: "X", model: "Y"}`, but provider X isn't registered in the cron runtime, the job fails silently with "No LLM provider configured". Fix: omit the model override entirely (pins current provider at creation) or set it to the exact same provider+model the current session uses.

### 3. Freqtrade hyperopt needs optuna in the right venv
The `freqtrade` binary may be in a different venv than the one where optuna is installed. Install via:
```bash
uv pip install --python /path/to/venv/bin/python optuna scikit-learn
```

### 4. AI-generated Markdown breaks Telegram parsing
When `parse_mode=ParseMode.MARKDOWN` is set on the bot and the AI returns text with broken Markdown (e.g. `**bold without closing`), Telegram responds with `TelegramBadRequest: can't parse entities`.

**Fix:** Set `DefaultBotProperties(parse_mode=None)` — send all AI responses as plain text. If formatting is needed, sanitise the AI output (strip/escape markdown chars) before sending with a parse mode.

### 5. Google-genai SDK vs old google-generativelanguage
The modern Gemini SDK is `google-genai` (package name) imported as `from google import genai`. NOT `google-generativelanguage` (old, deprecated). Key differences:
- New: `from google import genai; client = genai.Client(api_key=...)`
- Old: `import google.generativelanguage as genai` — don't use this
- Async: `client.aio.models.generate_content(model=..., contents=...)` — note `aio` sub-client
- Install: `pip install google-genai`

### 6. Cloned template may have incompatible aiogram version
GitHub templates (like `aiogram/bot`) may use old aiogram versions (pre-3.0 syntax) or Python 3.9. After cloning, update `pyproject.toml` / `requirements.txt`:
- aiogram: `>=3.10.0` (current stable)
- Python: `>=3.11`
- FSM storage: use `MemoryStorage()` for simple bots, skip Redis
- Remove old-style `aiohttp` webhook setup if using polling

### 7. Zismo.biz browser interaction
zismo.biz is slow to load in browser mode (IPB forum engine). If browser times out:
- Try curl for reading topics
- Registration may need manual browser session

### 8. Reddit JSON API blocks scrapers
Reddit blocks requests without proper User-Agent and login. Use browser with old.reddit.com for anonymous access.

### 9. 409 Conflict with multiple bot instances
When a Telegram bot gets a persistent 409 Conflict, it means ANOTHER process is holding the getUpdates connection.

**Docker prevention:** Running the bot in a Docker container (`docker compose up -d`) guarantees exactly one process polls the token. No manual cleanup needed on restart — Docker replaces the container.

**Detection (non-Docker):**
```bash
ps aux | grep python3 | grep -v grep | grep -v hermes
# Look for ALL python processes related to bot scripts (aiogram_bot, start_bot, ai_telegram_bot, etc.)
```

**Fix (non-Docker):**
1. Kill ALL bot-related processes by broad pattern:
```bash
pkill -f "aiogram_bot|ai_telegram_bot|start_bot"
```
2. Clear stale session on Telegram side:
```bash
curl -s "https://api.telegram.org/bot<TOKEN>/deleteWebhook?drop_pending_updates=true"
```
3. Verify no remaining processes: `ps aux | grep -E "bot|telegram" | grep -v grep`
4. Restart (Docker or single raw process, not both).

**Verification:** A manual `getUpdates` returning 409 AFTER the fix confirms the new bot instance is already polling (not a problem). A `getMe` returning `{"ok":true}` confirms the token works.

### 10. Docker image cache ignores .env changes on rebuild
When you run `docker compose build` (without `--no-cache`), Docker caches the `COPY . .` layer. If `.env` was previously baked into the image (because `.dockerignore` didn't exclude it), a cached build reuses the old `.env` even though the host file has changed.

**Fix:** Either:
- Exclude `.env` in `.dockerignore` (the file is loaded at runtime via `env_file` in docker-compose.yml)
- Or force a full rebuild: `docker compose build --no-cache bot`
- Or touch the Dockerfile: `touch Dockerfile && docker compose build bot`

Verify: `docker inspect <container> | jq '.[0].Config.Env'` shows the runtime env vars. If they differ from the host `.env`, rebuild with `--no-cache`.

### 12. `admin_ids: list[int]` fails with single-value env var
pydantic-settings `list[int]` field doesn't accept `ADMIN_IDS=8288589227` (an int). Add a `@field_validator`:

```python
from pydantic import Field, field_validator

class Settings(BaseSettings):
    admin_ids: list[int] = Field(default_factory=list)

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        if isinstance(v, int):
            return [v]
        return v
```

### 13. pip install from pyproject.toml dependency groups may fail
If the template uses `[dependency-groups]` (uv format) in pyproject.toml, a simple `pip install` won't parse them. In Docker, use direct pip install of the packages you need rather than trying to parse `pyproject.toml`:
```dockerfile
RUN pip install --no-cache-dir aiogram>=3.10.0 google-genai>=1.0.0 loguru>=0.7.0
```
This avoids uv dependency-group parsing issues entirely.
