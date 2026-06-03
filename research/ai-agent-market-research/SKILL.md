---
name: ai-agent-market-research
title: AI Agent Market Research
description: Daily multi-platform research for AI agent earning opportunities — Russian and international platforms.
trigger: user asks to research earning opportunities, find freelance gigs for AI agents, or set up recurring market monitoring.
---

# AI Agent Market Research

Daily research workflow scanning Russian and international platforms for earning opportunities that AI agents can fulfill.

## When to Use

- User asks "найди возможности заработка для ИИ-агентов"
- User asks "сделай ресерч по заработку в интернете"
- User wants to set up recurring market monitoring
- Any "что сейчас востребовано" / "где можно заработать" type query

## Research Targets

### Russian Platforms
| Platform | Section | What to look for |
|---|---|---|
| zismo.biz | forum/110 (Вакансии/Ищу работу) | Bot dev, parsing, automation, AI/ML |
| zismo.biz | forum/16 (Покупка/продажа и услуги) | SMM services, dev offers |
| zismo.biz | forum/92 (Программирование) | Dev discussions, custom scripts |
| zismo.biz | forum/111 (Биржа сообществ) | Channel/group marketplace |
| zismo.biz | forum/120 (Crypto&Airdrops) | Crypto opportunities |
| fl.ru, freelance.habr, kwork | — | Orders for bots, parsers, automation |

### International Platforms
| Platform | Target | What to search |
|---|---|---|
| Reddit | **r/forhire, r/slavelabour** (primary — active freelance gigs), r/AI_Agents, r/TelegramBots, r/freelance, r/beermoney | Posts sorted by new. Keywords: "telegram bot", "ai agent", "scraper", "parser" |
| YouTube | Search | Videos <7d: "make money with AI agents 2026", "AI automation freelance", "build AI agent for clients", "passive income AI tools", "Telegram bot automation business" |
| Google Trends | Trends Explorer | Compare: "AI agent development service", "Telegram bot developer", "freqtrade trading bot" — note rising queries last 7 days |

## Output Format

```
**Дата:** YYYY-MM-DD
**Русские площадки:**
- Zismo.biz: (summary, topic links)
- fl.ru/kwork: (summary)

**Иностранные:**
- Reddit: (hot threads, links)
- YouTube: (new videos summary)
- Google Trends: (trending terms)

**Топ-3 возможности для AI-агента на сегодня:**
1. ...
2. ...
3. ...
```

## Cron Setup

Use `cronjob` tool with `enabled_toolsets: ["web", "terminal"]`.

**Prompt template (customize as needed):**
```
Проведи ежедневный ресерч по заработку в интернете для AI-агентов.
Обязательно проверить: zismo.biz (forum/110, forum/16), fl.ru, freelance.habr, kwork.
Международные: Reddit (r/forhire, r/slavelabour, r/AI_Agents, r/TelegramBots — посты за 24ч),
YouTube (видео до 7 дней: "AI agents freelance", "Telegram bot automation business"),
Google Trends ("AI agent development service", "Telegram bot developer", "freqtrade" за 7 дней).

Формат отчёта:
— **Новые заказы** (ссылка, кратко, бюджет если есть)
— **Тренды/инсайты** (что ищут, какие технологии)
— **Ценные идеи для монетизации** (ниши с малой конкуренцией)
— **Кому предложить услуги напрямую** (из Reddit/YouTube)
```

**Model:** ALWAYS pin with `model: {provider: "X", model: "Y"}` — use the exact provider+model from the current session (e.g. `{"model":"deepseek-v4-flash","provider":"opencode-go"}`). Omitting it can cause `RuntimeError: No LLM provider configured` because the cron runner resolves providers independently from the session. Test with `cronjob(action='run', job_id=...)` and check `~/.hermes/cron/output/<job_id>/` for errors.

**Schedule:** daily at 10:00 user-timezone.

**Delivery:** omit `deliver` parameter (auto-delivers to origin). The system handles delivery automatically — the prompt just needs to say «Отправь отчёт пользователю».

## Pitfalls

- zismo.biz uses IPB forum engine — content is JS-rendered. Use `terminal` with `curl` + regex to extract topics. Steps: `curl -sL URL | sed 's/<script[^>]*>.*<\/script>//g' | sed 's/<style[^>]*>.*<\/style>//g' | sed 's/<[^>]*>//g'` then grep for keywords. Browser tools may timeout on this site.
- **Reddit blocks all scrapers.** Both `old.reddit.com` and JSON API return `"Blocked"` page. `web_search` tool may work. Alternative: use Google search with `site:reddit.com` prefix or browser with residential proxies.
- **DuckDuckGo HTML** blocks with CAPTCHA challenge. Not usable for automated research.
- **Google Trends** returns HTTP 429 (Too Many Requests) under automation. The RSS feed `trends.google.com/trending/rss?geo=US` still works for daily trending terms.
- **YouTube** search works reliably via `browser_navigate` to `https://www.youtube.com/results?search_query=...&sp=CAISBBABGAE%3D` (filter by date). The `browser_snapshot` then shows video titles, views, and age.
- **FL.ru** partially parseable via `curl` — topic titles appear in raw HTML as plain text after stripping tags. Full order details require login.
- **SearXNG instances** (privacy metasearch) inconsistently block — not a reliable fallback.
- Russian freelance platforms often require registration to see full order details — note availability restrictions in output.
- **Model in cron:** never use a model from a different provider than what's active in the session. Always test `cronjob(action='run')` and check `~/.hermes/cron/output/<job_id>/` for errors before declaring success.

## Linked References

- `references/zismo-biz-structure.md` — forum sections, topic counts, URL patterns, parsing tips, observed demand types.
- `references/international-platforms-scraping.md` — per-platform scraping status (Reddit blocked, YouTube via browser, Google Trends rate-limited, etc.) and workarounds.
