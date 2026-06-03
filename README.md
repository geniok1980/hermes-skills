# Hermes Agent Skills Collection

Коллекция лучших навыков (skills) для **Hermes Agent** от Nous Research.

## Источники

| Репозиторий | ⭐ | Описание |
|---|---|---|
| `0xNyk/awesome-hermes-agent` | 3,671 | Официальный curated list всех навыков |
| `wondelai/skills` | 380+ | Кроссплатформенные навыки (agentskills.io) |
| `42-evey/hermes-plugins` | — | Плагины: управление целями, bridge, cost control |
| `Romanescu11/hermes-skill-factory` | — | Авто-генерация навыков из повторяющихся задач |
| `tlehman/litprog-skill` | 75+ | Literate programming (Hermes + Claude + OpenCode) |
| `Cranot/super-hermes` | — | Мета-рассуждения: генерация промптов |
| `Yonkoo11/hermes-dojo` | — | Self-improvement: мониторинг + итерация навыков |

## Встроенные навыки Hermes (111 шт.)

Полный список доступен в `/usr/local/lib/hermes-agent/` и `~/.hermes/skills/`.

### Ключевые категории:
- **software-development**: plan, web-scraping, tdd, ai-service-development, ai-generation-mode-development, writing-plans
- **devops**: cloudflare-dns-caddy-proxy, cron-jobs, webhook-subscriptions
- **creative**: claude-design, excalidraw, sketch, p5js, ascii-art, manim-video
- **github**: code-review, pr-workflow, issues, repo-management, research
- **mlops**: llama-cpp, vllm, huggingface-hub, outlines, unsloth, axolotl
- **research**: arxiv, blogwatcher, polymarket, ai-agent-market-research
- **productivity**: notion, airtable, google-workspace, obsidian, powerpoint
- **social-media**: telegram-promotion, xurl, youtube-content

## Как использовать

1. Скопировать нужную папку навыка в `~/.hermes/skills/`
2. Перезапустить Hermes: `hermes reset`
3. Навык будет доступен через `skill_view(name)`
