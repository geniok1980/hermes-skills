---
name: neuraldeep-ecosystem
description: Russian AI infrastructure from NeuralDeep.ru — self-hosted LLM API on GPU in Russia, skillsbd catalog of skills/MCP/CLI for AI agents, and setup patterns for their ecosystem.
---

# NeuralDeep Ecosystem

Russian AI-infrastructure platform providing self-hosted OSS models on GPU in Russia, plus an open-source aggregator (skillsbd) of skills, MCP servers, and CLI tools for Russian services.

## NeuralDeep Services

| Service | URL | Description |
|---------|-----|-------------|
| **hub** | hub.neuraldeep.ru | LLM API gateway (10 OSS models, liteLLM, vLLM). Бесплатный тариф |
| **api** | api.neuraldeep.ru | OpenAI-совместимый API: `/v1/chat`, `/v1/embeddings`, `/v1/audio` |
| **coder** | coder.neuraldeep.ru | Браузерный AI-IDE (opencode + Firecracker microVM) |
| **drift** | drift.neuraldeep.ru | Self-hosted сеть AI-агентов (Telegram + веб + API) |
| **search** | search.neuraldeep.ru | Корпоративный поиск + RAG (SearXNG, FastAPI) |
| **skillsbd** | neuraldeep.ru/skills | Каталог навыков, MCP и CLI |

## SkillsBD — установка навыков

### Базовые команды

```bash
# Установить навык из GitHub репозитория
npx skillsbd add <owner/repo>

# Примеры
npx skillsbd add vakovalskii/skillsbd-skills       # find-skills
npx skillsbd add artwist-polyakov/polyakov-claude-skills  # 19 навыков (Яндекс, SSH, scraper и др.)
npx skillsbd add teng-lin/notebooklm-py            # notebooklm-py
npx skillsbd add theYahia/dadata-mcp               # DaData (адреса, компании, ФИО)
```

### Структура установки

Skills устанавливаются в `~/.skills/<name>/`. Каждый содержит `SKILL.md` (агентский навык), `CLAUDE.md`/`AGENTS.md` (для Claude Code и других агентов).

### Питфоллы

- **MCP серверы ≠ навыки.** Некоторые репозитории в каталоге — MCP-серверы (npm-пакеты), а не skillsbd-совместимые навыки. skillsbd выдаст `✗ Навыки не найдены`. Пример: `woyaxnini/mcp-chestnyi-znak` — это npm-пакет `@woyax/mcp-chestnyi-znak`, устанавливается через `npx -y @woyax/mcp-chestnyi-znak`, не через skillsbd.
- **Установка Python-пакетов.** Сервер на Debian/Ubuntu с PEP 668 — используй `uv pip install` (не `pip`). `pip install` упадёт с `externally-managed-environment`.
- **Playwright на headless-сервере.** `playwright install chromium` ставит браузер в `~/.cache/ms-playwright/`. Для GUI-логина (Google OAuth) нужен display или `--browser-cookies` со стороннего браузера.

## notebooklm-py (установка через skillsbd)

Установлен через skillsbd, пакет — через uv.

```bash
# Установка пакета
uv pip install "notebooklm-py[browser]"

# Браузер для авторизации
uv run playwright install chromium

# Проверка авторизации
uv run notebooklm auth check --test --json
# Ожидай: "status": "ok" + "checks.token_fetch": true

# Логин (требует GUI или cookies)
notebooklm login                                    # открывает браузер для Google OAuth
notebooklm login --browser-cookies chrome           # куки из установленного Chrome
```

**На headless-сервере:** логин через браузер не работает (нет display). Варианты:
- Установить `[cookies]` extra и использовать `--browser-cookies`
- Запустить `notebooklm login` на локальной машине и перенести `storage_state.json`
- Автообновление сессии: `notebooklm auth refresh` (можно в cron, 15-20 мин)

## Релевантные навыки из каталога

### Для ресторанного бизнеса (R-Keeper, 1С)
- `1c-enterprise-skills` — работа с 1С через AI-агента
- `bitrix24` — CRM через AI-агента
- `YooKassa` — приём платежей
- `docx-contracts` — генерация договоров

### Для маркетплейсов (WB, Ozon)
- `wb-seller-api-skill` — Wildberries
- `ozon-seller-api-skill` — Ozon
- `mpstats` — аналитика

### Для контента и продвижения
- `yandex-wordstat` — подбор ключевых слов
- `yandex-metrika` — аналитика трафика
- `yandex-webmaster` — управление сайтами
- `yandex-search-api` — поисковый API
- `telegraph-publisher` — публикация в Telegraph
- `yandex-tts` — синтез речи

### MCP серверы (установка через npm, не skillsbd)
- `@woyax/mcp-max-messenger` — VK MAX мессенджер (21 инструмент)
- `@woyax/mcp-chestnyi-znak` — система маркировки товаров (требует JWT + КриптоПро)
- `mcp-server-docker` — управление Docker контейнерами
- `mcp-server-postgres` — SQL запросы
- `mcp-server-github` — GitHub через агента
- `mcp-server-playwright` — управление браузером
