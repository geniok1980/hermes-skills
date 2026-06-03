# SQLite + Docker: Avoiding Database Baking

When a Bun/Hono project uses SQLite via `bun:sqlite`, the database file (e.g. `photostudio.db`) can get **baked into the Docker image** if it exists on disk during `docker build`. This causes:

- **Stale data** in every container instance
- **Duplicate rows** on re-seed (old rows + new rows)
- **"Admin already exists"** on first run of a fresh container

## The Problem

```dockerfile
COPY apps/api apps/api  # ← copies photostudio.db if present on host!
```

The `COPY` instruction copies **everything** from the source directory, including any SQLite database files that were created during local development or testing.

## The Fix

### 1. Add database files to `.gitignore`

```gitignore
*.db
*.db-wal
*.db-shm
```

This prevents the files from being tracked by git AND from being baked into the Docker image (since `.dockerignore` respects `.gitignore` patterns by default).

### 2. Verify the image is clean

```bash
# Check if a database was baked into the image
docker run --rm my-image sh -c "ls -la /app/apps/api/photostudio.db 2>&1"
# If it exists, rebuild the image after adding .gitignore
```

### 3. Seed the database at runtime

After the container starts, run the seed script:

```bash
docker exec <container-name> sh -c "cd /app/apps/api && bun run src/db/seed.ts"
```

### 4. Option: Start script that auto-seeds

For production, add a startup script that seeds the database on first run:

```dockerfile
# entrypoint.sh
#!/bin/sh
cd /app/apps/api
bun run src/db/seed.ts 2>&1 || echo "Seed skipped (already seeded or error)"
exec bun run src/index.ts
```

```dockerfile
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
CMD ["/app/entrypoint.sh"]
```

## Verification

```bash
# Check API returns correct data (no duplicates)
curl -s http://localhost:3007/api/modes | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f'Count: {len(d[\"modes\"])}')
# Should be 2, not 4
"

# Check no duplicate packages
curl -s http://localhost:3007/api/sparks/prices | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f'Count: {len(d[\"packages\"])}')
# Should be 4, not 8
"
```

## Root Cause Diagram

```
Host filesystem (has photostudio.db)
    ↓ docker build
Build stage copies photostudio.db
    ↓
Runtime image has photostudio.db baked in
    ↓
Container starts → initDb() opens existing DB → old data persists
    ↓
docker exec seed.ts → INSERT OR IGNORE → new UUIDs → DUPLICATE rows!
```

## Seed Idempotency

`INSERT OR IGNORE` with UUID primary keys does **not** prevent duplicates across seed runs because UUIDs are generated fresh each time. To make seed scripts safe to re-run:

### Option 1: UNIQUE constraints

Add `UNIQUE` to logical key columns:
```sql
name TEXT NOT NULL UNIQUE,
```

Then `INSERT OR IGNORE` skips existing rows by name:
```typescript
insertMode.run({ $name: 'portrait', ... }); // safe to re-run
```

### Option 2: Wipe before seed

Clear tables before inserting:
```typescript
db.exec('DELETE FROM generation_modes');
db.exec('DELETE FROM concepts');
// then insert...
```

### Detection check

```bash
curl -s http://localhost:3007/api/modes | python3 -c "
import sys,json; d=json.load(sys.stdin)
dupes = len(d['modes']) - len(set(m['name'] for m in d['modes']))
print(f'Duplicate rows: {dupes}')
"
```
