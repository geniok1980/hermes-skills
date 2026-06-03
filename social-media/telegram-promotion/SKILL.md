---
name: telegram-promotion
description: Promote technical/crypto services on Telegram — find relevant groups, create a channel, post content strategy, convert followers to clients.
---

# Telegram Promotion for Technical & Crypto Services

## Trigger

Load this skill when the user needs to:
- Find Telegram channels/groups in a niche (crypto, AI, Freqtrade, HoReCa automation)
- Create a Telegram channel for content marketing
- Plan content and posting strategy for a Telegram channel
- Promote Freqtrade strategies, AI agents, HoReCa automation services on Telegram
- Set up recurring content delivery via cron jobs

## Finding Relevant Telegram Channels

### Method 1: Aggregator articles
Niche aggregators (vc.ru, Habr, TGStat) publish curated lists of Telegram channels.

For crypto specifically:
1. Search `vc.ru/crypto` for articles like "150+ Telegram каналов про криптовалюты"
2. Find the relevant category section (e.g., "Крипто трейдинг и сигналы")
3. Extract t.me links with JS in browser console:
   ```js
   [...document.querySelectorAll('a')]
     .filter(a => a.href && a.href.includes('t.me'))
     .map(a => a.href.split('?')[0] + ' — ' + a.textContent.trim())
     .join('\n')
   ```
   (vc.ru uses redirect wrapper, but the real `t.me/xxx` is in the `to` param)

### Method 2: TGStat / tgram.io
- [TGStat](https://tgstat.ru) — Russian platform, category browsing
- [tgram.io](https://tgram.io) — international channel catalog

### Method 3: Telegram search
- Search Telegram's global search by keyword
- Look for related channels in existing group descriptions

## Creating a Telegram Channel

Agent cannot create Telegram channels via available tools. User must do it manually:

1. Telegram → Menu (☰) → Create Channel
2. Choose a name reflecting your services (e.g., "Freqtrade Strategies by Geniok")
3. Write a clear description: what you offer, your expertise, link to your site/github
4. Set profile photo and public link (t.me/yourchannel)
5. Pin a welcome message with your offer

## Content Strategy

### In other groups (outreach — don't spam)
- Give value before selling: answer questions, share insights
- When appropriate, offer your service concretely:
  > "Напишу/доработаю стратегию под Freqtrade. Бектесты, оптимизация, подключение. Любая биржа. 5000₽ за стратегию."
- Include results/portfolio as proof
- Don't post the same message in every group — adapt to each community's vibe

### In your own channel (content)
- Post your best strategies with backtest results (equity curves, stats)
- Share market analysis and trade ideas (builds authority)
- Case studies: how a strategy performed, what was optimized
- Cross-promote your other competencies (AI agents, HoReCa automation)
- Offer limited free spots to build social proof
- **First post**: use `templates/first-post.md` for the pinned welcome message — includes bio, expertise, and links to site/GitHub
### Automation (cron jobs)

Set up daily cron jobs to:
- Send you a plan to earn 10 000₽/day at 10:00 (see cron-jobs skill)
- Reminders for personal habits (no alcohol, workout) — morning + evening
- Cross-post content if you have a multi-platform strategy
- Post recurring content directly to your Telegram channel (use `deliver='telegram:-100xxxxxxxxx'` with the channel's chat ID)

## Connecting Agent to Channel (Post-Creation)

After the user creates a Telegram channel and adds your bot as admin:

### 1. Discover Bot Username

```bash
source /root/.hermes/.env 2>/dev/null
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"
```

### 2. Get Channel Chat ID

**⚠️ Known issue**: The `getUpdates` API method often returns empty because the Hermes Telegram platform consumes updates before raw API calls can see them. Do NOT waste time debugging this.

**Reliable method: Ask the user for the numeric ID directly.**
The user can find the channel's numeric ID by:
- Forwarding any message from the channel to `@getidsbot` on Telegram
- Opening the channel in Telegram Web (web.telegram.org) and checking the URL
- Opening channel info → checking for a public @username (convert to ID if possible)
- Asking a friend in the channel to forward a message to `@getidsbot`

Chat IDs for private channels always start with `-100` followed by 10 digits (e.g., `-1003896078901`).

**Plan B (if bot was recently added and platform is idle):**
Ask the user to send a message in the channel, then immediately:

```bash
source /root/.hermes/.env 2>/dev/null
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates"
```

If this returns empty, the Hermes platform already consumed the update — fall back to the reliable method above.

### 3. Test the Chat ID

Once you have a candidate ID, test it immediately:

### 3. Configure Delivery to Channel

Once you have the chat ID (e.g., `-1001234567890`):

- **Cron jobs**: set `deliver='telegram:-1001234567890'`
- **One-time posts**: `send_message(target='telegram:-1001234567890', message='...')`

## Content Approval Workflow (Plan → Email → Publish)

When the user wants structured content published to their channel:

1. **Prepare a content plan** — agenda of topics, posting cadence, target audience
2. **Send plan via email** for user approval:
   - Use himalaya CLI (if configured) or Hermes email gateway
   - To: user's email (e.g., geniok@gmail.com)
   - Subject: clear proposal label
3. **Wait for user approval** — do NOT publish until they explicitly confirm
4. **Publish approved content** via:
   - `send_message(target='telegram:-100XXXXXXXXX', message='...')` — one-off posts
   - cron jobs with `deliver='telegram:-100XXXXXXXXX'` — recurring auto-posts

### Email Setup for Approval

**Option A: Gmail App Password (Simple)**
- Install himalaya: `curl -sSL https://raw.githubusercontent.com/pimalaya/himalaya/master/install.sh | PREFIX=~/.local sh`
- Configure SMTP in `~/.config/himalaya/config.toml` with user's Gmail + App Password
- For Gmail with 2FA, user must create an App Password at https://myaccount.google.com/apppasswords
- Example `~/.config/himalaya/config.toml`:
  ```toml
  [accounts.gmail]
  email = "geniok@gmail.com"
  display-name = "Evgeniy"
  default = true

  backend.type = "imap"
  backend.host = "imap.gmail.com"
  backend.port = 993
  backend.encryption.type = "tls"
  backend.login = "geniok@gmail.com"
  backend.auth.type = "password"
  backend.auth.cmd = "echo APP_PASSWORD_HERE"

  message.send.backend.type = "smtp"
  message.send.backend.host = "smtp.gmail.com"
  message.send.backend.port = 587
  message.send.backend.encryption.type = "start-tls"
  message.send.backend.login = "geniok@gmail.com"
  message.send.backend.auth.type = "password"
  message.send.backend.auth.cmd = "echo APP_PASSWORD_HERE"

  folder.aliases.inbox = "INBOX"
  folder.aliases.sent = "[Gmail]/Sent Mail"
  folder.aliases.drafts = "[Gmail]/Drafts"
  folder.aliases.trash = "[Gmail]/Trash"
  ```

**Option B: Gmail OAuth 2.0 (No Password Needed)**
If the user has a `client_secret_*.json` file from Google Cloud Console, use the OAuth manual console flow:

1. Save the client_secret JSON to a known path (e.g., `/root/gmail-client-secret.json`)
2. Use the Python manual OAuth flow (see `references/gmail-oauth.md` for the full script)
3. The flow: generate auth URL → user opens in browser → user pastes redirect URL back → exchange code for tokens → save tokens
4. Use the saved tokens with Gmail API for sending emails

Advantage: no app password to manage, works with any 2FA.

### Sending the content plan

```bash
cat << 'EOF' | himalaya template send
From: geniok@gmail.com
To: geniok@gmail.com
Subject: Контент-план: [тема]

План на утверждение:
1. ...
2. ...
EOF
```

## Channel vs DM Delivery

**IMPORTANT** — user preference: personal cron jobs (reminders, daily plans) deliver to the user's DM (`origin`), NOT to the Telegram channel. The channel is only for published content (articles, tips, announcements). Never send habit reminders or personal daily plans to the channel unless explicitly asked.

## Editing Published Posts

After a post is published to the channel, the user may ask to edit it. Use the Telegram Bot API `editMessageText` method:

```bash
source /root/.hermes/.env 2>/dev/null
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/editMessageText" \
  -d "chat_id=-100XXXXXXXXX" \
  -d "message_id=N" \
  -d "text=New text here"
```

- Get the `message_id` from the `send_message` response
- The bot must be an admin in the channel
- For Cyrillic text, encode via Python rather than shell to avoid encoding issues

## Cross-Platform Presence

When the user wants to expand beyond Telegram, help them set up:

1. **VK (VKontakte)**: User creates a group at vk.com/groups?act=create manually. Set it to public (not closed). Add description matching the Telegram channel bio.
2. **YouTube**: User creates a channel at youtube.com (via their Google account). Use the same name and branding as Telegram for consistency.
3. **Content sync**: Post the same core content across all platforms, but adapt format per platform (Telegram = short text, VK = longer posts, YouTube = video).

## Content Automation Ideas

- **Content series**: schedule posts about AI agents, Freqtrade strategies, case studies
- **Daily tip**: post a Freqtrade strategy tip at a fixed time  
- **Cross-promote**: notify channel when you post on YouTube/Medium

## Channels for Freqtrade / Crypto Services

See `references/crypto-channels.md` for a categorized list of 60+ Telegram channels.

### Quick picks (most relevant for promoting bot/strategy services):
- **Job/Work**: holder_job_devs, work2earn_crypto
- **Trading**: Cr_ideas, proscalping_trade, sttrade88  
- **Communities**: cryptophilos, cryptochyvak, CryptoAmbitions

## Conversion Tactics
- Lead with a free mini-service (5-min consultation, one free backtest) → upsell to paid strategy
- Show real results: PnL screenshots, backtest stats
- Price transparently and competitively
- Redirect traffic to your Telegram channel for ongoing content
- Collect testimonials from first clients

## Pitfalls
- **Don't spam** the same message in 10 groups — you get banned
- **Don't over-promise** — crypto is volatile, no strategy is 100%
- **Don't ignore DMs** — quick replies = more conversions
- **Don't post without proof** — screenshots or GitHub repos build trust
