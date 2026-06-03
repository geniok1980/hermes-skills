# AI Agent Services — Product Structure

## Root directory
```
/root/ai-agent-services/
├── bot-templates/                 # Pre-cloned templates for rapid adaptation
│   ├── service-booking-bot/       # T4rk123/ManicureSalon-TelegramBot
│   ├── shop-bot/                  # DaniilDonskoy/Shop-bot
│   └── README.md                  # Catalog with plan and template mapping
├── telegram-bot-platform/         # Our main AI agent bot (deployed)
│   ├── bot/                       # Modular structure (aiogram 3.x)
│   ├── Dockerfile
│   └── docker-compose.yml
├── freqtrade-strategies/          # Freqtrade trading strategies
│   ├── config.json
│   └── user_data/strategies/
│       └── AIAgentStrategyV2.py
├── telegram-ai-bot/               # Legacy single-file bot (deprecated)
└── vk-parser-bot/                 # VK API parser
    └── vk_parser.py
```

## Templates on GitHub (public)
| Repo | URL | Based on |
|------|-----|----------|
| tg-service-booking-bot | github.com/geniok1980/tg-service-booking-bot | T4rk123/ManicureSalon-TelegramBot |
| tg-shop-bot | github.com/geniok1980/tg-shop-bot | DaniilDonskoy/Shop-bot |
| tg-ai-agent-bot | github.com/geniok1980/tg-ai-agent-bot | Er1one/telegram-bot-template |

## Pricing tiers
| Tier | Range | Products | Target |
|------|-------|----------|--------|
| 1 | $100-500 | Telegram bot with AI, VK parser | Zismo, FL.ru |
| 2 | $500-3000 | Custom AI agents, full automation | FL.ru, international |
| 3 | $200-2000 | Freqtrade strategies + signals | Crypto communities |

## Sales channels
| Channel | Product | Action |
|---------|---------|--------|
| Zismo.biz forum/110 | Tier 1 | Create service thread |
| FL.ru | Tier 1, 2 | Bid on matching projects |
| Telegram crypto groups | Tier 3 | Post backtest results |
| GitHub (README) | Tier 3 | Link to paid pack |
| Reddit r/forhire | Tier 2 | Post offering |
