# International Platforms — Scraping Guide

## Reddit

**Status: BLOCKED for scraper access.**
- `old.reddit.com` and JSON API (`reddit.com/r/*/new/.json`) return "Blocked" page.
- `www.reddit.com` redirects to login.
- User-Agent and cookie tricks don't help — Reddit uses network-level blocking.

**Workarounds:**
1. Google search `site:reddit.com/r/AI_Agents <query>` — but Google also blocks scrapers.
2. Browser with residential proxies (Browserbase with proxy enabled).
3. Manual: use `browser_navigate` to Reddit, accept the login wall, search from there.
4. Use archived/cached versions: `webcache.googleusercontent.com`.

**For cron-based research:** note in output that Reddit data may be incomplete.

## YouTube

**Status: WORKS via browser.**
- `browser_navigate` to `https://www.youtube.com/results?search_query=<query>&sp=CAISBBABGAE%3D` (filter by date).
- Filter params: `CAISBBABGAE` = "Today", `CAISBBABGAM` = "This week", `CAISBBABGAE` = "Recently uploaded".
- `browser_snapshot` returns video titles, view counts, channel names, and upload age.
- Video titles are nested under `<heading>` elements with `level=3`.
- View counts appear as `StaticText` like "1.4K views".
- Upload age appears as `StaticText` like "13 days ago".

**Limitations:**
- Cannot scrape the full description without clicking into each video.
- Comment data not accessible via snapshot (needs JS interaction).

## Google Trends

**Status: RATE-LIMITED.**
- Interactive page `trends.google.com/trends/explore` returns HTTP 429 under automation.
- RSS feed still works: `trends.google.com/trending/rss?geo=US` returns XML with top 20 daily trending searches (general, not AI-specific).

**Alternative:** Note "Google Trends data unavailable due to rate limiting" in reports.

## DuckDuckGo

**Status: CAPTCHA-BLOCKED.**
- `html.duckduckgo.com/html/?q=<query>` returns JavaScript challenge (select squares with ducks).
- Cannot be bypassed without solving the captcha.

## SearXNG instances

**Status: INCONSISTENT.**
- Some instances (searx.be, search.sapti.me) return empty or error responses.
- Not a reliable substitute for Google/DuckDuckGo.

## Bing

**Status: PARTIALLY BLOCKED.**
- Returns results but may return empty for long queries.
- Better success with simple single-word queries.
- User-Agent: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36` works best.
