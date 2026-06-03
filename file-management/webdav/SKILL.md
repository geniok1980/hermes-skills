---
name: webdav
description: "WebDAV operations — Yandex Disk, uploads, directory creation, parallel batch sync"
author: Hermes Agent
created_by: agent
---

# WebDAV

WebDAV operations for cloud storage (primarily Yandex Disk). Upload, delete, list, create directories.

## Yandex Disk WebDAV

**Base URL:** `https://webdav.yandex.ru/Obsidian%20Vault/`
**Auth:** Basic Auth (login:password)
**Format:** XML responses (PROPFIND, MKCOL, etc.)

### Commands

```bash
# List directory contents
curl -s -u "login:pass" -X PROPFIND -H "Depth: 1" "https://webdav.yandex.ru/path/"

# Create directory
curl -s -u "login:pass" -X MKCOL "https://webdav.yandex.ru/path/newdir/"

# Upload file (PUT)
curl -s -u "login:pass" -T localfile.md "https://webdav.yandex.ru/path/localfile.md"

# Delete
curl -s -u "login:pass" -X DELETE "https://webdav.yandex.ru/path/target/"
```

## CRITICAL PITFALL: MKCOL before PUT

Yandex WebDAV does NOT auto-create parent directories. If `path/to/file.md` is the target but `path/` and `path/to/` don't exist, the upload (PUT) fails silently or creates a directory instead of a file.

**Always create parent directories first:**
```bash
curl -s -u "login:pass" -X MKCOL "https://webdav.yandex.ru/path/"
curl -s -u "login:pass" -X MKCOL "https://webdav.yandex.ru/path/to/"
curl -s -u "login:pass" -T file.md "https://webdav.yandex.ru/path/to/file.md"
```

## Parallel Batch Upload Pattern

For large numbers of files (thousands), use Python asyncio + curl subprocess in parallel batches:

```python
async def upload_one(local_path, remote_url):
    proc = await asyncio.create_subprocess_exec(
        "curl", "-s", "-u", auth, "-T", local_path, remote_url,
        "-w", "%{http_code}", stdout=asyncio.subprocess.PIPE)
    out, _ = await proc.communicate()
    return out.decode().strip() in ('201', '204', '200')

# Batch of N parallel uploads
results = await asyncio.gather(*tasks)
```

See `references/yandex-disk-quirks.md` for detailed failure modes and recovery.

## Verification

After upload, verify by:
1. PROPFIND the target directory and count entries
2. GET a specific file and check HTTP 200 + content length
3. Check that `<d:resourcetype/>` (empty) = file, `<d:collection/>` = directory
