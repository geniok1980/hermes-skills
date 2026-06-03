---
name: web-scraping
description: Parse websites using Scrapling (fast HTTP/stealth) and crawl4AI (Markdown/docs) for data collection — job boards, freelance platforms, price monitoring. Setup, usage patterns, pitfalls, and integration with cron jobs.
---

# Web Scraping with Scrapling & crawl4AI

> This skill covers two complementary scraping tools. **Scrapling** for structural data extraction (hh.ru, freelance boards, catalogues) — 20-50x faster, CSS/XPath selectors, adaptive elements, built-in Cloudflare bypass. **crawl4AI** for documentation-to-Markdown conversion (Confluence, ReadTheDocs) and WebDAV upload to Obsidian.

## When to use which

| Task | Tool |
|------|------|
| hh.ru, Avito, job boards — structural data | **Scrapling** (HTTP Fetcher, ~0.6s) |
| Cloudflare-protected sites | **Scrapling** (StealthyFetcher, bypasses Turnstile) |
| Sites with changing HTML structure | **Scrapling** (adaptive=True finds elements after redesign) |
| Confluence / docs → Markdown → Obsidian | **crawl4AI** (native Markdown + WebDAV scripts) |
| Full-site recursive crawl | **crawl4AI** (BFS pattern) **or** Scrapling (Spider with pause/resume) |
| Real-time / multi-session crawl | **Scrapling** (Spider framework, streaming, multiple session types) |

## Setup

### Installation (one-time)

```bash
# Create dedicated venv
python3 -m venv /root/crawl4ai-env
source /root/crawl4ai-env/bin/activate
pip install -U crawl4ai

# Install browser
crawl4ai-setup
```

The venv lives at `/root/crawl4ai-env`. All crawl4ai scripts should use explicit shebang.

### Verify

```bash
source /root/crawl4ai-env/bin/activate
crawl4ai-doctor
```

## Scrapling Setup

### Installation

```bash
# Create dedicated venv
python3 -m venv /root/scrapling-env
/root/scrapling-env/bin/pip install "scrapling[fetchers,shell,ai]"

# Install browsers (for StealthyFetcher / DynamicFetcher)
/root/scrapling-env/bin/scrapling install
```

The venv lives at `/root/scrapling-env`. All Scrapling scripts should use explicit shebang `#!/root/scrapling-env/bin/python3`.

### Verify

```bash
/root/scrapling-env/bin/python3 -c "from scrapling.fetchers import Fetcher; print('OK')"
```

## Scrapling Basic Usage

### HTTP fetcher (fastest, no browser)

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://example.com', stealthy_headers=True)
print(page.status)  # 200

# CSS selectors
titles = page.css('.title::text').getall()

# XPath
items = page.xpath('//div[@class="item"]/text()').getall()

# find_all (BeautifulSoup-style)
links = page.find_all('a', class_='link')

# Navigation
parent = page.css('.item')[0].parent
siblings = page.css('.item')[0].siblings
similar = page.css('.item')[0].find_similar()
```

### Stealthy fetcher (bypass Cloudflare)

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare',
    headless=True, solve_cloudflare=True)

# After Cloudflare is solved — same API
data = page.css('#padded_content a').getall()
```

### Adaptive elements (survive website redesign)

```python
# First scrape: save element fingerprints
page.css('.product', auto_save=True)

# Weeks later, after website redesign: find elements by similarity
page.css('.product', adaptive=True)  # still works
```

### Spider for full crawls (pause/resume, concurrent)

```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
    name = "crawl"
    start_urls = ["https://example.com/"]
    concurrent_requests = 10

    async def parse(self, response: Response):
        for item in response.css('.item'):
            yield {"title": item.css('h2::text').get()}

result = MySpider(crawldir="./data").start()  # crawldir enables pause/resume
result.items.to_json("output.json")
```

### CLI (quick extraction)

```bash
scrapling extract get 'https://example.com' page.md
scrapling extract fetch 'https://example.com' page.txt --css-selector '.content'
```

## Basic Usage Pattern

```python
import asyncio
from crawl4ai import *

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://example.com",
            word_count_threshold=10,
            bypass_cache=True,  # force fresh fetch
        )
        if result.success and result.markdown:
            print(result.markdown)  # clean LLM-ready Markdown

asyncio.run(main())
```

### Key Parameters

| Parameter | Default | When to change |
|-----------|---------|----------------|
| `word_count_threshold` | 10 | Lower (2-5) for dense content, higher (20-50) for noisy pages |
| `bypass_cache` | False | Always True for fresh data (job listings, prices) |
| `css_selector` | None | Set to a specific container when you only need a page section (e.g., `.vacancy-serp-content` for hh.ru) |
| `verbose` | True | Omit entirely to suppress — don't pass `verbose=False` (see pitfall #1) |

## Integration with Cron Jobs — No-Agent Pattern

The most reliable pattern for daily scraping cron jobs is **`no_agent=True`** with a standalone script. The script's stdout is delivered verbatim — no LLM, no token limits, no "describing instead of doing" failures.

### Setup

1. Write a Python script with the correct **shebang** pointing to the crawl4ai venv:

```python
#!/root/crawl4ai-env/bin/python3
```

2. The script runs via cron: `cronjob(action='create', no_agent=True, script='your-script.py')`

3. Script output (`print()`) becomes the delivered message. If there's nothing to report, produce empty output.

### Cron job setup

```bash
cronjob(action='create',
    name='Earnings digest',
    schedule='30 4 * * *',          # 04:30 Samara (00:30 UTC)
    script='earnings-compilation.py',
    no_agent=True,
    deliver='origin')
```

Scripts in `no_agent=True` mode run via the system shell. The **shebang** must be explicit to pick up the venv's Python.

### Testing & Debugging

- Run the script manually first: `timeout 120 /path/to/script.py`
- Check cron output via cron job list or session_search
- Use `cronjob(action='run', job_id=...)` to test with the updated script
- Scripts are stateless — each run is a fresh fetch, no caching

## Site-Specific Notes

### hh.ru

**Preferred tool: Scrapling HTTP Fetcher** (~0.6s vs ~10s for crawl4ai).

- URL: `https://hh.ru/search/vacancy?text={query}&area=113` (113 = Russia)
- Scrapling handles it without a browser — `stealthy_headers=True` bypasses bot detection
- **Current selectors** (June 2026): `[data-qa="vacancy-serp__vacancy"]` for cards, `[data-qa="serp-item__title-text"]` for titles, `[data-qa="vacancy-serp__vacancy-employer-text"]` for employers, `[data-qa="address-metro-station-name"]` for metro
- Salaries are in text without dedicated data-qa — extract via regex: `re.compile(r'((?:\d{1,3}\s?){1,3}\u202f?\d{3}\s*(?:₽))')`
- See `references/scrapling-hh.py` for a working cron-ready script
- **Known issue**: hh.ru sometimes shows a "Произошла ошибка" message on first load — retry usually works (with crawl4ai). Scrapling is more resilient.

### fl.ru
- URL: `https://www.fl.ru/search/?q={query}`
- Requires authentication for search results — without login, returns empty results
- Alternative: use the projects category page directly: `https://www.fl.ru/projects/`
- Scrapling's StealthyFetcher with session persistence may handle auth better

### kwork.ru
- URL: `https://kwork.ru/search?query={query}`
- Search by name finds users, not projects
- Better to browse categories directly (Разработка и IT → Скрипты, боты)

### Avito (Услуги)
- URL: `https://www.avito.ru/all/uslugi?q={query}`
- Heavily JS-rendered, crawl4AI handles it well
- May return ~7k chars of content

## BFS Deep Crawl (Documentation Sites)

For crawling large documentation trees (Confluence, ReadTheDocs, etc.), use a **two-phase approach** to avoid ~10x slowdown from using Playwright for link discovery.

### Phase 1: Discover URLs via curl (fast mode)

Confluence and similar doc sites render internal links as `<a href="...">` in raw HTML. No JS rendering needed for link discovery — use curl:

```python
import re, asyncio

link_pat = re.compile(r'href="(https?://domain\.com/path/[^"]+\.html)"')

async def discover_urls(start_url, max_pages=200):
    discovered = {start_url}
    to_visit = [start_url]
    visited = set()
    
    while to_visit and len(discovered) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)
        
        proc = await asyncio.create_subprocess_exec(
            "curl", "-sL", url,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
        stdout, _ = await proc.communicate()
        html = stdout.decode('utf-8', errors='replace')
        
        for m in link_pat.finditer(html):
            link = m.group(1)
            if link not in visited and link not in discovered:
                discovered.add(link)
                to_visit.append(link)
    
    return discovered
```

### Phase 2: Crawl content via crawl4ai

After Phase 1 returns the full URL list, crawl each page for proper content:

```python
async with AsyncWebCrawler() as crawler:
    for url in sorted(all_urls):
        result = await crawler.arun(url=url, word_count_threshold=5, bypass_cache=True)
        if result.success and result.markdown:
            # Save locally, then upload
```

### Phase 3: Upload to WebDAV (Obsidian)

Use `curl -T` for uploads (NOT heredoc — unreliable with asyncio subprocess):

```python
async def webdav_upload(local: str, remote: str) -> bool:
    proc = await asyncio.create_subprocess_exec(
        "curl", "-s", "-u", "user:pass", "-T", local,
        f"https://webdav.yandex.ru/Obsidian%20Vault/Folder/{remote}",
        "-w", "%{http_code}",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
    stdout, _ = await proc.communicate()
    return stdout.decode().strip() in ['201', '204', '200']  # all success codes
```

### Phase 4: Index page

Generate `index.md` with `[[wikilinks]]` for Obsidian navigation.

See `references/docsite-to-obsidian.md` for the full production pattern with all four phases.

## User preference

**Евгений:** Результат сразу, минимум объяснений. Подборка должна быть полной, без обрывания на середине. Если скрипт не может выполниться полностью — лучше не присылать ничего, чем кусок.

## Pitfalls

### 1. crawl4ai v0.8.6 — verbose=False bug
Passing `verbose=False` to `arun()` causes:
```
aprocess_html() got multiple values for keyword argument 'verbose'
```
**Fix:** Simply omit the `verbose` parameter. Default verbose output is fine for CLI runs.

### 2. crawl4ai v0.8.6 — deep_crawl=True bug
Using `deep_crawl=True` or similar options that expect `CrawlResult.children` will fail with an AttributeError — the attribute doesn't exist in v0.8.6.
**Fix:** Use manual BFS (breadth-first search) with `to_visit` + `visited` sets instead of relying on built-in deep crawl. The two-phase BFS pattern (curl for link discovery, crawl4ai for content) described in this skill is the correct workaround.

### 3. Timeouts
- Some sites take 10-15s to render. Default timeout is usually fine but set `timeout=30` in `arun()` for slow sites.
- If a site consistently times out, try without `css_selector` (full page load is sometimes faster).
- For doc-site crawls (100+ pages), use a 10-minute timeout or run as a background process.

### 4. Massive Output
- hh.ru returns 500k+ chars of markdown. If you only need structured data (titles, salaries), post-process with regex/parsing instead of dumping the full markdown.
- Use `word_count_threshold=50` on noisy pages to filter out navigation.

### 5. Login Walls
- fl.ru, Avito, and some sections of kwork.ru require authentication.
- For cron jobs, these cannot be accessed without session cookies.
- Better to focus on hh.ru, Хабр Карьера, and Telegram channels for automated scraping.

### 6. Rate Limiting
- crawl4AI uses a real browser, so it's harder to detect as a bot.
- But too many rapid requests still trigger rate limits. Add `asyncio.sleep(2-5)` between requests.
- For cron jobs (daily runs), rate limiting is not an issue.

### 7. venv Activation (cron scripts)
- Use explicit shebang: `#!/root/crawl4ai-env/bin/python3`
- The system Python won't have crawl4ai installed.
- cron `no_agent` scripts rely on shebang to pick the right venv.

### 8. BFS Discovery Order
- Confluence sites include sidebar nav links on every page. A naive BFS may explore the entire tree in sidebar order, not content order.
- Set `max_pages` to a reasonable limit (100-200) unless you need the full site.

### 9. WebDAV Upload via asyncio + curl
- Do NOT use shell heredoc for uploads — the heredoc marker conflicts with shell escaping and the process may hang or truncate content.
- Use `-T` flag (file upload) with `asyncio.create_subprocess_exec` instead.
- Always save to a local file first, then upload. This allows retries without refetching.
- MKCOL returns 201 (Created) for new dirs and 405 (Method Not Allowed) for existing — both are success for our purposes.

### 10. Content Cleaning for Documentation Sites
- Confluence pages include header/footer, sidebar nav, and image references in the markdown.
- Strip `![...](url)` lines (images) if they won't render in an offline vault. Use `if s.startswith('!['): continue` to skip inline logo images that Confluence inserts in every page's markdown.
- Strip lines containing `vk.com`, `youtube.com`, `bit.ly` (social links).
- Add YAML frontmatter with `title`, `source`, and `date` for Obsidian.

### 11. Link Extraction from Crawl4AI Markdown
crawl4AI renders page content **after JS execution**, so links appear in markdown format `[text](url)` rather than HTML `<a href="url">`. Use a combined regex:

```python
LINK_PAT = re.compile(r'(?:href="|\\(+)((?:https?:)?//domain\\.com/[^"\')\\s]+\\.html)')
```

This handles three cases:
- **HTML**: `href="https://domain.com/page.html"`
- **Markdown**: `[text](https://domain.com/page.html)`
- **Protocol-relative**: `//domain.com/page.html`

⚠️ **First-pass failure pattern:** Using only `href="..."` regex on crawl4ai markdown output yields 0-1 pages because all links are in markdown format.

### 13. Empty Source Pages on Confluence/Scroll Viewport Sites

docs.rkeeper.ru (and similar Confluence + Scroll Viewport sites) renders content server-side (SSR), so crawl4ai extracts it fine for most pages. BUT some pages are **genuinely empty** — they exist as stubs on the Confluence server with no body content, only navigation chrome (sidebar, breadcrumbs, footer).

**How to detect:** Pages with `word_count_threshold=5` that produce <~5KB markdown and have no `#` heading lines longer than 30 chars are empty stubs. The raw HTML has `<div class="article__content">` but it's empty.

**Verified pattern on docs.rkeeper.ru:** release notes for the latest version and sub-version placeholders (e.g., 7.26.05, 7.26.03-001, 7.26.04-01) are empty on the server. The Confluence REST API confirms: `/rest/api/content/{pageId}?expand=body.storage` returns `<p />`.

Before debugging the crawler, verify page content via curl first. See `references/docsite-to-obsidian.md` pitfall #6 for details and verification commands.

### 14. Scrapling: adaptive=True requires global enable

`auto_save=True` and `adaptive=True` only work when `StealthyFetcher.adaptive` is set globally:

```python
# WRONG — auto_save silently ignored
page = StealthyFetcher.fetch('https://example.com')
page.css('.product', auto_save=True)

# RIGHT — enable before any fetch
StealthyFetcher.adaptive = True
page = StealthyFetcher.fetch('https://example.com', headless=True)
page.css('.product', auto_save=True)
```

### 15. Scrapling: StealthyFetcher headless for cron

`StealthyFetcher` opens a real browser. For cron jobs with no display:
- Always pass `headless=True` — otherwise crashes with 'No display available'
- Each call takes ~10-15s (browser startup overhead) — prefer `Fetcher` (HTTP) when possible
- Use `solve_cloudflare=True` for Cloudflare-protected sites

### 16. Scrapling: Response object quirks

- `.body` = raw bytes, `.text` = decoded string, `.html_content` = full HTML
- NOT `.content` (common 'requests'-import mistake)
- Parsed DOM methods (`.css()`, `.xpath()`, `.find_all()`) work directly on Response

### 17. Scrapling: hh.ru selectors drift

hh.ru periodically changes class names and data-qa attributes. Run discovery periodically:

```python
vacs = page.css('[data-qa="vacancy-serp__vacancy"]')
all_qas = set()
for v in vacs:
    for el in v.css('[data-qa]'):
        qa = el.attrib.get('data-qa', '')
        if qa: all_qas.add(qa)
print('\n'.join(sorted(all_qas)))
```

### 12. User Preference: No Artificial Crawl Limits
When crawling documentation sites for Obsidian import, Евгений explicitly prefers **NO page limit** (`MAX_PAGES = 9999` or simply an unbounded `while to_visit:` loop). He will ask "а зачем лимит 150, а если там больше страниц?" if you set one. Only cap the crawl when:
- There's a known upper bound (e.g., "crawl the last 30 days of changelogs")
- The user explicitly requests a limit
- Resource constraints require it (e.g., only 1GB free disk)

## Reference files

- `references/earnings-compilation.py` — Production script: parses 6 hh.ru categories for the morning earnings digest using Scrapling (20x faster than crawl4ai version). Runs daily via no_agent cron.
- `references/docsite-to-obsidian.md` — Pattern for crawling large Confluence documentation sites and uploading all pages as Markdown to Obsidian vault via WebDAV.
- `references/crawl4ai-scripts.md` — Concrete script examples (earnings digest, rkeeper single-product crawl, rkeeper multi-product crawl) with full BFS patterns and link-extraction regex.

## Related

- `cron-jobs` skill — for integrating scraping results into daily cron digests
- `russian-marketplace-profiles` skill — for platform-specific account setup and API auth
- ~~`crawl4ai` skill~~ — **absorbed into this skill.** Tool-level details (parameters, known bugs, installation) are now integrated above.
