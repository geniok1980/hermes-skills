# NeuralDeep Catalog Dump

Свежий срез каталога neuraldeep.ru/skills (июнь 2026).

## Skills (46 шт)

### Топ по звёздам
| # | Навык | ★ | Автор | Описание |
|---|---|---|---|---|
| 1 | 1c-enterprise-skills | 166 | Nikolay-Shirokov | Работа с 1С через AI-агента |
| 2 | yandex-wordstat | 152 | Polyakov | Подбор ключевых слов Яндекса |
| 3 | yandex-metrika | 103 | Polyakov | Яндекс.Метрика |
| 4 | bitrix24 | 102 | rsvbitrix / Neural Deep | Битрикс24 CRM |
| 5 | yandex-webmaster | 62 | Polyakov | Яндекс.Вебмастер |
| 6 | yandex-search-api | 52 | Polyakov | Поисковый API Яндекса |
| 7 | wb-seller-api-skill | 48 | miilv | Wildberries Seller API |
| 8 | ru-text | 42 | talkstream | Обработка русского текста |
| 9 | ozon-seller-api-skill | 38 | miilv | Ozon Seller API |
| 10 | ssh-remote-connection | 32 | Polyakov | SSH подключение |
| 11 | neural-deep-search | 30 | vakovalskii | Поиск через NeuralDeep |
| 12 | scrapedo-web-scraper | 28 | Polyakov | Веб-скрапинг |
| 13 | find-skills | 26 | vakovalskii | Поиск по skillsbd |
| 14 | docx-contracts | 24 | Polyakov | Генерация договоров DOCX |
| 15 | telegraph-publisher | 21 | Polyakov | Публикация в Telegraph |
| 16 | genome-analizer | 17 | Polyakov | Геномный анализ |
| 17 | YooKassa | 16 | gulivan | Приём платежей |
| 18 | travel-search-ru | 15 | MissiaL | Поиск путешествий по РФ |
| 19 | positioning-plugin | 13 | Gerstep | Позиционирование |
| 20 | codex-review | 11 | Polyakov | Code review через Codex |
| 21 | 1c-agent-based-dev-framework | 11 | steelmorgan | 1С фреймворк для агентов |
| 22 | 3x-ui-vpn-skill | 11 | olegtsvetkov | 3X-UI VPN |
| 23 | yandex-tts | 11 | rasperepodvipodvert | Синтез речи Яндекс |
| 24 | slop-stop | 9 | skosovsky | Фильтр контента |
| 25 | yandex-office | 9 | bizyumov | Яндекс.Документы |

### Остальные
26. avito-api (7★) — MissiaL
27. zenmoney (7★) — miilv
28. ask-perplexity-skill (4★) — Serg2000Mr
29. mpstats (4★) — mpstats-io
30. dadata-skills (4★) — theYahia
31. gigachat-setup (3★) — trashchenkov
32. xmpp-debugger-skill (3★) — MaxeeTig
33. sbermobile-skill (2★) — pocketpet
34. claude-codex-review-skill (2★) — Serg2000Mr
35-38. gigachat-navigation / gigachat-sdk-chat / yandex-iot / gigachat-sdk-files-embeddings (1★) — trashchenkov, wannawhat
39. stitch-design-md (1★) — eveiljuice
40. claude-code-haiku-guard (1★) — Serg2000Mr
41-46. langchain-gigachat / audit-prompt-caching / gpt2giga / xbsl-ai-skills / Laravel API Architecture / gigachat-sdk-functions (0★)

## MCP Servers (26 шт)

### Российские
| MCP | ★ | Описание | Установка |
|-----|---|-----------|-----------|
| 1c-lsp-mcp-skill | 5 | MCP-bridge для 1С (BSL language server) | npx skillsbd add FSerg/1c-lsp-mcp-skill |
| mcp-max-messenger | new | VK MAX мессенджер, 21 инструмент | npx -y @woyax/mcp-max-messenger |
| mcp-chestnyi-znak | new | Честный Знак (маркировка товаров) | npx -y @woyax/mcp-chestnyi-znak |
| 1c-log-checker | 49 | Парсинг логов 1С (ClickHouse+Grafana) | npx skillsbd add steelmorgan/1c-log-checker |
| spring-mcp-1c-copilot | 40 | 1С.Напарник (SSE+Docker) | npx skillsbd add steelmorgan/spring-mcp-1c-copilot |
| dadata-mcp | new | DaData.ru — 31 инструмент | npx skillsbd add theYahia/dadata-mcp |
| mcp-bsl-lsp-bridge | 41 | BSL Language Server для 1С/OneScript | npx skillsbd add steelmorgan/mcp-bsl-lsp-bridge |
| mcp-ozon-seller | new | Ozon Seller API | npx skillsbd add woyaxnini/mcp-ozon-seller |
| ВкусВилл MCP | new | Первый открытый MCP в e-commerce РФ | endpoint: https://mcp001.vkusvill.ru/mcp |
| Додо Пицца (концепт) | — | Заказ пиццы через AI (closed) | — |
| Yandex Tracker MCP | 3 | Yandex Tracker | go install github.com/sunnyyssh/mcp-yandex-tracker |
| GigaChat Image MCP | — | Генерация через GigaChat | pip install mcp-server-gigachat-image |
| Telegram MCP | — | Telegram через MCP | pip install mcp-telegram-worker |

### Глобальные
| MCP | ★ | Описание | Установка |
|-----|---|-----------|-----------|
| Kubernetes MCP | 1361 | Управление k8s | npx mcp-server-kubernetes |
| Terraform MCP | 1288 | HashiCorp Terraform | npx @hashicorp/terraform-mcp-server |
| Docker MCP | 690 | Docker контейнеры | npx mcp-server-docker |
| Playwright MCP | 282 | Браузер | npx mcp-server-playwright |
| Puppeteer MCP | 22 | Headless Chrome | npx @anthropic-ai/mcp-puppeteer |
| PostgreSQL MCP | — | SQL запросы | npx mcp-server-postgres |
| SQLite MCP | 16 | SQLite | npx mcp-server-sqlite |
| GitHub MCP | 85 | GitHub API | npx mcp-server-github |
| Brave Search MCP | 22 | Веб-поиск | npx @anthropic-ai/mcp-brave-search |
| Fetch MCP | — | HTTP запросы | npx @anthropic-ai/mcp-fetch |
| Memory MCP | — | Память агента | npx @anthropic-ai/mcp-memory |
| Filesystem MCP | 5 | Файловая система | npx @anthropic-ai/mcp-filesystem |
| Instagram/TikTok Datalikers | 2 | Аналитика соцсетей | npx skillsbd add subzeroid/datalikers-mcp |

## CLI Tools (18 шт)

### Российские
| CLI | Описание | Установка |
|-----|----------|-----------|
| skillsbd | Установка навыков из каталога | npx skillsbd --help |
| create-skillsbd | Генератор корп. skill-библиотек | npx create-skillsbd my-company-skills |

### Глобальные AI-агенты
| CLI | ★ | Описание | Стек |
|-----|---|-----------|------|
| Gemini CLI | 98.9K | Google AI-агент в терминале | TS |
| OpenHands | 69.7K | Автономная AI-разработка | Python |
| Codex CLI | 67.3K | OpenAI AI-агент | TS |
| Cline | 59.3K | Автономный AI-агент в VS Code | TS |
| Goose | 33.5K | Open-source AI-агент от Block | Rust |
| Tabby | 33.0K | Self-hosted AI-ассистент кода | Rust |
| Devika | 19.5K | Open-source аналог Devin | Python |
| Plandex | 15.1K | AI-агент для больших проектов | Go |
| OpenCode | 11.6K | Go AI-кодинг агент | Go |
| PR-Agent | 10.7K | AI-ревью PR | Python |
| Aider | — | AI pair programming | Python |
| Continue.dev | — | Open-source IDE ассистент | TS |
| Roo Code | — | VS Code AI-агент | TS |
| AIDE | 2.7K | VS Code AI-расширение | TS |
| Coddy Agent | 3 | Go ReAct агент с SKILLS/MCP | Go |
| openapi-to-cli | 169 | OpenAPI → CLI генератор | TS |
