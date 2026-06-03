---
name: cloudflare-dns-caddy-proxy
description: Add DNS records via Cloudflare API and configure Caddy reverse proxy on a remote server via SSH.
category: devops
triggers:
  - создай поддомен
  - add subdomain
  - add DNS record
  - настрой caddy
  - reverse proxy
  - cloudflare dns
  - белый экран
  - white screen
  - не грузится сайт
  - russia cloudflare block
author: Hermes Agent
version: 1.2.0
---

# Cloudflare DNS + Caddy Reverse Proxy

Add a subdomain pointing to a service running on a server behind Caddy.

## SSH Access Methods

### Key-based (primary)
The skill primarily uses SSH key auth (`-i /root/.ssh/id_ed25519_1panel`).

### Password-based fallback (sshpass)
When no key is available, use `sshpass` with the user's shared password:

```bash
which sshpass || apt-get install -y sshpass
sshpass -p "20Upiter17!" ssh -o StrictHostKeyChecking=no root@SERVER_IP "command"
sshpass -p "20Upiter17!" scp -o StrictHostKeyChecking=no local.file root@SERVER_IP:/remote/path/
```

Good for one-shot commands on newly discovered servers. Test reachability first: `nc -z -w 3 IP 22`.

## Pre-flight Check — inspect existing records first

Before creating a new subdomain, **check what all A records on the zone use for proxied mode**. If you're on geniok.ru (server 2.26.98.104), do this first:

```python
import json, urllib.request
with open('/root/clawhost/.env') as f:
    token = [l.split('=',1)[1].strip() for l in f if 'CLOUDFLARE_API_TOKEN' in l][0]
zone_id = 'c53b86d60ef7fa713b5fb535893c8748'
req = urllib.request.Request(
    f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A',
    headers={'Authorization': f'Bearer {token}'})
resp = json.loads(urllib.request.urlopen(req).read())
for r in resp['result']:
    if 'geniok.ru' in r['name']:
        print(f"{r['name']:35s} proxied={str(r['proxied']):5s} content={r['content']}")
```

**If ALL existing subdomains on the same server/zone use proxied=False, your new subdomain MUST also use proxied=False.** Do not assume proxied=True works — verify by inspecting what the zone already does.

Then check the Caddyfile for the pattern used by a working subdomain:
```bash
cat /etc/caddy/Caddyfile
```

**Copy the exact same block shape** from a working subdomain (like `aiphoto.geniok.ru`). If aiphoto uses just a bare `reverse_proxy` block without @http handlers, tls blocks, or transport timeouts — your new subdomain should match. Overcomplicating breaks things.

## Workflow

### 1. Get Cloudflare credentials

The API token and zone ID are stored in the project `.env` file (e.g. `/root/clawhost/.env`):

```bash
# Read token directly from .env
CLOUDFLARE_TOKEN=$(sed -ne 's/.*CLOUDFLARE_API_TOKEN=//p' /root/clawhost/.env)
ZONE_ID=$(sed -ne 's/.*CLOUDFLARE_ZONE_ID=//p' /root/clawhost/.env)
```

### 2. Add DNS A record

**Shell approach** (watch for token special chars in $( ) substitution):

```bash
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "A",
    "name": "SUBDOMAIN",
    "content": "SERVER_IP",
    "ttl": 120,
    "proxied": true
  }'
```

**Python approach** (more reliable — avoids token quoting issues):

```python
import json, urllib.request
with open('/root/clawhost/.env') as f:
    token = [l.split('=',1)[1].strip() for l in f if 'CLOUDFLARE_API_TOKEN' in l][0]
zone_id = 'c53b86d60ef7fa713b5fb535893c8748'
data = json.dumps({
    'type': 'A', 'name': 'SUBDOMAIN', 'content': 'SERVER_IP',
    'ttl': 120, 'proxied': True
}).encode()
req = urllib.request.Request(
    f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records',
    data=data,
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    method='POST'
)
resp = json.loads(urllib.request.urlopen(req).read())
print(f"Created: {resp['result']['name']}")
```

**To update an existing record** — get record ID first, then PUT:\n\n```python\nimport json, urllib.request\nwith open('/root/clawhost/.env') as f:\n    token = [l.split('=',1)[1].strip() for l in f if 'CLOUDFLARE_API_TOKEN' in l][0]\nzone_id = 'c53b86d60ef7fa713b5fb535893c8748'\nheaders = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}\n\n# Find the record\nreq = urllib.request.Request(\n    f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A&name=SUBDOMAIN.geniok.ru',\n    headers=headers)\nresult = json.loads(urllib.request.urlopen(req).read())\nrecord_id = result['result'][0]['id']\n\n# Update\nreq2 = urllib.request.Request(\n    f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}',\n    data=json.dumps({'type':'A','name':'SUBDOMAIN','content':'IP','ttl':120,'proxied':True}).encode(),\n    headers=headers,\n    method='PUT')\nresp = json.loads(urllib.request.urlopen(req2).read())\nprint(f\"Proxied: {resp['result']['proxied']}\")\n```

### 3. SSH to server and edit Caddyfile

```bash
# SSH with the available key
ssh -i /root/.ssh/id_ed25519_1panel root@SERVER_IP

# Read current config
cat /etc/caddy/Caddyfile

# Append new site block
echo -e '\nSUBDOMAIN.geniok.ru {\n\treverse_proxy 127.0.0.1:PORT\n}' >> /etc/caddy/Caddyfile

# Validate and reload
caddy validate --config /etc/caddy/Caddyfile
caddy reload --config /etc/caddy/Caddyfile
```

### 4. Static file deployment (landing page, SPA)

When deploying a static site (not a proxied backend service), use Caddy's `file_server` directive:

```bash
# 1. Upload files to the server
ssh -i /root/.ssh/id_ed25519_1panel root@SERVER_IP "mkdir -p /var/www/PROJECT_NAME"
scp -i /root/.ssh/id_ed25519_1panel /path/to/local/index.html root@SERVER_IP:/var/www/PROJECT_NAME/index.html

# 2. Add to Caddyfile -- use heredoc to safely rewrite multi-line blocks (sed breaks on multi-line)
# For small edits, append with heredoc is safest:
ssh -i /root/.ssh/id_ed25519_1panel root@SERVER_IP "
cat >> /etc/caddy/Caddyfile << 'EOF'

SUBDOMAIN.geniok.ru {
    root * /var/www/PROJECT_NAME
    file_server
}
EOF"

# 3. Reload
ssh -i /root/.ssh/id_ed25519_1panel root@SERVER_IP "caddy reload --config /etc/caddy/Caddyfile 2>&1"
```

**To rewrite the entire Caddyfile over SSH** (when adding multiple blocks), use a heredoc with `cat >`:

```bash
ssh -i /root/.ssh/id_ed25519_1panel root@SERVER_IP "
cat > /etc/caddy/Caddyfile << 'CADDYEOF'
# Existing blocks unchanged...
clawhost.geniok.ru {
    reverse_proxy 127.0.0.1:2222
}

geniok.ru {
    root * /var/www/geniok
    file_server
}
CADDYEOF

caddy reload --config /etc/caddy/Caddyfile 2>&1
"
```

The `'CADDYEOF'` quoting (single-quotes around the delimiter) prevents SSH from expanding variables on the client side -- critical when the Caddyfile contains `$` characters.

### 5. Verify

```bash
# Check DNS
dig +short SUBDOMAIN.geniok.ru

# Check HTTP response (for proxy backend)
curl -s -o /dev/null -w "%{http_code}" http://SERVER_IP:PORT/

# Check HTTP response (for static site)
curl -s -o /dev/null -w "%{http_code}" https://SUBDOMAIN.geniok.ru/

# Check Caddy config on server
ssh -i /root/.ssh/id_ed25519_1panel root@SERVER_IP "caddy validate --config /etc/caddy/Caddyfile 2>&1 | tail -3"
```

### 6. Toggle proxy on/off (PATCH existing record)

```bash
# Get record ID first
RECORD_ID=$(curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?type=A&name=SUBDOMAIN.DOMAIN" \
  -H "Authorization: Bearer $CLOUDFLARE_TOKEN" | jq -r '.result[0].id')

# PATCH to toggle proxy
curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
  -H "Authorization: Bearer $CLOUDFLARE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"A","name":"SUBDOMAIN","content":"SERVER_IP","ttl":120,"proxied":true}'
```

## SSL / Proxy Interaction (Critical)

Cloudflare proxy (`proxied: true`) and Caddy's automatic HTTPS can conflict:

- Cloudflare's default SSL mode is "Flexible" -- traffic from Cloudflare edge to the origin server is HTTP (port 80), not HTTPS.
- Caddy automatically redirects HTTP to HTTPS (308 Permanent Redirect) by default. When Cloudflare sends HTTP to port 80, Caddy redirects to HTTPS, creating a redirect loop or TLS handshake failure.

**Symptom patterns:**

- **Redirect loop / TLS failure on page load:** Cloudflare Flexible SSL sends HTTP to origin, Caddy redirects back to HTTPS. Browser hangs or shows "too many redirects".
- **White screen / blank page:** React/Vue app loads HTML but Cloudflare proxy is blocked or failing (common in Russia where Cloudflare CDN is under DDoS/blocked). The browser gets the index.html but JS never fully executes. Fix: switch to DNS-only mode (proxied: false), simplify Caddy config, user hard-refreshes.

- **ERR_HTTP2_PING_FAILED in console — Russia→EU HTTP/2 disconnects:** After switching to DNS-only (proxied: false), Russian users may still see a white screen with `ERR_HTTP2_PING_FAILED` in the browser console. The HTML loads, then JS asset downloads fail because HTTP/2 PING frames from browser to server time out over the unstable direct connection. Fix: force HTTP/1.1 in Caddy via `tls { alpn http/1.1 }`:

  ```caddy
  example.geniok.ru {
      tls {
          alpn http/1.1
      }
      reverse_proxy 127.0.0.1:PORT { ... }
  }
  ```

  Verify with `curl -s -o /dev/null -w "HTTP version: %{http_version}" https://example.geniok.ru/` (should print 1.1).
  
  **Diagnostic note:** Don't dismiss browser extension errors (`contentscript.js`, `ObjectMultiplex`) in the console — they're noise from wallet extensions. Look past them for the real error: `ERR_HTTP2_PING_FAILED` on a `.js` asset load. If a Russian user reports white screen, check for this first.
  
  **WARNING — `tls { alpn http/1.1 }` CANNOT be combined with `http://` prefix in the same site block.** Caddy will error: `"server listening on [:80] is HTTP, but attempts to configure TLS connection policies"`. Fix: split into two separate blocks — one for HTTP (no tls), one for HTTPS (with tls ALPN narrowing):
  
  ```caddy
  http://example.geniok.ru {
      reverse_proxy 127.0.0.1:PORT
  }
  
  https://example.geniok.ru {
      tls {
          alpn http/1.1
      }
      reverse_proxy 127.0.0.1:PORT
  }
  ```
  
  This also avoids Caddy's auto-HTTPS redirect for the HTTP block, which is desirable when Cloudflare proxy is on with Flexible SSL. The HTTPS block retains auto-HTTPS (via Let's Encrypt) for direct DNS-only access.
- **ERR_CONNECTION_CLOSED for static assets only:** HTML loads, but fonts/JS/CSS fail. Happens in DNS-only mode (proxied: false) when client has poor routing to the server (e.g. Russia to European server). TCP resets on new connections for asset files but the initial HTML request works (cached or keep-alive).
- **Direct IP:PORT works but domain name doesn't:** DNS resolves correctly, server is up, but browser can't load the page through the domain.

**Critical constraint — Russia DPI/blocking:** Cloudflare CDN servers are actively blocked/DDoSed in Russia. Even with proxied: true, Russian users may see a white screen because Cloudflare edge nodes are unreachable. **For any site targeting Russian users, always start with proxied: false (DNS-only mode).** Do not waste time debugging the @http handler or SSL settings — the fix is to bypass Cloudflare entirely. See `references/russia-deployment-checklist.md` for the full diagnostic protocol.

**Solutions:**

1. **DNS-only mode (RECOMMENDED for Russian-audience sites)** -- Set `proxied: false` and let Caddy handle SSL directly via Let's Encrypt. Caddy auto-obtains certificates via http-01 challenge on port 80/443 with no extra config. The Caddyfile block should be a simple reverse_proxy with NO @http handler:
   ```caddy
   example.geniok.ru {
       reverse_proxy 127.0.0.1:PORT {
           transport http {
               read_timeout 120s
               write_timeout 120s
               dial_timeout 30s
           }
       }
   }
   ```
   After switching from proxied to unproxied, remove the @http handler from Caddyfile and reload. Verify with `curl -sI https://example.geniok.ru/`.

2. **Cloudflare Full (Strict) SSL** -- Change Cloudflare SSL/TLS mode to "Full (strict)" (requires access to Cloudflare dashboard, API token needs Zone.Settings edit permission) so traffic from Cloudflare to origin is also HTTPS. This requires a valid cert on the origin server (Caddy auto-provisioned Let's Encrypt qualifies). Then Cloudflare proxy works without loops. NOT suitable for Russia-audience sites — Cloudflare itself is blocked.

3. **Keep proxied: true + configure Caddy to handle HTTP directly** -- When Cloudflare SSL mode is Flexible (or unknown), Caddy needs explicit HTTP handling to bypass its auto-HTTPS redirect. Two approaches:

   **Option A: @http named matcher (works with any Cloudflare SSL mode):**

   ```caddy
   example.geniok.ru {
       @http {
           protocol http
       }
       handle @http {
           reverse_proxy 127.0.0.1:PORT
       }
       handle {
           reverse_proxy 127.0.0.1:PORT
       }
   }
   ```

   The `@http` matcher catches HTTP connections from Cloudflare (Flexible mode) and serves the proxy directly. The second `handle` block catches HTTPS connections (direct access or Full SSL mode). This works with both Cloudflare SSL modes simultaneously, so no dashboard changes are needed.

   **Option B: Explicit protocol blocks (simpler, recommended when Cloudflare SSL mode is Full/Strict):**

   ```caddy
   http://example.geniok.ru {
       reverse_proxy 127.0.0.1:PORT
   }
   https://example.geniok.ru {
       reverse_proxy 127.0.0.1:PORT
   }
   ```

   Using `http://` and `https://` prefixes on the domain bypasses Caddy's automatic HTTP→HTTPS redirect entirely. Each protocol block is handled independently. This is simpler than the `@http` matcher pattern when you know the Cloudflare SSL mode.

4. **Cloudflare proxy + Full (strict) SSL** -- Re-enable proxied: true and set Cloudflare SSL to Full (strict). Gives fast edge routing + full TLS + no Caddy redirect issues.

**When to use which approach:**

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Russian users, European server | **DNS-only (option 1)** | Cloudflare CDN is actively blocked/DDoSed in Russia. proxied: true fails for Russian users regardless of SSL mode. Always go DNS-only. |
| Local/RU users, RU server | DNS-only (option 1) | Direct connection is fast enough; simpler |
| API backend, global users | Cloudflare proxy + Full SSL (option 2 or 4) | Full TLS edge-to-origin; stable connections |
| Static landing page | Either mode works | Caddy file_server handles both without issues |

### Root domain SSL timing

When adding a root domain (`geniok.ru`) with `proxied: true`, Caddy on the origin server will attempt to obtain a Let's Encrypt certificate via http-01 challenge. If the DNS record was just created and Cloudflare is still provisioning, Let's Encrypt can't find the A record and the challenge fails. Caddy retries automatically, but the first attempt may fail with:

```
"challenge failed" ... "no valid A records found for geniok.ru"
```

Caddy will retry after ~60 seconds and succeed once DNS/Cloudflare propagation completes. The site will be unavailable for the first 1-2 minutes after initial setup. No action needed -- wait for the retry.

## Pitfalls

- **Check ALL existing subdomains on the zone before creating a new one** — Don't assume proxied=True. On geniok.ru (server 2.26.98.104), ALL subdomains including aiphoto, clawhost, rkdash use proxied=False (DNS-only) because Cloudflare is blocked in Russia. Your new subdomain MUST match the existing pattern. Run the pre-flight check first.
- **Copy the config from a working subdomain — don't invent a new one** — When adding a new site to the Caddyfile, look at what a working subdomain (like aiphoto.geniok.ru) uses and copy it verbatim. If aiphoto uses a bare `reverse_proxy 127.0.0.1:PORT` without @http handlers, tls blocks, or transport timeouts, so should your new one. Overcomplicating the Caddy config is the #1 cause of white-screen bugs on this server.
- **After switching proxied mode, tell user to hard-refresh (Ctrl+F5)** — The user's browser and Cloudflare's edge cache can both serve stale versions. Even after the DNS change propagates, the user must clear cache. If they report "still white" after the fix, ask if they hard-refreshed.
- The `$(grep ...)` shell substitution with parentheses inside backtick commands can break in complex one-liners. Prefer writing a separate `.sh` script file or using `tail -1` on the env line directly.
- When reading the Cloudflare token from `.env` files, the token may contain special characters that break shell expansion inside `$(...)` and backtick substitution. Workaround: store the token in a temp file first, then read with `cat /tmp/token_file` in scripts.
- Cloudflare `proxied: true` only works for HTTP/HTTPS (ports 80/443). If the app uses a non-standard port, Cloudflare proxy handles 80/443 and Caddy reverse-proxies to the internal port.
- After adding a DNS record via API, Cloudflare usually propagates within seconds, but the initial SSL certificate from Cloudflare may take 1-2 minutes.
- **Caddyfile editing with `sed` breaks on multi-line blocks** -- sed expects each directive on its own line. Using `sed -i '/pattern/a...'` inserts everything on one line, causing Caddy parse errors. **Use heredoc** (`cat >> ... << 'EOF'`) instead, or rewrite the entire file with `cat >` over SSH.
- Caddy automatically proxies ACME (Let's Encrypt) certificate requests on port 80/443 -- no additional config needed. When `proxied: false`, Caddy obtains certificates seamlessly via http-01 challenge (logs show "certificate obtained successfully").
- **Caddy auto-HTTPS redirect + Cloudflare Flexible SSL = redirect loop**: When proxied: true and Cloudflare SSL mode is Flexible (default), Cloudflare sends HTTP to origin. Caddy's built-in HTTP->HTTPS redirect (308) kicks in, Cloudflare receives the redirect as HTTP again, and the browser hangs. Check Caddy logs for "enabling automatic HTTP->HTTPS redirects" to confirm this is active. Fix: either set proxied: false (DNS-only), use the @http handler pattern (option 3), or change Cloudflare SSL mode to Full (strict).
- **PROXY PERFORMANCE IMPACT**: If the server is in Europe and the user is in Russia, Cloudflare proxy (proxied: true) is critical for speed. Without it, every request goes over direct international lines (slow). With proxy, Cloudflare's edge nodes near Russia handle the connection, and the origin link uses Cloudflare's optimized backbone. Disabling proxy caused page load times from Russia to a UK server to become unusable.
- **Caddy context canceled errors**: If Caddy logs show "aborting with incomplete response" with "context canceled" errors, the reverse proxy connection to the backend is timing out. This is often a symptom of slow network (see proxy impact above), not a misconfiguration.
- **ERR_CONNECTION_CLOSED despite HTTP 200**: If the server returns HTTP 200 but the browser shows ERR_CONNECTION_CLOSED for all resources (HTML, CSS, JS, fonts), and direct IP:PORT works, this signals the reverse proxy is closing connections before the full response body is streamed. Fix: add explicit transport timeouts to the reverse proxy block:

  ```caddy
  example.geniok.ru {
      reverse_proxy 127.0.0.1:PORT {
          transport http {
              read_timeout 120s
              write_timeout 120s
              dial_timeout 30s
          }
      }
  }
  ```

  This prevents premature connection drops from the proxy side. Default Caddy timeouts may be too aggressive for Docker containers serving Next.js apps with many concurrent asset requests.
- **Cloudflare cache stale responses**: After changing proxied: true/false on a DNS record, Cloudflare may serve a cached error page even though the origin is working. Purge the cache via API:
  ```bash
  curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache" \
    -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"files":["https://SUBDOMAIN.DOMAIN/","https://SUBDOMAIN.DOMAIN/PATH"]}'
  ```
  Or have the user hard-refresh (Ctrl+F5) to bypass Cloudflare edge cache.
- When writing Python automation scripts for the Cloudflare API (instead of shell), use `subprocess.run()` with a list of args (not shell=True) to avoid token quoting issues. The token can contain special characters that break shell commands.
- **SSH heredoc + single-quoted delimiter rule**: When rewriting Caddyfile over SSH with `cat >`, always use `<< 'CADDYEOF'` with single-quotes around the delimiter to prevent local shell expansion. Without the quotes, if the Caddyfile content contains `$` characters, the local shell will try to expand them.
- **Cloudflare API token purge permission**: The Cloudflare API token used for DNS edits may NOT have Cache Purge (`purge_cache`) permission. DNS PATCH works, but `POST /purge_cache` returns 401. This is normal — just ask the user to purge cache via Cloudflare dashboard if needed, or set TTL low (120s) and wait.\n- **Python f-string + Cloudflare token**: The Cloudflare API token may contain `$` characters. When using Python's `subprocess.run()` or writing code, avoid f-strings that include the token directly -- use string concatenation (auth = "Authorization: Bearer *** + token) instead of f-strings (auth = f"Authorization: Bearer *** The `$` in the token value can corrupt f-string parsing in some Python/tool environments.\n- **Docker compose `version:` obsolete**: Docker Compose v5+ warns that the `version: '3.8'` attribute in docker-compose.yml is obsolete. Remove it — it has no functional effect.
- **Russian white screen diagnosis protocol:** See `references/russia-deployment-checklist.md` for a step-by-step checklist. The golden rule: check what existing subdomains on the zone use (proxied mode, Caddy config shape) before making ANY changes.
- **User says "Skills" → clarify: personal tech stack or agent skills catalog?** When a user asks to add "Skills" to a landing page, they may mean either (a) a "my technology stack" section showing their personal expertise, or (b) a catalog of downloadable skills for AI agents (like neuraldeep.ru/skills). These are completely different in design, content, and complexity. Before building, clarify: "Это твои личные технологии или Skills для AI-агентов, которые можно установить?" Building the wrong one wastes significant effort.

## Full flow: new subdomain + new server

When adding a subdomain for a service on a server that doesn't have Caddy yet:

1. **Check server** — `nc -z -w 3 IP 22` (SSH), `sshpass -p "PASS" ssh -o ConnectTimeout=5 root@IP "hostname"`
2. **List Docker containers** — `docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'` to find the service and its port
3. **Check port conflicts** — `ss -tlnp | grep ':PORT'` before starting a new service. If port is taken (e.g. dashboard on 3000), change the host port in docker-compose.yml (e.g. `"3008:3000"`)
4. **Install Caddy** if missing — `sshpass -p "PASS" ssh root@IP "apt-get update && apt-get install -y caddy"`
5. **Write Caddyfile** — SSH with heredoc:
   ```bash
   sshpass -p "PASS" ssh root@IP "cat > /etc/caddy/Caddyfile << 'EOF'
   subdomain.geniok.ru {
       reverse_proxy localhost:PORT
   }
   EOF
   caddy reload --config /etc/caddy/Caddyfile"
   ```
6. **Add Cloudflare DNS record** — Default to `proxied: false` if site is for Russian audience (Cloudflare blocked in Russia). Use `proxied: true` only for non-Russian audiences where Cloudflare proxy actually works.
7. **Verify** — `curl -sI https://subdomain.geniok.ru/ | head -5`

Port mapping: Cloudflare proxy only works on 80/443. Caddy listens on both by default. Internal Docker container on any port — Caddy reverse_proxy handles mapping.

**Docker port binding:** Always bind the container port to `127.0.0.1` only — this blocks direct external access to `http://IP:PORT` (which bypasses Caddy's SSL/ALPN config and breaks the app for end users):

```yaml
# GOOD — only accessible from localhost
ports:
  - "127.0.0.1:3008:3000"

# BAD — publicly accessible on port 3008
ports:
  - "3008:3000"
```

After changing the binding: `docker compose down && docker compose up -d`. Verify with `docker ps --format "{{.Names}} {{.Ports}}"` — should show `127.0.0.1:PORT->CONTAINER_PORT/tcp`.

Also remove the `version: '3.8'` line from docker-compose.yml if present — Docker Compose v5+ warns it's obsolete and ignores it.

### Switching from proxied → unproxied mid-flight

If the user reports a white screen and is in Russia:

1. PATCH the DNS record to set `proxied: false`
2. Simplify Caddyfile: remove the @http handler block, use a plain reverse_proxy block
3. Reload Caddy: `caddy reload --config /etc/caddy/Caddyfile`
4. Tell the user to hard-refresh (Ctrl+F5) — browser caches old Cloudflare routing

## Sub-pages in file_server

When a Caddy `file_server` serves a root directory (e.g. `/var/www/geniok`), subdirectories become sub-pages automatically:

```
/var/www/geniok/
├── index.html        → geniok.ru/
└── skills/
    └── index.html    → geniok.ru/skills/
```

Caddy resolves `/skills/` → `/var/www/geniok/skills/index.html` with zero config. No need to add extra Caddyfile blocks for sub-pages.

## GitHub backup for static sites

See reference file: `references/static-site-backup.md`

The workflow: after editing static files served by Caddy, create a private GitHub repo and push files via the GitHub API (blob → tree → commit → ref update). This avoids needing git CLI on the server. Supports multi-file commits in one tree for atomic updates.

## Reference

- Cloudflare API docs: https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-create-dns-record
- Caddyfile docs: https://caddyserver.com/docs/caddyfile
