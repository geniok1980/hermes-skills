# geniok.ru Landing Page Reference

## File Layout

```
/var/www/geniok/
├── index.html              # Main portfolio page
└── skills/
    └── index.html          # Agent Skills catalog (separate page)
```

## Caddy Config (in /etc/caddy/Caddyfile)

```
geniok.ru {
    root * /var/www/geniok
    file_server
}
```

Caddy serves any file/directory under the root automatically — no restart needed after adding files.

## Design Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--bg` | `#0a0a0f` | Page background |
| `--bg2` | `#12121a` | Secondary background |
| `--card` | `#1a1a28` | Section card background |
| `--card` (skills) | `#18181b` | Skills row background |
| `--border` | `#2a2a3e` | Section borders |
| `--border` (skills) | `#27272a` | Skills row borders |
| `--accent` | `#7c5cfc` | Primary accent (purple) |
| `--accent2` | `#5c9cfc` | Secondary accent (blue) |
| `--text` | `#e8e8f0` | Primary text |
| `--text2` | `#8888aa` | Muted text |
| Font | `Inter` | Google Fonts import |

## GitHub Repos

- **geniok1980/geniok-landing** (PRIVATE) — Backup of the entire landing page
- **geniok1980/Skills** (PUBLIC) — Skills catalog, contains:
  - `skills.json` — manifest with all skills (name, description, category, author)
  - `{skill-name}/SKILL.md` — individual skill metadata files
- **geniok1980/Freqtrade-Strategies** (PUBLIC) — Freqtrade strategies, contains:
  - `strategies.json` — manifest with all strategies (name, description, type, timeframe, pairs, ml, status)
  - `{strategy-name}/{strategy-name}.py` — individual strategy Python files

## Catalog Pages

### Skills Page (/skills/)
Fetches from: `https://raw.githubusercontent.com/geniok1980/Skills/main/skills.json`
Detail page: `/skills/skill.html?name=skill-name`

### Strategies Page (/strategies/)
Fetches from: `https://raw.githubusercontent.com/geniok1980/Freqtrade-Strategies/main/strategies.json`
Detail page: `/strategies/strategy.html?name=strategy-name`

No Caddy changes needed — creating a directory with index.html makes it available at the corresponding path.

## Section Architecture

- **Main page (index.html):** lightweight, has nav links + hero + projects grid + skills link + strategies link + open source + contacts
- **Skills page (skills/index.html):** standalone, full styles + JS, fetches from GitHub, back button to /
- **Strategies page (strategies/index.html):** standalone, full styles + JS, fetches from GitHub, back button to /
- **Detail pages (skill.html, strategy.html):** fetch from manifest + individual file from raw GitHub, copy-button for install command, code preview
- **Nav bar links:** Проекты (#projects), Навыки (/skills/), Стратегии (/strategies/), Open Source (#oss), Контакты (#about), GitHub (external)

## Mobile Hamburger Menu

Every page now has a side-slide menu for mobile:
- Trigger: hamburger button (3 spans, animates to X)
- Panel: position fixed, right side, 280px wide, transform translate
- Overlay: backdrop-filter blur, click to close
- Menu items: Главная, Проекты, Навыки, Стратегии, Open Source, Контакты, GitHub
- Desktop (>769px): force hidden with display:none!important

## User's Understanding of "Skills"

On geniok.ru, "Skills" ALWAYS means **AI Agent Skills Catalog** — a directory of installable skills for AI agents (Claude Code, Cursor, Copilot, etc.). NOT a personal technology stack.
