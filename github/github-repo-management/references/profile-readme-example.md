# Profile README Example: geniok1980

**User:** Евгений — автоматизация кафе/баров/ресторанов (rkeeper, iiko), дашборды, аналитика, системы лояльности, торговые боты, разработка.
**Telegram:** @geniok
**GitHub:** geniok1980

## Current README.md

```markdown
### Привет, я Евгений 👋

Автоматизирую кафе, бары и рестораны на rkeeper и iiko, разрабатываю торговых ботов,
строю дашборды и аналитику, внедряю системы лояльности и решаю сложные технические задачи.

---

### 🔥 Чем занимаюсь

| Направление | Подробнее |
|---|---|
| 🏪 **Автоматизация кафе/баров/ресторанов** | rkeeper, iiko — внедрение, настройка, интеграция, сопровождение |
| 📊 **Дашборды и аналитика** | Системы отчётности, бизнес-аналитика, визуализация данных, OLAP |
| 🎯 **Системы лояльности** | Разработка и внедрение программ лояльности для ресторанов и розницы |
| 🤖 **Торговые боты** | Криптотрейдинг, фондовый рынок (MOEX), алгоритмическая торговля |
| 💻 **Разработка** | Telegram-боты, API-интеграции, парсинг, веб-сервисы, автоматизация |
| ⚙️ **DevOps** | Docker, CI/CD, деплой, администрирование серверов |

---

### 🛠️ Технологии

**Языки:**  
![TypeScript](https://img.shields.io/badge/-TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Bun](https://img.shields.io/badge/-Bun-000000?style=flat-square&logo=bun&logoColor=white)

**Фреймворки и инструменты:**  
![React](https://img.shields.io/badge/-React-61DAFB?style=flat-square&logo=react&logoColor=black)
![Hono.js](https://img.shields.io/badge/-Hono.js-E36002?style=flat-square&logo=hono&logoColor=white)
![Vite](https://img.shields.io/badge/-Vite-646CFF?style=flat-square&logo=vite&logoColor=white)
![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Node.js](https://img.shields.io/badge/-Node.js-339933?style=flat-square&logo=nodedotjs&logoColor=white)

**Базы данных:**  
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![SQLite](https://img.shields.io/badge/-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)

**Платформы:**  
![GitHub](https://img.shields.io/badge/-GitHub-181717?style=flat-square&logo=github&logoColor=white)
![Vercel](https://img.shields.io/badge/-Vercel-000000?style=flat-square&logo=vercel&logoColor=white)
![Cloudflare](https://img.shields.io/badge/-Cloudflare-F38020?style=flat-square&logo=cloudflare&logoColor=white)

---

### 📌 Проекты

🔹 [**clawhost**](https://github.com/geniok1980/clawhost) — Платформа для одно-кликовой деплоймента OpenClaw и Hermes Agent. [→ clawhost.geniok.ru](https://clawhost.geniok.ru)
🔹 [**rkdash**](https://github.com/geniok1980/rkdash) — Аналитическая система для Rkeeper с AI-агентами: дашборды, чат с БД, план/факт. [→ rkdash.geniok.ru](https://rkdash.geniok.ru)
🔹 [**FreqDash**](https://github.com/geniok1980/freqwebui-free) — Multi-Bot Dashboard для Freqtrade: управление несколькими ботами, аналитика, мониторинг
🔹 [**ai-photostudio**](https://github.com/geniok1980/ai-photostudio) — AI фотостудия: генерация фото и видео через Gemini/Veo. Turborepo, Bun, Hono.js, React + Vite
🔹 **dashboard** — Универсальная панель управления и мониторинга

---

### 📊 Статистика

<p align="center">
  <img src="https://github-readme-stats.vercel.app/api?username=geniok1980&show_icons=true&theme=dark&hide_border=true&count_private=true" />
  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=geniok1980&layout=compact&theme=dark&hide_border=true" />
</p>

---

### 📬 Контакты

[![Telegram](https://img.shields.io/badge/-Telegram-26A5E4?style=flat-square&logo=telegram&logoColor=white)](https://t.me/geniok)
[![GitHub](https://img.shields.io/badge/-GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/geniok1980)

---

*По вопросам автоматизации ресторанов, разработки ботов и технических решений — в Telegram 👆*
```

## User profile settings (API)

```json
{
  "name": "Евгений Шляхтин",
  "bio": "🏪 Автоматизация кафе/баров/ресторанов на rkeeper и iiko | 📊 Дашборды и аналитика | 🎯 Системы лояльности | 🤖 Торговые боты | 💻 TypeScript, Python",
  "location": "Самара",
  "company": "rkeeper automation / trading bots"
}
```

## Workflow: Adding a new project to the profile

When adding a new public project repo:

1. **Create repo** on GitHub (public, auto_init=true, with description)
2. **Write README.md** with consistent structure:
   - Title + badges
   - What the project does (in Russian for this user)
   - Features list
   - Tech stack table
   - Link to live demo/site (if applicable)
   - Contact info (Telegram @geniok)
3. **Set topics** via API (`PUT /repos/:owner/:repo/topics`)
4. **Add to profile README** under "Проекты" section with `🔹 [**name**](link) — description. [→ link](url)` format
5. **Commit and push** both repos

## Pitfalls & Lessons

### CDN caching
README renders in the repo view immediately, but profile page may lag (CDN cache — can take minutes to hours). This is normal — no additional config needed.

### Repo rename / rebranding pattern
If a repo has a different GitHub name than the project brand (e.g. GitHub name `freqwebui-free` but project is called **FreqDash**), link to the actual GitHub repo but use the project name as the display text:
```markdown
🔹 [**FreqDash**](https://github.com/geniok1980/freqwebui-free) — Description...
```
This keeps the URL stable while presenting the brand name to visitors.

### Private projects
**Never** list private repos or reference private project names in the profile README. The profile is public. If a repo was recently made private or deleted, remove it from the README immediately. The projects section should only show what you want potential clients/employers to see.

### Bio should be concise
Emoji-prefixed pipe-separated categories work well. Keep under the GitHub character limit (~160 chars).

### Link format in descriptions
Use visible URLs with arrow: `[→ demo.geniok.ru](https://...)` instead of `[Сайт](...)` — renders cleaner and the user can see the URL before clicking.

### Project descriptions
Should be detailed — include what tech is used and what problem it solves, not just a one-liner. This helps visitors understand the project scope at a glance.

### Keeping profile clean
Periodically audit your repo list. Delete stale/irrelevant public repos to keep the profile focused. Use bulk delete via API:
```bash
GH_TOKEN=$(git remote get-url origin | sed 's|.*https://||;s|@github.com.*||')
for repo in name1 name2 name3; do
  curl -s -X DELETE -H "Authorization: token $GH_TOKEN" \
    "https://api.github.com/repos/$GH_USER/$repo"
done
```
