# GitHub Backup for Static Landing Pages

Back up a Caddy-served static site (`/var/www/...`) to a private GitHub repository.

## When to use

After making significant changes to a static landing page (new sections, design overhaul, new sub-pages), push a snapshot to GitHub for versioning and disaster recovery.

## Workflow

### 1. Create the private repo (one-time)

```bash
# Get GitHub token (from git remote URL or .env)
TOKEN=$(python3 -c "
import re
with open('/root/clawhost/.git/config') as f:
    m = re.search(r'https://([^@]+)@github\.com', f.read())
    print(m.group(1))
")

# Create repo via API
curl -s -X POST https://api.github.com/user/repos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "project-landing",
    "description": "Backup of project landing page",
    "private": true,
    "auto_init": true
  }'
```

### 2. Push files via API (no git client needed)

Use Python to create blob → tree → commit → update ref:

```python
import json, urllib.request, base64, re

# Get token
with open('/root/clawhost/.git/config') as f:
    match = re.search(r'https://([^@]+)@github\.com', f.read())
token = match.group(1)

REPO = 'geniok1980/project-landing'
PATH = 'index.html'

# Read file
with open('/var/www/project/index.html') as f:
    content = f.read()

# Get latest commit and base tree
req = urllib.request.Request(f'https://api.github.com/repos/{REPO}/git/refs/heads/main')
req.add_header('Authorization', f'Bearer {token}')
latest = json.loads(urllib.request.urlopen(req).read())['object']['sha']

req = urllib.request.Request(f'https://api.github.com/repos/{REPO}/git/commits/{latest}')
req.add_header('Authorization', f'Bearer {token}')
base_tree = json.loads(urllib.request.urlopen(req).read())['tree']['sha']

# Create blob
req = urllib.request.Request(f'https://api.github.com/repos/{REPO}/git/blobs', method='POST')
req.add_header('Authorization', f'Bearer {token}')
req.add_header('Content-Type', 'application/json')
blob_sha = json.loads(urllib.request.urlopen(
    req, json.dumps({'content': content, 'encoding': 'utf-8'}).encode()
).read())['sha']

# Create tree
req = urllib.request.Request(f'https://api.github.com/repos/{REPO}/git/trees', method='POST')
req.add_header('Authorization', f'Bearer {token}')
req.add_header('Content-Type', 'application/json')
tree_sha = json.loads(urllib.request.urlopen(
    req, json.dumps({
        'base_tree': base_tree,
        'tree': [{'path': PATH, 'mode': '100644', 'type': 'blob', 'sha': blob_sha}]
    }).encode()
).read())['sha']

# Create commit
req = urllib.request.Request(f'https://api.github.com/repos/{REPO}/git/commits', method='POST')
req.add_header('Authorization', f'Bearer {token}')
req.add_header('Content-Type', 'application/json')
commit_sha = json.loads(urllib.request.urlopen(
    req, json.dumps({
        'message': 'Update landing page',
        'tree': tree_sha,
        'parents': [latest]
    }).encode()
).read())['sha']

# Update branch ref
req = urllib.request.Request(f'https://api.github.com/repos/{REPO}/git/refs/heads/main', method='PATCH')
req.add_header('Authorization', f'Bearer {token}')
req.add_header('Content-Type', 'application/json')
urllib.request.urlopen(req, json.dumps({'sha': commit_sha, 'force': True}).encode())

print(f"✅ Pushed to https://github.com/{REPO}")
```

### 3. Push sub-pages (skills/index.html etc.)

For subdirectory pages, use path like `'skills/index.html'` in the tree array. The backup repo mirrors the server directory structure.

## Multi-file update (one commit)

When updating multiple files (e.g. main page + sub-pages), create a tree with multiple entries in one commit:

```python
tree = [
    {'path': 'index.html', 'mode': '100644', 'type': 'blob', 'sha': blob1_sha},
    {'path': 'skills/index.html', 'mode': '100644', 'type': 'blob', 'sha': blob2_sha},
]
```

This creates one commit with both changes for a clean history.
