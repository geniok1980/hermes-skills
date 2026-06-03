#!/usr/bin/env python3
"""
Batch-fetch GitHub repository metadata for a list of repos.

Usage:
    python3 scripts/batch_fetch_repos.py owner/repo1 owner/repo2 owner/repo3

Output: TSV with fields: full_name | stars | forks | language | license | topics | description | pushed_at

Requires: urllib (stdlib), json (stdlib)
Rate limit: 60 req/hr unauthenticated, 5000 req/hr with GITHUB_TOKEN env var.
"""
import json, os, sys, urllib.request, urllib.error

TOKEN = os.environ.get("GITHUB_TOKEN", "")

repos = sys.argv[1:]
if not repos:
    print("Usage: batch_fetch_repos.py owner/repo [...]", file=sys.stderr)
    sys.exit(1)

headers = {"Accept": "application/json", "User-Agent": "Hermes-GitHub-Research/1.0"}
if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"

for full_name in repos:
    url = f"https://api.github.com/repos/{full_name}"
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        d = json.loads(resp.read())
        topics = ",".join(d.get("topics", []) or [])
        desc = (d.get("description") or "")[:200]
        license_spdx = d.get("license") and d["license"].get("spdx_id") or "NONE"
        print(f"{d['full_name']} | ★{d['stargazers_count']} | ⑂{d['forks_count']} | "
              f"{d.get('language') or '?'} | {license_spdx} | [{topics}] | {desc}")
    except urllib.error.HTTPError as e:
        print(f"{full_name} | HTTP {e.code}", file=sys.stderr)
    except Exception as e:
        print(f"{full_name} | ERROR: {e}", file=sys.stderr)
