# Crawl4AI Script References

## 1. Earnings Digest (утренняя подборка заработка)

**Location:** `/root/.hermes/scripts/earnings-digest.py`
**Also mirrored at:** `crawl4ai-env` venv, referenced in web-scraping skill.

**Purpose:** Daily crawl of hh.ru for job vacancies matching user's profile (rkeeper, Python, trading bots, DevOps, Telegram bots). Outputs structured markdown digest.

**Key patterns:**
- AsyncWebCrawler for JS-rendered content
- Keyword filtering on extracted markdown lines
- Salary extraction from ₽-containing lines
- Cron job runs with `no_agent=True` at 04:30 Samara time

**Target URLs:** 6 hh.ru search queries with Cyrillic query params

**Output format:**
```
📅 Утренняя подборка — DD.MM.YYYY

🔥 rkeeper / Автоматизация ресторанов:
  — [vacancy description]
  💰 Зарплаты:
    • 90 000 – 110 000 ₽
```

## 2. rkeeper Docs Crawler (single product)

**Location:** `/root/.hermes/scripts/crawl-rkeeper-docs.py`

**Purpose:** Crawl entire Confluence documentation site for ONE product (r_keeper 7), save each page as .md with Obsidian frontmatter, upload via WebDAV.

**Key patterns:**
- One-pass BFS: discover + extract in single crawl per page
- WebDAV upload via `curl -T` (more reliable than heredoc)
- Obsidian frontmatter: `title:`, `source:`, `date:`
- Index page with `[[docs/filename|Title]]` wikilinks

**Target:** `https://docs.rkeeper.ru/rk7/latest/ru/r_keeper-7-1146927.html`
**Typical size:** 150+ pages, ~4 MB

**Obsidian folder:** `rkeeper-docs/rk7/`
**WebDAV base:** `https://webdav.yandex.ru/Obsidian%20Vault/rkeeper-docs/rk7`

**Pitfalls encountered:**
- WebDAV heredoc upload (`curl -T - << EOF`) unreliable via asyncio subprocess — use file-based upload (`curl -T /path/to/file`)
- Confluence links require Playwright (curl can't see JS-rendered hrefs)
- crawl4ai renders links as markdown `[text](url)`, not HTML `href="url"`

## 3. Full rkeeper Knowledge Base Crawler (multi-product)

**Location:** `/root/.hermes/scripts/crawl-rkeeper-full.py`
**Also mirrored at:** `crawl4ai` skill's `references/full-site-crawl.py`

**Purpose:** Crawl ALL products on the entire docs.rkeeper.ru domain. Saves each page into a product-specific subdirectory (rk7/, license/, sh5/, delivery/, webman/, cloud/, kds/, kiosk/, crm/, etc.) and uploads to Obsidian with matching folder structure.

**Key patterns vs single-product crawler:**
- URL → product mapping via `url_to_product()` extracts the 2nd URL segment
- Product subdirectories created on-the-fly during crawl
- No page limit (MAX_PAGES absent — crawls everything)
- Combined regex for link discovery handles both markdown `[text](url)` and HTML `href="url"` formats
- Each page uploaded individually during the crawl (no separate upload phase)

**Link extraction regex (critical):**
```python
LINK_PAT = re.compile(r'(?:href="|\\(+)((?:https?:)?//docs\.rkeeper\.ru/[^"\')\s]+\.html)')
```

This matches:
- HTML: `<a href="https://docs.rkeeper.ru/...">`
- Markdown: `[text](https://docs.rkeeper.ru/...)`
- Relative proto: `//docs.rkeeper.ru/...`

**Product categories discovered on docs.rkeeper.ru (22 products):**
rk7, license, sh5, delivery, webman, cloud, mobwaiter, ws, elk, kds, kiosk, rkfin, gs, qms, menuboard, crm, pds, rklite, fordealers, news, rkint, archive

**Typical size:** 500-1000+ pages across all products

**Watch out:**
- First pass with `LINK_PAT = re.compile(r'href="...")'` found only 1 page because crawl4ai renders markdown links, not HTML. Switch to the combined regex above.
- Run in background: `notify_on_complete=True, timeout=3600`
- The crawler uses `while to_visit:` without a `MAX_PAGES` guard. For very large sites (2000+ pages) it could run for hours. Monitor progress via `process(action='log')`.
