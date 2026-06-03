---
name: portfolio-landing-maintenance
description: Maintain and edit a static HTML portfolio landing page served by Caddy, including section creation, style research from reference sites, sub-page architecture, and GitHub integration for backups and dynamic data sources.
category: software-development
triggers:
  - "обновить лендинг"
  - "добавить на сайт"
  - "добавить услуги"
  - "добавить курсы"
  - "изменить секцию на лендинге"
  - "создать страницу на geniok.ru"
  - "поменять дизайн лендинга"
  - "добавить навыки на сайт"
  - "добавить стратегии"
  - "каталог навыков"
  - "каталог стратегий"
  - "мобильное меню"
  - "гамбургер"
---

# Portfolio Landing Page Maintenance

## Context

This skill covers maintaining a static HTML/CSS portfolio landing page hosted via Caddy file_server. The user's site is at geniok.ru, served from `/var/www/geniok/`.

## Key User Preferences

### Mobile Navigation: Hamburger & Side Menu

On mobile (< 768px), ALL pages must have:
- A hamburger button (three stacked spans) in the top-bar/nav
- A side-menu panel that slides in from the right (position: fixed, right: 0, transform: translateX(100%) → 0)
- A semi-transparent overlay behind the side menu (backdrop-filter: blur)
- The hamburger animates to an X when open (rotate spans)
- body overflow: hidden when menu is open
- Click overlay or menu link → close menu

The side menu must include ALL nav items: Главная, Проекты, Навыки, Стратегии, Open Source, Контакты, GitHub. On the main page, the desktop nav links are hidden on mobile via `display: none` and only the hamburger shows. Desktop (>= 769px) must force side menu hidden via `display: none !important`.

### Catalog Page Architecture

When creating a catalog/directory page (Skills, Strategies, etc.):

1. **Separate sub-page** — `/var/www/geniok/<section>/index.html`, NOT embedded in index.html
2. **Dynamic data** — fetch from `raw.githubusercontent.com/owner/repo/main/manifest.json` via async JS
3. **Search + filter** — search input + category filter buttons with active state
4. **Detail pages** — `/section/thing.html?name=xxx` pattern, NOT separate HTML files per item
5. **Install section** — every detail page has a code block with copy button
6. **Back button** — a `back-btn` in the top-bar that links to the parent catalog

### Detail Page Pattern (thing.html?name=xxx)

Each detail page follows this structure:
- Top-bar with back button to parent catalog + logo + hamburger
- Tags row (category, status, AI/ML badges)
- Title + description
- Meta cards grid (4-6 cards: author, category, timeframe, pairs, status, repo, etc.)
- Install section: code block + copy button + GitHub link
- Optional content section (code preview from raw GitHub, extra notes)
- Info section
- Footer

The JS flow: get `?name=` from URL → fetch manifest.json → find matching item → render full HTML. Also try to fall back to path parsing for cleaner URLs.

### "Skills" = AI Agent Skills Catalog, NOT Personal Tech Stack

**CRITICAL PITFALL:** When the user says "Skills" or "навыки" on their landing page, they mean a **catalog of skills for AI agents** (like neuraldeep.ru/skills) — not a "my technology stack" section. Do NOT create a personal tech-stack grid. The correct interpretation:

- ✅ A directory of installable skills for agents (Claude Code, Cursor, Copilot, etc.)
- ❌ A grid of "Languages: TypeScript, Python, React" with proficiency levels

### Architecture Preferences

- **Separate pages for separate content.** Major sections (like Skills) should live on their own sub-page (/skills/), not embedded in the main index.html. The main page gets a link/banner pointing to the sub-page.
- **Back button on sub-pages.** Every sub-page should have a prominent "На главную" button at the top.
- **Dynamic data from GitHub.** Skills and similar catalog content should be fetched live from a GitHub repo (raw.githubusercontent.com), not hardcoded in the HTML. This allows adding/removing items without editing the page.

### Design Style

The landing uses a dark theme:
- Background: #0a0a0f, Cards: #1a1a28 (section cards) or #18181b (table rows)
- Accent: #7c5cfc (purple), Accent2: #5c9cfc (blue)
- Borders: #2a2a3e or #27272a
- Text: #e8e8f0, muted: #8888aa
- Font: Inter (Google Fonts)
- Shimmer shine effect on hover (linear-gradient overlay with translate transform)
- Neuraldeep.ru/skills is the reference for the Agent Skills catalog style

## Working with the Landing Page

### File Structure

```
/var/www/geniok/
├── index.html              # Main portfolio page
├── skills/
│   ├── index.html          # Skills catalog (AI agent skills)
│   └── skill.html          # Skill detail page (?name=xxx)
└── strategies/
    ├── index.html          # Strategies catalog (Freqtrade)
    └── strategy.html       # Strategy detail page (?name=xxx)
```

Caddy config for geniok.ru uses `file_server` with root `/var/www/geniok` — any file/directory under it is served automatically.

### Typical Workflow

1. **Research reference site** — use browser tools to examine design, colors, layout of the inspiration site
2. **Edit the HTML/CSS** — patch the relevant file(s) locally
3. **Verify** — open the page in browser to check
4. **Backup** — push changes to the private backup repo (geniok1980/geniok-landing)
5. **Deploy** — scp files to server: `sshpass -p "20Upiter17!" scp index.html root@2.26.98.104:/var/www/geniok/`
6. **Verify live** — `curl -sI https://geniok.ru/ | grep last-modified`

### GitHub Repos

- **geniok1980/geniok-landing** — PRIVATE. Backup of the entire landing page. Contains index.html, skills/, strategies/, and all sub-pages.
- **geniok1980/Skills** — PUBLIC. Skills catalog for AI agents. Contains skills.json (manifest) and per-skill SKILL.md files. The /skills/ page fetches skills.json from `raw.githubusercontent.com/geniok1980/Skills/main/skills.json`.
- **geniok1980/Freqtrade-Strategies** — PUBLIC. Freqtrade trading strategies. Contains strategies.json (manifest) and per-strategy .py files. The /strategies/ page fetches from `raw.githubusercontent.com/geniok1980/Freqtrade-Strategies/main/strategies.json`.

### Deployment

After editing files in the geniok-landing backup repo, deploy to the live server:

```bash
# Server: 2.26.98.104 (Prod1.play2go.cloud)
# Web root: /var/www/geniok/
# SSH password: общий пароль из памяти (20Upiter17!)

# SCP the changed file(s)
sshpass -p "20Upiter17!" scp -o StrictHostKeyChecking=no \
  index.html root@2.26.98.104:/var/www/geniok/index.html

# For sub-pages
sshpass -p "20Upiter17!" scp -o StrictHostKeyChecking=no \
  -r skills/ root@2.26.98.104:/var/www/geniok/
```

Verify deployment:
```bash
# Check last-modified header
curl -sI https://geniok.ru/ | grep -i last-modified

# Check for specific content
curl -s https://geniok.ru/ | grep -o 'YourContent' | head -1
```

### Adding a New Open Source Card

1. If the project's actual code is in a **private** repo, create a new **public showcase repo** first (see `github-repo-management` skill — "Public Showcase Repo for a Private Project"). Do NOT make the private repo public.
2. Add HTML inside the `#oss` section's `.grid`, following the existing card pattern
3. The `href` must point to the **public** showcase repo — never to a private repo
4. Update the hero stats counter if adding a net-new project
5. Push changes to geniok-landing repo
6. Deploy: `sshpass -p "20Upiter17!" scp -o StrictHostKeyChecking=no index.html root@2.26.98.104:/var/www/geniok/index.html`
7. Verify: `curl -sI https://geniok.ru/ | grep -i last-modified`

Card pattern:
```html
<!-- project-name -->
<a href="https://github.com/geniok1980/project-name" class="card" target="_blank">
  <div class="card-top">
    <div class="card-name">BrandName</div>
    <div class="card-status status-oss">OSS</div>
  </div>
  <div class="card-desc">🤖 One-line description with emoji prefix.</div>
  <div class="card-tags">
    <span class="card-tag py">Python</span>
    <span class="card-tag fastapi">FastAPI</span>
    <span class="card-tag docker">Docker</span>
  </div>
  <div class="card-links">
    <span class="card-link">GitHub <span class="arrow">→</span></span>
  </div>
</a>
```

### Adding a Live Service Card

When a project has a **live dashboard** on a subdomain with its own server:

```html
<!-- project-name -->
<a href="https://subdomain.geniok.ru" class="card" target="_blank">
  <div class="card-top">
    <div class="card-name">BrandName</div>
    <div class="card-status status-live">LIVE</div>
  </div>
  <div class="card-desc">🤖 Same description, linking to live service.</div>
  <div class="card-tags">
    <span class="card-tag py">Python</span>
    <span class="card-tag fastapi">FastAPI</span>
    <span class="card-tag docker">Docker</span>
  </div>
  <div class="card-links">
    <span class="card-link">subdomain.geniok.ru <span class="arrow">→</span></span>
  </div>
</a>
```

Card lives in the `#projects` section's `.grid`.

### Two-Card Pattern: LIVE + OSS

**If a project has BOTH a live dashboard and public source code**, create TWO cards:

1. **PROJECTS section** (`#projects`) — LIVE badge, link to live subdomain
2. **OPEN SOURCE section** (`#oss`) — OSS badge, link to GitHub repo

This is the user's explicit preference — do NOT collapse into one card or prefer one over the other. Both sections get a card with different links and different badges.

```html
<!-- In #projects .grid: -->
<a href="https://subdomain.geniok.ru" class="card" target="_blank">
  <div class="card-top">
    <div class="card-name">BrandName</div>
    <div class="card-status status-live">LIVE</div>
  </div>
  <div class="card-desc">🤖 Live service description.</div>
  <div class="card-tags">....</div>
  <div class="card-links">
    <span class="card-link">subdomain.geniok.ru <span class="arrow">→</span></span>
  </div>
</a>

<!-- In #oss .grid (among other OSS projects, not necessarily adjacent): -->
<a href="https://github.com/geniok1980/repo-name" class="card" target="_blank">
  <div class="card-top">
    <div class="card-name">BrandName</div>
    <div class="card-status status-oss">OSS</div>
  </div>
  <div class="card-desc">🤖 Исходный код — brief source code description.</div>
  <div class="card-tags">....</div>
  <div class="card-links">
    <span class="card-link">GitHub <span class="arrow">→</span></span>
  </div>
</a>
```

### Updating Hero Stats

After adding/removing a card, update the hero section stats:

```html
<div class="stats">
  <div class="stat-item">
    <div class="stat-num">6</div>
    <div class="stat-label">Open Source проектов</div>
  </div>
  <div class="stat-item">
    <div class="stat-num">6</div>
    <div class="stat-label">Live-сервиса</div>
  </div>
  ...
</div>
```

Count OSS projects (cards in `#oss .grid`) and live services (cards in `#projects .grid`) separately. Both usually increase together for a project with both a live dashboard and public code.

### Setting Up a Live Subdomain for a New Project

When a project needs a live dashboard subdomain (separate server, not the landing server):

1. **Check the target server** — `sshpass -p "20Upiter17!" ssh -o ConnectTimeout=5 root@SERVER_IP "docker ps --format '{{.Names}} {{.Ports}}'"` to find the service port
2. **Install Caddy** if missing — `sshpass -p "20Upiter17!" ssh root@SERVER_IP "apt-get update -qq && apt-get install -y caddy"`
3. **Write Caddyfile** — reverse_proxy localhost:SERVICE_PORT
4. **Reload Caddy** — `caddy reload --config /etc/caddy/Caddyfile`
5. **Add Cloudflare DNS A record** with `proxied: true` — use Python script (more reliable than shell, avoids token quoting issues)
6. **Verify** — `curl -sI https://subdomain.geniok.ru/ | head -5`

See `cloudflare-dns-caddy-proxy` skill for full DNS/Caddy workflow details.

### Public Showcase Repo for a Private Project

When the actual code lives in a **private** repo and you need a public repo for the landing page:

1. **Do NOT make the private repo public** — this would expose API keys, config, and real code
2. **Create a new public repo** via GitHub API with `auto_init: true`:
   ```python
   import urllib.request, json
   token = open('/tmp/ghtoken.txt').read().strip()
   req = urllib.request.Request(
       'https://api.github.com/user/repos',
       data=json.dumps({"name": "repo-name", "description": "...", "private": False, "auto_init": True}).encode(),
       headers={'Authorization': f'token {token}', 'Content-Type': 'application/json'},
       method='POST'
   )
   ```
3. **Get the auto-generated README SHA** — `GET /repos/owner/repo/contents/README.md`
4. **Push the full README** via PUT with the SHA
5. **Add the landing card** linking to the new public repo

The README should describe architecture, features, quick start, and tech stack — but not include any real credentials, API keys, or internal configuration details.

### Adding a New Section to Main Page

1. Add CSS styles inside the existing `<style>` block (before the `@media` section)
2. Add HTML section between existing sections
3. Add nav link in the `<nav .links>` section
4. Add side menu link in the side-menu
5. Update stats counters if applicable

### Course Section Pattern (Банеры курсов)

**CRITICAL PREFERENCE:** Courses on the landing page are BANNER CARDS (name + description + tags), NOT full embedded lessons. Full lesson content lives on a separate learning platform.

The pattern:

```html
<!-- Courses -->
<section class="section" id="courses">
  <div class="section-label">/ COURSES</div>
  <h2>Обучающие курсы</h2>
  <p class="subtitle">Краткое описание секции.</p>
  <div class="grid">
    <div class="card" style="cursor:pointer" onclick="window.open('https://t.me/geniok','_blank')">
      <div class="card-top">
        <div class="card-name">📈 Название курса</div>
        <div class="card-status status-live">NEW</div>
      </div>
      <div class="card-desc">Описание курса: что входит, количество уроков, результат.</div>
      <div class="card-tags">
        <span class="card-tag">Tag1</span>
        <span class="card-tag">Tag2</span>
      </div>
      <div class="card-links">
        <span class="card-link">Подробнее в Telegram <span class="arrow">→</span></span>
      </div>
    </div>
  </div>
</section>
```

Course cards use the base `.card` class (same as projects), NOT `.service-card` — no price display, no feature list, no CTA button. Instead: `status-live NEW` badge, tags, and a Telegram link.

Nav link: `<a href="#courses" class="nav-link">Курсы</a>`
Side menu: `<a href="#courses"><span class="icon">🎓</span> Курсы</a>`

Do NOT embed module/lesson content in the landing page. The landing page is a storefront; the platform is the delivery.

### Service Section Pattern (Услуги)

For a Services/Услуги section with price cards:

1. **CSS** — add `.card.service-card`, `.service-price`, `.service-features`, `.service-cta` styles:
   ```css
   .card.service-card { cursor: default; }
   .card.service-card:hover { transform: none; }
   .card .service-price { font-size: 20px; font-weight: 800; color: var(--green); margin-bottom: 12px; }
   .card .service-price span { font-size: 13px; font-weight: 500; color: var(--text2); }
   .card .service-features { list-style: none; padding: 0; margin: 0 0 16px; flex: 1; }
   .card .service-features li { font-size: 13px; color: var(--text2); padding: 4px 0; display: flex; align-items: center; gap: 8px; }
   .card .service-features li::before { content: "✦"; color: var(--accent); font-size: 10px; }
   .card .service-cta { display: inline-flex; align-items: center; gap: 8px; padding: 10px 20px; border-radius: 8px; background: linear-gradient(135deg, var(--accent), var(--accent2)); color: #fff; font-size: 13px; font-weight: 700; text-decoration: none; transition: all .3s; align-self: flex-start; }
   .card .service-cta:hover { box-shadow: 0 4px 20px rgba(124,92,252,.4); transform: translateY(-1px); }
   ```
2. **HTML section** — insert between existing sections using `id="services"`:
   ```html
   <section class="section" id="services">
     <div class="section-label">/ SERVICES</div>
     <h2>Мои услуги</h2>
     <p class="subtitle">...</p>
     <div class="grid">
       <div class="card service-card">
         <div class="card-top"><div class="card-name">🏪 Название услуги</div></div>
         <div class="service-price">от 20 000 ₽ <span>под ключ</span></div>
         <ul class="service-features">
           <li>Пункт 1</li>
           <li>Пункт 2</li>
         </ul>
         <a href="https://t.me/geniok" class="service-cta" target="_blank">Заказать <span class="arrow">→</span></a>
       </div>
     </div>
   </section>
   ```
3. **Nav** — add `<a href="#services" class="nav-link">Услуги</a>` and side-menu equivalent
4. Cards use `.card` base styles same as project/oss cards, with `service-card` override to disable hover lift

### Creating a New Sub-page

1. Create directory: `mkdir -p /var/www/geniok/<page>/`
2. Create `index.html` with its own styles and back link to /
3. Add link from main page (nav or prominent button)

## Pitfalls

- **"Skills" misinterpretation**: The first instinct is to make a "my skills" grid. RESIST. This user means AI Agent skills catalog.
- **Private→Public disaster**: When the user asks to create a public repo for a project that already exists as private, do NOT make the private repo public. Create a NEW separate public showcase repo with documentation only. Making the private repo public exposes real code, API keys, and config.
- **Embedding catalogs in main page**: A full catalog with 96+ items should be a separate page, not embedded in index.html. The main page gets a link.
- **Hardcoding skills data**: Skills should come from the GitHub repo dynamically, not hardcoded in HTML. Use fetch() to load skills.json.
- **Inline onclick on filter buttons**: Use addEventListener via DOMContentLoaded, not onclick attributes. They conflict and cause errors when the global function isn't defined.
- **Caddy file_server**: No special routing needed — just create the file/directory and Caddy serves it. No need to restart Caddy.
- **Mobile menu on desktop**: Force-hide side menu at >= 769px with display: none !important to prevent flash when resizing.
- **Detail page back button**: Must link to parent catalog (/skills/, /strategies/), not to generic geniok.ru.
- **Hamburger position**: On sub-pages, hamburger goes in the top-bar between logo and repo-link. Keep z-index above overlay (1001).
- **Landing card links**: Every card's href must point to a PUBLIC URL — either a public GitHub repo or a live subdomain. Never link to private repos from the landing page. If the project has both a live dashboard and a public repo, prefer linking to the live dashboard.
- **Rename, don't remove, compliance-sensitive cards**: When a service name is problematic (VPN, DMCA, etc.), do NOT delete the card — rename it preserving the card structure and icon. Update `card-name`, `card-desc`, and `card-tag` text; keep the rest (layout, link, icon/emoji) intact. Example: UDAFF VPN → UDAFF OPENSOURCE, tag from VPN → OpenSource. The user prefers evolution over deletion.

## See Also

- `web-design-recovery` — for extracting design tokens (colors, fonts, layout) from reference websites to guide the page's visual style
- `cloudflare-dns-caddy-proxy` — for DNS setup, Caddyfile configuration, and SSL/Cloudflare proxy settings (used behind the scenes)
- `bun-docker-deploy` — for deploying Next.js apps in Docker (used for rkdash landing page behind Caddy proxy)
- `references/nextjs-landing-patterns.md` — Next.js + Tailwind CSS v4 landing page patterns used for rkdash.geniok.ru (dark theme, pricing cards, AI chat mock, mobile nav)
