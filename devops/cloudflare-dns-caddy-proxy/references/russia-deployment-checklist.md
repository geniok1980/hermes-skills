# Russia Deployment Checklist — White Screen / Blocked CDN

## First symptom: user in Russia reports white screen

**Do NOT** start debugging Caddy SSL, HTTP/2, @http handlers, or transport timeouts.

### Step 1: Check DNS records on the zone

List all A records and check what proxy mode others use:

```python
import json, urllib.request
with open('/root/clawhost/.env') as f:
    token = [l.split('=',1)[1].strip() for l in f if 'CLOUDFLARE_API_TOKEN' in l][0]
zone_id = 'c53b86d60ef7fa713b5fb535893c8748'
headers = {'Authorization': f'Bearer {token}'}
req = urllib.request.Request(
    f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A',
    headers=headers)
resp = json.loads(urllib.request.urlopen(req).read())
for r in resp['result']:
    if 'geniok.ru' in r['name']:
        print(f"{r['name']:35s} proxied={str(r['proxied']):5s} content={r['content']}")
```

If ALL existing subdomains for this server use `proxied=False`, yours must too.

### Step 2: Inspect Caddyfile

```bash
cat /etc/caddy/Caddyfile
```

Find a working subdomain (e.g. `aiphoto.geniok.ru`) — copy its exact block shape.

### Step 3: Fix DNS — set proxied=False

```python
# Find record ID
req = urllib.request.Request(
    f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A&name=casino.geniok.ru',
    headers=headers)
result = json.loads(urllib.request.urlopen(req).read())
record_id = result['result'][0]['id']

# Update to unproxied
data = json.dumps({
    'type': 'A', 'name': 'casino', 'content': 'SERVER_IP',
    'ttl': 120, 'proxied': False
}).encode()
req2 = urllib.request.Request(
    f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}',
    data=data, headers=headers, method='PATCH')
resp = json.loads(urllib.request.urlopen(req2).read())
print(f"proxied: {resp['result']['proxied']}")
```

### Step 4: Fix Caddyfile — use bare reverse_proxy (no @http, no tls block)

```caddy
casino.geniok.ru {
    reverse_proxy 127.0.0.1:PORT
}
```

Reload:
```bash
caddy validate --config /etc/caddy/Caddyfile && caddy reload --config /etc/caddy/Caddyfile
```

### Step 5: Tell user to hard-refresh (Ctrl+F5)

Browser caches old Cloudflare routing. Hard refresh bypasses it.

### Step 6: Diagnostic — expose Docker port for direct-IP comparison

If hard-refresh didn't help, expose the container port publicly so the user can test direct IP access (bypasses Caddy entirely):

```yaml
# docker-compose.yml — change binding to public
ports:
  - "PORT:PORT"    # NOT 127.0.0.1:PORT:PORT
```

```bash
cd /root/casino && docker compose down && docker compose up -d
```

Then tell user: `http://SERVER_IP:PORT/`

- **If IP works, domain doesn't** → the app is fine. Problem is Caddy config or SSL/HTTP/2. Go to Step 7.
- **If IP ALSO fails** → the app itself is broken. Debug Docker logs, not Caddy.

After diagnosing, restore the `127.0.0.1:` binding:
```yaml
ports:
  - "127.0.0.1:PORT:PORT"
```

### Step 7: If still broken → check browser console for real errors

Don't trust browser extension noise (`contentscript.js`, `bybit:page`, `ObjectMultiplex`). Look past them for:

- `ERR_HTTP2_PING_FAILED` on `.js`/`.css` assets → add `tls { alpn http/1.1 }` to force HTTP/1.1 over HTTPS. **Must use separate `https://` block** — `tls` cannot coexist with `http://` prefix in Caddy:
  ```caddy
  http://example.geniok.ru {
      reverse_proxy 127.0.0.1:PORT
  }
  https://example.geniok.ru {
      tls { alpn http/1.1 }
      reverse_proxy 127.0.0.1:PORT
  }
  ```
- `ERR_CONNECTION_CLOSED` on assets → add transport timeouts to reverse_proxy
- `Failed to load resource` → check file path in HTML

---

## Golden rule

If a Russian user says "white screen":
1. Check DNS → set proxied=False
2. Check Caddy → use simple reverse_proxy
3. Hard refresh
4. Only then debug HTTP/2 or timeouts

Do NOT add @http handlers, tls ALPN settings, or transport timeouts as a first response. Match what existing working subdomains use.
