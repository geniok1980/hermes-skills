# Yandex Disk WebDAV Quirks

## MKCOL Requirement

Yandex WebDAV requires explicit directory creation via MKCOL before uploading files into subpaths. If `rkeeper-docs/full/` doesn't exist and you run `curl -T file.md "https://webdav.yandex.ru/rkeeper-docs/full/file.md"`, the upload **succeeds** (returns 201) but creates a **directory** named `file.md/` (collection) instead of a proper file.

### Symptom
- PROPFIND shows entries with trailing `/` → `<d:resourcetype><d:collection/></d:resourcetype>`
- Files appear as empty directories in Obsidian
- GET returns 415 or unexpected response

### Fix
```bash
# 1. Delete the broken directory
curl -s -u "login:pass" -X DELETE "https://webdav.yandex.ru/rkeeper-docs/"
# 2. Create proper directory structure
curl -s -u "login:pass" -X MKCOL "https://webdav.yandex.ru/rkeeper-docs/"
curl -s -u "login:pass" -X MKCOL "https://webdav.yandex.ru/rkeeper-docs/full/"
# 3. Create all subdirectories
for dir in archive cloud crm delivery elk fordealers gs kds kiosk license ...; do
  curl -s -u "login:pass" -X MKCOL "https://webdav.yandex.ru/rkeeper-docs/full/$dir/"
done
# 4. Upload files
python3 parallel-upload.py
```

## Parallel Upload Script

The `upload-rkeeper-parallel.py` script processes all `.md` files in a directory and uploads to WebDAV in batches of 10 parallel requests. Key parts:

- `asyncio.create_subprocess_exec("curl", "-s", "-u", auth, "-T", local_path, url, ...)` — spawns curl for each file
- `asyncio.gather(*batch_tasks)` — runs batch in parallel
- Success codes: 201 (Created), 204 (No Content), 200 (OK)

## PROPFIND Response Parsing

Yandex Disk returns XML with `<d:resourcetype>` element:
- Empty `<d:resourcetype/>` = regular file
- `<d:resourcetype><d:collection/></d:resourcetype>` = directory

Use Python/script to parse:
```python
import re
entries = re.findall(r'<d:href>([^<]+)</d:href>.*?<d:resourcetype>(.*?)</d:resourcetype>', data, re.DOTALL)
for href, rtype in entries:
    is_dir = '<d:collection/>' in rtype
```

## Depth Limitation

Yandex Disk may truncate `Depth: infinity` PROPFIND responses. Use `Depth: 1` and traverse directories manually for large trees.
