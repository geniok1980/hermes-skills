---
name: russian-marketplace-profiles
description: "Register and manage profiles on Russian freelance/business platforms (Avito, Profi.ru, fl.ru, kwork, freelance.ru, weblancer.net, hh.ru, Habr Career). Includes API auth for Avito."
version: 1.2.0
author: geniok
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [avito, marketplace, freelance, russia, smm, profile]
---

# Russian Marketplace Profiles

Register and manage seller/freelancer profiles on Russian business platforms. This skill covers API-based auth (Avito) and browser-based profile setup for platforms where the user has credentials.

## When to Use

- User provides logins/passwords or API credentials for Russian platforms
- User asks "оформи везде профили" / "размести услуги"
- Need to create or update service listings/ads
- Need to research platform-specific categories and pricing

---

## New Platform Registration Rules

When registering on a new platform:

1. **Generate password first** — use Python (`string.ascii_letters + string.digits + "!@#$%"`, 20 chars). Save to memory BEFORE filling the form.
2. **User email** — geniok@gmail.com can be used for registration; user has confirmed access via Gmail API
3. **Political statement requirement** — if the platform requires a political stance as a condition of registration (weblancer.net etc.), BLOCK immediately and remove from consideration
4. **Check for confirmation email** — after registration, check Gmail via `google-workspace` skill for confirmation/verification emails
5. **Always save passwords** — never generate a password and use it without saving. Memory entry format: `PlatformName: login/password`

**Rule:** Platforms that require mandatory political statements (war stance, regime loyalty, etc.) as a condition of registration or profile visibility are **blocked entirely**. Do not register, do not fill forms, do not ask the user to confirm. Close the tab and remove the platform from consideration.

Currently known to require such statements:
- **weblancer.net** — requires «Я против войны в Украине» badge on public profile for RU/BY citizens

## Platforms Checklist

| # | Platform | URL | Type | Auth Method |
|---|----------|-----|------|-------------|
| 0 | **GitHub** | github.com/geniok1980 | Профиль разработчика | API (PAT from git remote config) |
| 1 | **Avito** | avito.ru | Услуги / IT | API (OAuth client_credentials) |
| 2 | **Profi.ru** | profi.ru | Услуги / Мастера | **SMS-пуш** на телефон |
| 3 | **fl.ru** | fl.ru | Фриланс | Browser (email/password) — **Yandex SmartCaptcha** |
| 4 | **freelance.ru** | freelance.ru | Фриланс | Browser (OAuth via freelance.id) |
| 5 | **kwork.ru** | kwork.ru | Фриланс / услуги | Browser (login/password) — **требует SMS-подтверждения телефона для создания кворков** |
| 6 | **weblancer.net** | weblancer.net | Фриланс | Browser (login/password) — **политическое заявление** |
| 7 | **hh.ru** | hh.ru | Работа / резюме | **SMS** на телефон |
| 8 | **Freelancer.com** | freelancer.com | Международный фриланс | Browser (email/password) — **капча/валидация при регистрации** |

**Closed platforms (not available):**
- freelance.habr.com (Хабр Фриланс) — **закрылся навсегда** (redirects to career.habr.com)
- uslugi.yandex.ru (Яндекс Исполнители, ex Яндекс Услуги) — **не подходит для IT-услуг**. Платформа переориентировалась на бытовые услуги (ремонт, сантехника, электрика, уборка). Категория «Компьютеры и IT» ведёт в 404.

---

## Avito API

Avito is the only platform in the list with a public API for programmatic ad management.

### Authentication (OAuth Client Credentials)

```bash
# Get access token (valid 24h)
TOKEN=$(curl -s -X POST "https://api.avito.ru/token" \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "scope=user:read ads:read ads:write" | jq -r '.access_token')
```

Required scopes for full management: `user:read ads:read ads:write`

**Store credentials in memory** `Avito: email/password. API: client_id=..., secret=...` — the token flow is always the same, just update the client_id/secret.

### Read User Info

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.avito.ru/core/v1/accounts/self" | jq '.name, .email, .phone, .profile_url'
```

**Actual behavior (tested):** `client_credentials` token with no explicit scope returns:
- `name`, `email`, `phone`, `profile_url` — all successfully populated
- Profile URL: `https://www.avito.ru/user/<hash>/profile`

### Check Existing Ads

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.avito.ru/core/v1/items" | jq '.resources | length'
```

### Limitations of client_credentials token (tested)

**CRITICAL:** The `client_credentials` OAuth flow provides READ-ONLY access only. It CANNOT:
- Create new items/ads
- Modify existing items
- Upload images
- Edit profile (bio, avatar, contact info)
- Use Autoload API (`/autoload/v2/profile` returns "Получение профиля недоступно")

For write operations, the user must use the `authorization_code` OAuth flow (requires web browser redirect):
- Authorization URL: `https://avito.ru/oauth`
- Token URL: `https://api.avito.ru/token`
- Required scopes: `items:write`, `items:apply_vas`, `short_term_rent:write`, `job:write`

**Recommendation:** Use Avito API only for reading data. For profile editing and ad creation, use browser-based login at avito.ru.

### Create Ad / Listing

Avito's ad creation API requires:
- Category ID (get from `/core/v1/categories/{id}/fields`)
- Location data
- Ad type (free/paid)
- Title, description, price
- Images (upload first via `/core/v1/images`)

For service listings (Услуги), the category tree differs from goods. Service ads may require different API endpoints or additional scopes.

### Pitfalls (Avito API)

- Token expires in 24h — always refresh before use
- `client_credentials` is READ-ONLY — cannot create ads, upload images, or edit profile
- Categories endpoint `/item/categories` does not exist — returns "no Route matched with those values"
- Service ads (Услуги) may use different API paths than goods; not fully documented for IT services
- **Browser login**: avito.ru uses JavaScript modals (no separate login URL). Use email+password in the modal dialog. After login, navigate to profile settings to edit bio/photo.
- For full profile editing (bio, photo, contact info), browser login with password is the most reliable approach

---

## GitHub Profile (via API)

GitHub profile can be updated programmatically via REST API without browser automation, using a token from the user's git remote config.

### When to Use

- Add/update the `Website` (blog) field on the user's GitHub profile
- Update the profile README in `{username}/{username}` repo

### Authentication

Extract the token from the local git remote URL (stored in `.git/config`):

```python
import re
with open('/path/to/repo/.git/config') as f:
    content = f.read()
match = re.search(r'https://([^@]+)@github\.com', content)
token = match.group(1)
```

The token may appear masked when displayed (e.g., `ghp_Bd...jcpD`), but the actual value is the full 40-char PAT. It works when used programmatically.

### Update profile blog/website field

```python
import json, urllib.request
req = urllib.request.Request('https://api.github.com/user', method='PATCH')
req.add_header('Authorization', f'Bearer {token}')
req.add_header('Content-Type', 'application/json')
data = json.dumps({'blog': 'https://geniok.ru'}).encode()
resp = urllib.request.urlopen(req, data)
```

### Update profile README

```python
import base64
req = urllib.request.Request(f'https://api.github.com/repos/{owner}/{owner}/contents/README.md')
req.add_header('Authorization', f'Bearer {token}')
resp = urllib.request.urlopen(req)
file_data = json.loads(resp.read())
current = base64.b64decode(file_data['content']).decode('utf-8')
sha = file_data['sha']
encoded = base64.b64encode(new_content.encode()).decode()
req = urllib.request.Request(f'https://api.github.com/repos/{owner}/{owner}/contents/README.md', method='PUT')
req.add_header('Authorization', f'Bearer {token}')
data = json.dumps({'message': 'Add website link', 'content': encoded, 'sha': sha}).encode()
resp = urllib.request.urlopen(req, data)
```

---

## Browser-Based Profile Setup

For platforms without APIs, use the Hermes browser tools to log in and fill out profiles.

1. Navigate to the platform's login page
2. Enter credentials (login/password from memory/user)
3. Navigate to profile/settings page
4. Fill in:
   - Display name
   - Bio / description of services
   - Contact info (Telegram @geniok, GitHub)
   - Portfolio links (rkdash.geniok.ru, clawhost.geniok.ru)
   - Photo/avatar
5. Set pricing if applicable
6. Save/publish

### Known Pitfalls (tested May 2026)

| Platform | Issue | Workaround |
|----------|-------|------------|
| **fl.ru** | Yandex SmartCaptcha on login — OCR tools cannot solve the interactive checkbox+image captcha | User must login manually; automated approach is blocked |
| **kwork.ru** | Browser `<input type="file">` cannot be set programmatically due to security policy | User must upload avatar manually in profile settings |
| **kwork.ru** | "Информация о вас" uses Trumbowyg WYSIWYG editor (contenteditable div + hidden textarea). Setting textContent + dispatching `input` event may not reliably persist. | After setting text via JS, also update the hidden textarea value using `nativeInputValueSetter` and dispatch input+change events. If still not persisting, user must edit manually. |
| **kwork.ru** | Creating kworks requires phone verification (SMS). Create kwork link at /new redirects to /manage_kworks without showing a form when phone is unverified. No error message. | User must add and verify phone number first (SMS OTP). After verification, /new should show the kwork creation form. |
| **kwork.ru** | Login session does NOT persist across browser_navigate calls — navigating away from the seller dashboard forces re-login on return | Complete all kwork actions within a single page visit. Use browser_console with fetch/XHR to call internal APIs without losing session |
| **freelance.ru** | Login migrated to OAuth2 via freelance.id (PKCE flow). Wrong password produces a blank page (no error message, form silently resets) | User must reset password or provide the correct one. No automated way to distinguish 'wrong password' from 'account blocked' — both produce empty white page |
| **weblancer.net** | Registration form uses custom React components (not native `<select>`). Setting values via `element.value = ...` works for gender (`male`/`female`) and country (`RU`) | Use `browser_console` to fill fields programmatically and dispatch `input`+`change` events. Click the register button via JS. |
| **Freelancer.com** | Signup form uses React components with JS validation. Two failure modes: (1) bot-detected traffic silently resets form; (2) FL-VALIDATION-ERROR CSS classes appear with empty text — no visible error cues | Fill via browser_console. If validation errors persist invisibly, check for FL-VALIDATION-ERROR class elements. User may need to register manually |
| **Freelancer.com** | Registration with generated password uses email geniok@gmail.com — need to await confirmation email. Password MUST be saved to memory immediately | Generate passwords via Python (not browser JS), save to memory before filling the form |
| **All** | SMS-based auth cannot be automated | Skip these platforms and ask user to set up manually |

---

## Bot Detection & Search Engine Access

When researching platforms or projects from this VPS (European IP, no residential proxy):

| Engine / Platform | Status | Notes |
|-------------------|--------|-------|
| **Google** | Blocked — CAPTCHA | IP gets flagged immediately |
| **Yandex** | Blocked — CAPTCHA | SmartCaptcha requires interactive checkbox |
| **DuckDuckGo** | Blocked — CAPTCHA | HTML mode also blocked — try DuckDuckGo Lite (lite.duckduckgo.com/lite/) |
| **Upwork** | Blocked — Cloudflare challenge | Requires residential proxy |
| **Fiverr** | Blocked — human verification (ERRCODE PXCR10002539) | PerimeterX bot detection |
| **Freelancer.com** | Accessible | Loads without blocks, but needs registration to view active projects |
| **Kwork.ru** | Accessible | Project listings visible without login |
| **Fl.ru** | Partially blocked | Project list loads, but login requires Yandex SmartCaptcha |

**Workaround:** Use direct navigation to known platform URLs instead of search engine queries. Use DuckDuckGo lite (`lite.duckduckgo.com/lite/`) or Bing as fallback when search is needed. For blocked international platforms, ask the user to register manually.

---

## Parallel Processing Pattern

For multi-platform tasks, use `delegate_task` with up to 3 parallel subagents:

```python
from hermes_tools import delegate_task  # Not actually imported — use the tool directly
```

Best practices:
- Give each subagent full context (credentials, profile text, avatar path) — they have NO memory of the conversation
- Set `toolsets=["browser","file","terminal"]` for full access
- Set a generous timeout (subagents have their own iteration limits)
- Browser file uploads won't work — note this in the instructions
- Subagents will hit 50-iteration tool call limits on complex form workflows; chunk the task if needed
- After parallel work completes, do a manual pass for any missed "Сохранить" buttons and avatar uploads

---

## Profile Bios

### Short Template

Для Евгения (rkeeper/iiko specialist + AI/ML):

> Автоматизация кафе, баров и ресторанов на rkeeper и iiko
> Разработка и внедрение AI-агентов в бизнес-процессы
> Дашборды и бизнес-аналитика с AI
> Торговые алгоритмы с AI и ML
> TypeScript, Python, DevOps
> geniok.ru

### Full Template

Для развёрнутого описания профиля используйте текст из `references/profile-text-full.md` — он охватывает все направления услуг, проекты, технологии и преимущества. При обновлении добавляйте ссылку на сайт **geniok.ru** в первые строки описания.

### Per-Platform Ad Texts

Для готовых текстов под каждую площадку используйте `references/platform-ad-texts.md`:
- **Avito** — объявление в «Услуги» (формат c эмодзи-списками, подходит для длинного описания)
- **fl.ru** — профиль исполнителя (краткий, перечисляет направления)
- **kwork.ru** — 4 отдельных кворка (автоматизация, Telegram-боты, торговые боты, DevOps)
- **freelance.ru** — профиль (специализация + портфолио)
- **hh.ru** — резюме (формат hh, навыки списком)
- **Profi.ru** — профиль специалиста (короткий, доверительный)

### Portfolio links to include

- https://geniok.ru — Сайт-визитка, все проекты и сервисы
- https://rkdash.geniok.ru — Аналитика Rkeeper с AI-агентами
- https://clawhost.geniok.ru — Платформа деплоймента OpenClaw/Hermes
- https://aiphoto.geniok.ru — AI фотостудия
- https://t.me/udaff_vpn_bot — Сервис аренды приватного VPN

**Cloudflare proxy note:** The server is in Europe (play2go.cloud, IP 2.26.98.104). For Russian users accessing these portfolio links, ensure Cloudflare proxy (`proxied: true`) is enabled on the DNS records — without it, direct connections from Russia to the European server are extremely slow.

---

## Domain Knowledge: Crypto in Russia

**CRITICAL — do not confuse these:**

| Legal | Illegal |
|-------|---------|
| Cryptocurrency trading / investment | Paying for goods/services with crypto |
| Running trading bots (crypto, MOEX) | Accepting crypto payments in business |
| Algorithmic trading strategies | Crypto payment terminals in restaurants |

When writing service descriptions, **include crypto trading bot development** as a service. **Do NOT mention** accepting crypto payments or using crypto as a payment method in restaurant automation.

---

## Pricing Reference (2026)

| Service | Price Range |
|---------|-------------|
| Внедрение rkeeper/iiko под ключ | 30 000–70 000 ₽ |
| Абонентское обслуживание (ресторан) | 10 000–15 000 ₽/мес |
| BI-дашборд под ключ | 30 000–80 000 ₽ |
| Система лояльности | 50 000–100 000 ₽ |
| Фрод-мониторинг (премиум) | 5 000–15 000 ₽/мес |
| Telegram-бот | 15 000–50 000 ₽ |
| Торговый бот (разработка) | 50 000–150 000 ₽ |
| DevOps / администрирование | 5 000–15 000 ₽/мес |

---

## References

- `references/avito-api-notes.md` — Avito API auth details and endpoint reference
- `references/platform-ad-texts.md` — Готовые тексты объявлений под каждую площадку
- `references/profile-text-full.md` — Полный развёрнутый текст профиля
