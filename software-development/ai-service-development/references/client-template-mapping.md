# Client Type → Telegram Bot Template Mapping

Core principle: we have a library of pre-researched templates at `/root/ai-agent-services/bot-templates/`. When a client comes with a request, pick the best template, clone it to a new directory, and adapt.

## Client types

### Service Business (пирсинг, салоны, барбершопы, маникюр)

**Template:** `T4rk123/ManicureSalon-TelegramBot` (cloned → `service-booking-bot/`)

**Features out of the box:**
- Booking with date/time selection (inline calendar)
- Price list
- Portfolio with photos (Telegram file_id)
- Reviews with rating
- Geolocation (address + maps link)
- Waitlist for occupied slots
- Admin panel: manage slots, working days, customers, broadcasts
- Reminders 24h before (APScheduler)
- 12 SQLite tables (work_days, time_slots, bookings, portfolio, reviews, users, etc.)

**Adaptation:**
- `config.example.py`: set BOT_TOKEN, ADMIN_ID, CHANNEL (for subscription check)
- `database.py`: rename tables/columns for the business domain
- `keyboards.py`: change button labels
- `handlers/start.py`: change welcome text
- `README.md` states AIOgram 3.15.0 + aiosqlite 0.20.0 + APScheduler 3.10.4

### Digital Goods / Social Media Boosts (накрутки, SMM)

**Template:** `DaniilDonskoy/Shop-bot` (cloned → `shop-bot/`)

**Features out of the box:**
- Catalog with categories and subcategories
- Cart with add/remove
- Wallet/balance (prepayment system)
- Order status (warehouse → shipped → received)
- Admin panel: add products with photo, manage orders, answer user questions
- SOS button for user support
- Docker support (webhook + polling)
- 498 GitHub stars

**Pitfalls:**
- Uses **aiogram 2.x** — needs upgrade path to 3.x for new projects
- SQLite (not for high load)
- Payment integration is stubs (Yandex.Kassa, Sberbank, Qiwi placeholders)

**Upgrade path (aiogram 2 → 3):**
- Replace `from aiogram import Bot, Dispatcher, types` → `from aiogram import Bot, Dispatcher`
- Replace `@dp.message_handler()` → `@router.message()`
- Replace `Dispatcher.set_bot()` → pass bot to `Dispatcher(bot=bot)`
- Replace `state=SomeState.some` → `StateFilter(SomeState.some)`
- Rewrite `loader.py` — no `executor.start_polling()`, use `dp.run_polling(bot)`

### AI Agent Bot (наш сервисный бот)

**Template:** `Er1one/telegram-bot-template` (currently deployed)

**Features:**
- Modular architecture (core/handlers/services/keyboards/middlewares/filters)
- AI via OpenCode CLI (free models, no API key)
- SQLite for users + AI history
- Docker deployment
- Anti-flood middleware (in-memory)

### Crypto Store (для клиентов с крипто-оплатой)

**Template:** `ilyarolf/AiogramShopBot` (192 ⭐)

**Features:**
- BTC, DOGE, LTC, SOL, ETH, BNB, USDT, USDC via KryptoExpress
- Full Telegram admin panel + SQLAdmin web panel
- Referral system with anti-abuse
- i18n (multi-language)
- Docker Compose with Caddy reverse proxy
- 646 commits, v4.2.0, actively maintained

**Cost:** Heavy — needs PostgreSQL + Redis + Caddy in production.

## When a client asks for a bot

1. Identify client type (service / goods / crypto / AI)
2. Pick template from the mapping above
3. `cd /root/ai-agent-services/ && cp -r bot-templates/<template> <client-project-name>/`
4. Adapt: config, branding, handlers text, database schema (if needed)
5. Dockerize if not already
6. Deploy

## IMPORTANT

- NEVER write Telegram bots from scratch — always clone + adapt
- ALWAYS check GitHub first if no existing template matches
- The user rejected single-file bots explicitly — always use modular structure
- aiogram 3.x only — reject any template using python-telegram-bot or aiogram < 3
