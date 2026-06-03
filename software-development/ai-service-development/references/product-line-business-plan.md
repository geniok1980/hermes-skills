# Product Line Business Plan — AI Agent Services

## Overview
Full plan for building and selling Telegram bots, AI agents, and Freqtrade strategies as a service business.

## Product Line (3 Tiers)

### Tier 1: Telegram Bots ($100-500) — Быстрый вход, много заказов

| Bot type | Description | Template | Est. effort |
|----------|-------------|----------|-------------|
| VK Parser Bot | Collect audience from VK groups, parse wall/donut, auto-export | Custom script + Telegram frontend | 1-2 days |
| Lead Generation Bot | Bot-заявки with CRM/iiko integration, booking form | `service-booking-bot/` | 2-3 days |
| AI Auto-Responder Bot | GPT/Claude under the hood, answers client questions | `tg-ai-agent-bot` | 1-2 days |
| Group Admin Bot | Auto-moderation, timed comment closing, spam filter | `service-booking-bot/` or custom | 1 day |

### Tier 2: Custom AI Agents ($500-3000) — Маржа выше, конкурентов мало

| Agent | Description | Tech stack |
|-------|-------------|------------|
| SMM Automation Agent | Cross-platform posting + analytics + AI content gen | Python + API integrations |
| Email Marketing Agent | ML-based personalisation, campaign automation | Python + SMTP/API |
| Web RPA Agent | Website automation (fill forms, scrape, submit) | Scrapling / Playwright |
| Custom Parser | Any site parser with data export | Scrapling / Selenium / Stealth |

### Tier 3: Freqtrade Strategies ($200-2000) — Готовый спрос, recurring

| Product | Price | Description |
|---------|-------|-------------|
| One-off strategy by TZ | $300-1000 | Custom strategy built to client's specification |
| Strategy pack (5-10) | $200-500 | Bundle of tested strategies with backtest reports |
| Signal subscription | $50-100/mo | Telegram bot sends trade signals (recurring) |
| Strategy optimisation | $100-200/mo | Hyperopt tuning, parameter adjustment retainer |

## Sales Channels

| Channel | What to sell | Why |
|---------|-------------|-----|
| **Zismo.biz** (forum/110, forum/16) | Tier 1 — bots, parsers, scripts | Direct demand, live audience |
| **FL.ru** (Крипто, Автоматизация) | Tier 2, Tier 3 — AI agents, strategies | Clients pay, have budget |
| **Telegram crypto channels** | Tier 3 — Freqtrade strategies, signals | Target audience, trust |
| **GitHub README** | Tier 3 — Freqtrade strategies | 127 freqtrade repos, README → referral link |
| **Reddit** (r/forhire, r/AI_Agents) | Tier 2 — Build & Sell AI Agents | Western market, $1000+/project |

## Freqtrade Demand (confirmed)

- Freqtrade repo: 51K ⭐, 10.6K forks
- 127 repos on the topic, 65+ strategy-only repos
- Top strategies: 163⭐, 564⭐, 326⭐ ("strategies that work")
- People pay for working strategies — most free ones are unprofitable or outdated
- Growing trend: ML/RL strategies (freqtrade-gym — 229⭐)
- Direct TZ found on FL.ru: "Develop TV trading strategy, have TZ, need implementation"

## Action Plan

### Week 1 — Build 3 base bots + publish portfolio
1. VK Parser Bot (standalone)
2. AI Auto-Responder Bot (from `tg-ai-agent-bot`)
3. Lead Generation Bot (from `service-booking-bot/`)
4. Post on Zismo.biz in service thread

### Week 2 — Build Freqtrade strategies
1. Write 3 strategies with backtests
2. GitHub demo repos
3. Telegram channel post with results

### Week 3 — Sales
1. Forums + FL.ru bidding
2. First orders
3. Recurring model: bot support + signal subscriptions

## Template Library (cloned and pushed)

All templates on GitHub under geniok1980:

| Repo | GitHub | Based on | Use for |
|------|--------|----------|---------|
| `tg-service-booking-bot` | github.com/geniok1980/tg-service-booking-bot | T4rk123/ManicureSalon-TelegramBot | Service business (piercing, salon, barber) |
| `tg-shop-bot` | github.com/geniok1980/tg-shop-bot | DaniilDonskoy/Shop-bot | Digital goods, SMM boosts, shops |
| `tg-ai-agent-bot` | github.com/geniok1980/tg-ai-agent-bot | Er1one/telegram-bot-template | AI agent bots, auto-responders |
