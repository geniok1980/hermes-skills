# Documentation Site → Obsidian via Crawl4AI + WebDAV

Full production pattern for crawling large Confluence documentation sites (docs.rkeeper.ru, etc.) and importing every page into Obsidian as Markdown.

## Prerequisites

- crawl4ai installed in a venv (`/root/crawl4ai-env/`)
- WebDAV access to Yandex Disk with Obsidian vault

## Architecture

```
┌─ docs.rkeeper.ru ──┐     ┌─ Crawl4AI (Playwright) ──┐     ┌─ WebDAV ──┐     ┌─ Obsidian ──┐
│  Confluence (JS)   │────▶│  BFS → Markdown → Clean   │────▶│  curl -T   │────▶│  Vault      │
│  22 продуктов      │     │  One-pass discovery+save  │     │  MKCOL     │     │  Sync via   │
│  400+ страниц      │     │  Product-based folders    │     │  Yandex    │     │  Remotely   │
└────────────────────┘     └────────────────────────────┘     │  Disk     │     │  Save       │
                                                              └───────────┘     └────────────┘
```

## Key Patterns

### 1. Product Detection from URL

Confluence documentation URLs encode the product as the first path segment:
- `docs.rkeeper.ru/rk7/latest/ru/page.html` → product = `rk7`
- `docs.rkeeper.ru/sh5/storehouse-pro-1146986.html` → product = `sh5`
- `docs.rkeeper.ru/license/sistema-litsenzirovaniya.html` → product = `license`

```python
def url_to_product(url: str) -> str:
    path = urlparse(url).path.strip('/')
    return path.split('/')[0] if path else "root"
```

### 2. Link Extraction from Crawl4AI Markdown (CRITICAL)

Confluence renders content via JS. crawl4AI returns the rendered page as Markdown, where links appear as:

```markdown
[text](https://docs.rkeeper.ru/rk7/latest/ru/page.html)
```

NOT as HTML `<a href="...">`. Use a combined regex:

```python
LINK_PAT = re.compile(r'(?:href="|\(+)((?:https?:)?//docs\.rkeeper\.ru/[^"\')\s]+\.html)')
```

**First-pass failure pattern**: Using only `href="..."` regex on crawl4AI output yields 0-1 pages.

### 3. One-Pass BFS (Discovery + Content)

```python
all_urls = {}  # url -> (product, filename, local_path)
to_visit = [START_URL]
visited = set()

async with AsyncWebCrawler() as crawler:
    while to_visit:   # NO max_pages limit — user wants everything
        url = to_visit.pop(0)
        if url in visited: continue
        visited.add(url)

        result = await crawler.arun(url=url, word_count_threshold=5, bypass_cache=True)
        if not result.success or not result.markdown: continue

        # 1. Extract links for further discovery
        for m in LINK_PAT.finditer(result.markdown):
            link = m.group(1)
            if link not in visited and link not in all_urls:
                to_visit.append(link)

        # 2. Save content immediately
        product = url_to_product(url)
        title = extract_title(result.markdown)
        save_and_upload(url, product, title, result.markdown)
        all_urls[url] = (product, filename)
```

### 4. Product-Based Folder Organization

```
Obsidian Vault/rkeeper-docs/full/
├── index.md              # Main index with per-product sections
├── rk7/                  # r_keeper 7 (150 pages)
│   ├── r_keeper-7-1146927.md
│   ├── nastrojka-tsen-4038037.md
│   └── ...
├── sh5/                  # StoreHouse Pro (58 pages)
├── delivery/             # Delivery (61 pages)
├── cloud/                # r_k Cloud (39 pages)
├── license/              # System licensing (34 pages)
├── webman/               # Web Manager (30 pages)
├── kiosk/                # Kiosk PRO (29 pages)
├── ws/                   # White Server (36 pages)
├── elk/                  # Office (17 pages)
├── kds/                  # KDS Pro (16 pages)
├── gs/                   # Guest Screen (16 pages)
├── mobwaiter/            # Waiter & Cash Desk (19 pages)
├── rkfin/                # r_k Finance (25 pages)
├── qms/                  # QMS (7 pages)
├── rklite/               # Lite
├── rkint/                # Integrations
├── pds/                  # PDS
├── news/                 # Release Notes
├── menuboard/            # Menuboard Pro
├── fordealers/           # For dealers
├── crm/                  # CRM
└── archive/              # Archive
```

### 5. WebDAV Upload (curl -T)

```python
async def webdav_upload(local: str, remote: str) -> bool:
    proc = await asyncio.create_subprocess_exec(
        "curl", "-s", "-u", "user:pass", "-T", local,
        f"https://webdav.yandex.ru/Obsidian%20Vault/Folder/{remote}",
        "-w", "%{http_code}",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
    stdout, _ = await proc.communicate()
    return stdout.decode().strip() in ('201', '204', '200')
```

**NEVER use heredoc** for uploads — `asyncio.create_subprocess_exec` + shell heredoc conflicts cause hangs. Always save to local file first, then `curl -T`.

### 6. Index Generation

```python
idx = ["---", f"title: {SITE_NAME}", f"total: {total_pages}", "---",
       "", f"# {SITE_NAME}", "", "## Products", ""]
for product in sorted(product_counts.keys()):
    idx.append(f"### {product} ({product_counts[product]} pages)")
    for url, info in saved_urls.items():
        if info[0] != product: continue
        idx.append(f"  - [[{info[1].replace('.md', '')}|{title}]]")
```

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Pages per second | ~0.3 (3-4s per page with Playwright) |
| rk7 product | 150 pages, ~8 min |
| Full docs.rkeeper.ru (22 products) | 400-500 pages, ~25-30 min |
| WebDAV upload speed | ~2-3 files/sec (parallel batches) |
| Local storage | ~3-5 MB per 100 pages |

## Cron Integration

This task runs as a one-shot script, not a recurring cron. Run with:
```bash
PYTHONUNBUFFERED=1 /root/.hermes/scripts/crawl-rkeeper-full.py
```
Use background terminal with 1-hour timeout.

## Pitfalls

1. **BFS discovers all versions**: Confluence changelogs include ALL historical versions. rk7 alone has 50+ changelog pages (7.26.04, 7.26.03, 7.26.01, ...). The BFS will find them all — this is correct behavior since the user wants "all documentation".

2. **Product detection fails on root URLs**: Root-level pages (not under any product) get saved to `root/` folder. These are usually links pages and can be safely ignored.

3. **Duplicate filenames across products**: The same basename might exist in different products (e.g., `o-produkte-xxx.html` in rk7, cloud, license). Solution: save in separate product subfolders.

4. **WebDAV rate limiting**: Yandex Disk may throttle after ~50 rapid uploads. The 3-4s crawl time between uploads prevents this naturally.

5. **Background process output**: Using `PYTHONUNBUFFERED=1` helps see real-time progress, but some output still gets buffered. Check `find` counts for accurate progress.

6. **Empty source pages are NOT a crawler bug**: Scroll Viewport (K15t) renders Confluence content server-side (SSR), so crawl4ai extracts it fine for most pages. BUT some pages — especially new release notes, sub-version placeholders, and unpublished drafts — exist on the Confluence server as **empty stubs with only navigation chrome** (sidebar, breadcrumbs, footer). The crawler faithfully saves what the server sends. Before debugging the crawler, verify the page has content by checking raw HTML via curl:
   ```bash
   curl -s <url> | python3 -c "
   import sys,re; html=sys.stdin.read()
   body=re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
   txt=re.sub(r'<[^>]+>',' ',body.group(1)) if body else ''
   print(len(txt),'chars'); print(txt[:500])"
   ```
   If output is just navigation links (release version list, sidebar items, copyright), the page is empty on the source.

   **Detection heuristics for empty pages in post-processing:** a page with `word_count_threshold=5` that produces <~5KB of markdown and has no `#` heading lines longer than 30 chars is almost certainly empty. Such pages have only a title (`# 7.26.05`) and navigation. The `fit_html` contains `<div class="article__content">` but it's empty or has only breadcrumbs.

   **Verified on docs.rkeeper.ru:** 7.26.05 (9.6KB markdown), 7.26.03-001 (10KB), 7.26.04-01 (10.8KB) — all empty stubs on the server. 7.26.04 (15KB) and older releases — full content. The Confluence REST API (`/rest/api/content/{pageId}?expand=body.storage`) returns `<p />` for empty stub pages, confirming the server stores no body content.

   **What to do:** log empty pages during crawl, skip uploading them, or upload with a marker `<!-- EMPTY: no body content on source -->` in the markdown. Check source FTP (`https://files-rkcloud.ucs.ru/`) for PDF alternatives for critical missing pages.
