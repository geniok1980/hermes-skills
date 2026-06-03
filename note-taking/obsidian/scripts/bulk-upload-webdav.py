#!/usr/bin/env python3
"""Bulk upload .md files to Yandex Disk WebDAV with parallel batches.

Usage:
    python3 bulk-upload-webdav.py <source_dir> <webdav_url> <auth> [batch_size]

Example:
    python3 bulk-upload-webdav.py \
        /root/rkeeper-full-docs/docs \
        "https://webdav.yandex.ru/Obsidian%20Vault/rkeeper-docs/full" \
        "login:pass" \
        10
"""

import asyncio, os, sys

BATCH_SIZE = int(sys.argv[4]) if len(sys.argv) > 4 else 10


async def ensure_dir(base_url: str, path: str, auth: str) -> bool:
    """Create directory on WebDAV."""
    proc = await asyncio.create_subprocess_exec(
        "curl", "-s", "-u", auth, "-X", "MKCOL", f"{base_url}/{path}",
        "-w", "%{http_code}", "-o", "/dev/null",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
    out, _ = await proc.communicate()
    return out.decode().strip() in ('201', '200', '204')


async def upload_one(local: str, remote: str, base_url: str, auth: str) -> bool:
    proc = await asyncio.create_subprocess_exec(
        "curl", "-s", "-u", auth, "-T", local,
        f"{base_url}/{remote}",
        "-w", "%{http_code}",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
    out, _ = await proc.communicate()
    return out.decode().strip() in ('201', '204', '200')


async def main():
    source_dir = sys.argv[1]
    webdav_base = sys.argv[2].rstrip('/')
    auth = sys.argv[3]

    # 1. Collect all .md files with relative paths
    files: list[tuple[str, str]] = []
    dirs: set[str] = set()
    for root, _, fnames in os.walk(source_dir):
        for fname in fnames:
            if not fname.endswith('.md'):
                continue
            local_path = os.path.join(root, fname)
            rel_dir = os.path.relpath(root, source_dir)
            if rel_dir == '.':
                remote_path = fname
            else:
                remote_path = f"{rel_dir}/{fname}"
                dirs.add(rel_dir)
            files.append((local_path, remote_path))

    if not files:
        print("No .md files found.")
        return

    # 2. Create required directories
    print(f"Creating {len(dirs)} directories...")
    # First ensure base path itself exists (create parent chain if needed)
    base_parts = [p for p in webdav_base.replace('https://webdav.yandex.ru/', '').split('/') if p]
    for i in range(len(base_parts)):
        parent = '/'.join(base_parts[:i+1])
        await ensure_dir('https://webdav.yandex.ru', parent, auth)
    # Then create subdirectories
    for d in sorted(dirs):
        await ensure_dir(webdav_base, d, auth)

    # 3. Upload in parallel batches
    total = len(files)
    print(f"Uploading {total} files in batches of {BATCH_SIZE}...")
    uploaded = 0
    for i in range(0, total, BATCH_SIZE):
        batch = files[i:i+BATCH_SIZE]
        tasks = [upload_one(local, remote, webdav_base, auth) for local, remote in batch]
        results = await asyncio.gather(*tasks)
        uploaded += sum(1 for r in results if r)
        processed = min(i + BATCH_SIZE, total)
        if processed % 100 == 0 or processed >= total:
            print(f"  [{uploaded}/{total}] uploaded ({processed}/{total} processed)")

    print(f"\nDone! Uploaded {uploaded}/{total} files")
    sys.exit(0 if uploaded == total else 1)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    asyncio.run(main())
