# GitHub Telegram Bot Templates — Research (June 2026)

## Top templates for aiogram 3.x bots

### General / AI Agent bots

| Repo | Stars | Python | DB | Docker | Updated | Best for |
|------|-------|--------|----|--------|---------|---------|
| **Er1one/telegram-bot-template** | 8 | 3.13+ | PostgreSQL | ✅ | Dec 2025 | **PREFERRED** — cleanest modular structure, easy to strip |
| donbarbos/telegram-bot-template | 464 | 3.10+ | PostgreSQL | ✅ | May 2026 | Solid but heavy (Flask+Prometheus+Grafana) |
| aiogram/bot | 282 | 3.7+ | PostgreSQL | ✅ | Mar 2026 | Official, but old Python target |
| MassonNN/masson-aiogram-template | 126 | 3.10+ | PostgreSQL | ✅ | May 2026 | Good structure, has templates |
| wakaree/aiogram_bot_template | 165 | 3.10+ | PostgreSQL+asyncpg | ✅ | May 2026 | SQLAlchemy+Alembic |

### Service Business (booking, salon, barbershop)

| Repo | Stars | Stack | Best for |
|------|-------|-------|----------|
| **T4rk123/ManicureSalon-TelegramBot** | 1 | aiogram 3.x + SQLite + APScheduler | **BEST for service booking** — booking with calendar, portfolio, reviews, pricing, location, waitlist, admin panel. 12 SQLite tables. Easy rebrand. |
| 6atyrlan/logovo-barbershop-bot | 0 | aiogram 3.x, single-file | Reference only — minimal booking flow |
| Sahakian88/beauty-salon-bot | 0 | aiogram 3.x + React (Mini-App) | Reference — has mini-app frontend |

### Goods / Digital Products

| Repo | Stars | Stack | Best for |
|------|-------|-------|----------|
| **DaniilDonskoy/Shop-bot** | 498 | aiogram 2.x + SQLite | **BEST for shop** — catalog, cart, wallet, delivery, admin, Docker |
| **ilyarolf/AiogramShopBot** | 192 | aiogram 3.x + PostgreSQL + Redis + FastAPI | **BEST for crypto shop** — crypto payments, referrals, full admin, i18n |
| rashidovich2/TelegramGoodsInbot | 99 | aiogram 2.x + SQLite | Legacy — multi-city, multi-seller, many payments. Abandoned 3 years. |
| twers1/telegram-bot-shop | 39 | python-telegram-bot + PostgreSQL | python-telegram-bot — NOT our stack |

### Pre-cloned templates library

All templates are pre-cloned at `/root/ai-agent-services/bot-templates/` and pushed to GitHub under geniok1980:

```bash
/root/ai-agent-services/bot-templates/
├── service-booking-bot/   # T4rk123/ManicureSalon-TelegramBot
│                          # → github.com/geniok1980/tg-service-booking-bot
└── shop-bot/              # DaniilDonskoy/Shop-bot
                           # → github.com/geniok1980/tg-shop-bot
```

Also deployed:
```bash
/root/ai-agent-services/telegram-bot-platform/  # Er1one adapted
                                                 # → github.com/geniok1980/tg-ai-agent-bot
```

See `references/client-template-mapping.md` for which template to use per client type.

## Er1one/telegram-bot-template — recommended template

This is the **current preferred template** for Telegram bot projects. It has:
- Cleanest module separation (`bot/core/`, `bot/handlers/`, `bot/services/`, `bot/keyboards/`, `bot/middlewares/`, `bot/filters/`)
- `Settings` via pydantic-settings (no configparser)
- `Makefile` with 20+ commands
- `tests/` directory with pytest
- Docker support
- 14 commits, last updated Dec 2025

### Stripping Er1one for a simple AI agent bot

Remove PostgreSQL, Redis, i18n, webhook, FastAPI, and monitoring:

```bash
# Clone
git clone https://github.com/Er1one/telegram-bot-platform.git
cd telegram-bot-platform

# Delete unnecessary components
rm -rf \
  bot/managers/redis_manager.py \
  bot/managers/i18n_manager.py \
  bot/routes/ \
  bot/models/ \
  bot/utils/ \
  bot/locales/ \
  bot/handlers/groups/ \
  bot/handlers/private/settings.py \
  bot/handlers/private/blocking.py \
  bot/services/broadcast_service.py \
  bot/middlewares/i18n_middleware.py \
  bot/filters/admin.py \
  bot/filters/chat_type.py \
  bot/filters/content.py \
  docker-compose.dev.yml \
  docker-compose.prod.yml \
  .env.example \
  .coverage \
  pytest.ini \
  tests/ \
  Makefile \
  CLAUDE.md
```

Then rewrite these files (see session-specific code in `references/telegram-bot-deployment.md`):
- `pyproject.toml` — remove aerich, fastapi, fluent-runtime, msgspec, redis, tortoise-orm, uvicorn, aiogram-i18n. Keep: aiogram, pydantic-settings, loguru, aiosqlite.
- `bot/core/config.py` — remove pg_*, redis_*, webhook_url, app_port. Keep bot_token, admin_ids, debug.
- `bot/core/loader.py` — remove FastAPI, RedisStorage, Tortoise. Use MemoryStorage.
- `bot/main.py` — polling mode, no FastAPI/uvicorn/i18n.
- `bot/managers/database_manager.py` — replace Tortoise with aiosqlite.
- `bot/managers/__init__.py` — re-create with just DatabaseManager.
- `bot/middlewares/user_middleware.py` — simplify, remove Tortoise.
- `bot/middlewares/antiflood_middleware.py` — replace Redis with in-memory defaultdict.
- `bot/services/user_service.py` — simplify to SQLite.
- `bot/keyboards/inline.py` — rewrite without i18n.
- `bot/handlers/private/*.py` — rewrite without i18n.
- `docker-compose.yml` — just bot service + volumes, no postgres/redis.
- `bot/Dockerfile` — python:3.11-slim + pip install + opencode install.

### Er1one adapted project structure (final)

```
telegram-bot-platform/
├── bot/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # pydantic-settings
│   │   ├── loader.py        # Bot + Dispatcher (MemoryStorage)
│   │   └── logging.py       # loguru setup
│   ├── filters/
│   │   └── __init__.py      # IsPrivateChat, IsAdmin
│   ├── handlers/
│   │   ├── __init__.py      # router aggregator
│   │   ├── errors_router.py
│   │   └── private/
│   │       ├── __init__.py
│   │       ├── start.py
│   │       ├── commands.py  # /menu, /help, /ask, /admin
│   │       ├── menu.py      # callback query handlers
│   │       └── free_text.py # catch-all AI handler
│   ├── keyboards/
│   │   ├── __init__.py
│   │   └── inline.py        # get_main_menu_keyboard, get_back_keyboard
│   ├── managers/
│   │   ├── __init__.py
│   │   └── database_manager.py  # aiosqlite, users + ai_history tables
│   ├── middlewares/
│   │   ├── __init__.py
│   │   ├── user_middleware.py   # auto-register users
│   │   └── antiflood_middleware.py  # in-memory throttling
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai.py             # OpenCode CLI integration
│   │   └── user_service.py   # SQLite user CRUD
│   ├── __init__.py
│   └── main.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env
```

## Common adaptation steps

1. `git clone <repo> telegram-bot-platform && cd telegram-bot-platform`
2. Remove unnecessary: `rm -rf admin/ configs/ scripts/ .github/`
3. Update pyproject.toml: Python>=3.11, keep only bot deps (aiogram, aiosqlite, loguru)
4. Rewrite core/config.py: pydantic-settings with BOT_TOKEN, ADMIN_IDS (add @field_validator for int→list conversion)
5. Rewrite core/loader.py: MemoryStorage instead of Redis, remove aiohttp web app
6. Add bot/services/ai.py: OpenCode CLI integration
7. Create handlers: start, menu, commands, free_text
8. Remove monitoring/analytics middleware references
9. Simplify Dockerfile: python:3.11-slim + pip install + opencode install with symlink
10. Simplify docker-compose.yml: just bot service + .env + opencode volume
