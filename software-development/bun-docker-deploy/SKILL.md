---
name: bun-docker-deploy
title: Docker Deploy (Bun & Next.js)
description: Deploy web apps in Docker — Bun monorepo (Hono API + React/Vite), Next.js apps, or any Node.js service. Multi-stage builds, Caddy reverse proxy integration, container lifecycle.
tags: [docker, bun, nextjs, node, deploy, monorepo, react, caddy]
---

# Docker Deploy (Bun & Next.js)

Deploy web apps in Docker containers. Covers two common stacks:
- **Bun monorepo** (Turborepo/workspaces) with Hono API + React/Vite frontend
- **Next.js app** with Node.js runtime (standalone output)

Both behind Caddy reverse proxy on the same server.

## When to use

- Deploying a Bun monorepo (workspaces) with a Hono API + React/Vite frontend
- Deploying a Next.js application (pages router or app router) via Docker
- Any Node.js web service that needs multi-stage Docker builds
- Updating a landing page or dashboard and redeploying via docker compose

## Variant A: Next.js with Node.js Dockerfile

For Next.js apps (like rkdash dashboard), the Dockerfile uses `node:22-slim` with npm:

```dockerfile
FROM node:22-slim AS dependencies
WORKDIR /app
RUN npm install -g bun
COPY package.json bun.lock* ./
RUN bun install --no-save --frozen-lockfile

FROM node:22-slim AS builder
WORKDIR /app
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .
ENV NODE_ENV=production
ENV BUILD_STANDALONE=true
RUN npm run build

FROM node:22-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
COPY --from=builder --chown=node:node /app/public ./public
COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static
USER node
EXPOSE 3000
CMD ["node", "server.js"]
```

Key differences from Bun variant:
- Uses `node:22-slim` (not `oven/bun`)
- Uses `npm run build` (not `bun run build`)
- `BUILD_STANDALONE=true` enables Next.js standalone output
- Static assets split: `.next/static` separate from standalone

### Docker compose for Next.js with multiple services

```yaml
services:
  dashboard:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    volumes:
      - ./data:/data:ro
    restart: always
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    restart: unless-stopped
```

### Clerk/auth in Docker build

`NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` is a build-arg. If omitted, Clerk pages won't render, but server-rendered pages (landing page) work fine.

## Variant B: Bun monorepo (Hono API + React/Vite)

The API serves the built frontend as static files and handles SPA client-side routing — single-port deployment.

### 1. Patch the API to serve static frontend

In the API entry file (e.g. `apps/api/src/index.ts`), add static file serving **before** the API routes:

```typescript
import { serveStatic } from '@hono/node-server/serve-static';

// Serve static frontend files — MUST be before API routes
app.use('/*', serveStatic({
  root: '../web/dist',
  index: 'index.html',
}));

// ... API routes ...

// SPA fallback — catch client-side routes (not /api/*)
app.notFound(async (c) => {
  if (c.req.path.startsWith('/api/')) {
    return c.json({ error: 'Not Found' }, 404);
  }
  const { readFileSync } = await import('fs');
  const { join } = await import('path');
  const html = readFileSync(join(import.meta.dir, '../../web/dist/index.html'), 'utf-8');
  return c.html(html);
});
```

⚠️ **Order matters**: `app.use('/*', serveStatic(...))` must go **before** route mounting.

### 2. Multi-stage Dockerfile

```dockerfile
FROM oven/bun:1 AS build
WORKDIR /app

COPY package.json bun.lock turbo.json ./
COPY apps/api/package.json apps/api/package.json
COPY apps/web/package.json apps/web/package.json
COPY packages/*/package.json packages/*/package.json

RUN bun install --no-progress

COPY . .

WORKDIR /app/packages/shared
RUN bun run build || true

WORKDIR /app/apps/web
RUN bun run build

FROM oven/bun:1-slim AS runtime
WORKDIR /app

COPY --from=build /app/apps/web/dist       /app/apps/web/dist
COPY --from=build /app/apps/api            /app/apps/api
COPY --from=build /app/packages/shared     /app/packages/shared
COPY --from=build /app/bun.lock            /app/
COPY --from=build /app/package.json        /app/
COPY --from=build /app/.env                /app/.env
COPY --from=build /app/node_modules        /app/node_modules
COPY --from=build /app/apps/*/node_modules /app/apps/*/node_modules
COPY --from=build /app/packages/*/node_modules /app/packages/*/node_modules

RUN mkdir -p /app/apps/api/uploads

EXPOSE 3001
WORKDIR /app/apps/api
CMD ["bun", "run", "src/index.ts"]
```

### 3. docker-compose.yml

```yaml
services:
  app:
    build: .
    container_name: my-app
    restart: unless-stopped
    ports:
      - "3007:3001"    # host:container
    environment:
      - PORT=3001
      - CORS_ORIGIN=http://localhost:3007
      - APP_URL=http://localhost:3007
```

## Deploy workflow (both variants)

```bash
# 1. Build fresh image (cache-friendly)
docker compose build <service-name>

# 2. Recreate container WITHOUT restarting other services
docker compose up -d --no-deps --force-recreate <service-name>

# 3. Verify
docker ps --filter "name=<service-name>" --format "{{.Names}} {{.Status}}"
```

## Container recreation pitfalls

### `docker compose up -d` without `--force-recreate` silently keeps old container

`docker compose build` creates a fresh image, but `docker compose up -d` MAY silently reuse the existing running container. Verify with:

```bash
docker inspect <container-name> --format '{{.Created}}'
```

If the container timestamp is BEFORE the build timestamp, it was NOT recreated.

**Force recreation (one service only):**
```bash
docker compose up -d --no-deps --force-recreate dashboard
```

The `--no-deps` flag is critical when you only want to restart ONE service in a multi-service compose. Without it, `--force-recreate` recreates ALL services in the dependency chain.

### Container name conflict after force-recreate

If you get:
```
Error: The container name "/service-name-1" is already in use by container "sha256:...".
```

The old container wasn't fully cleaned up. Solution:
```bash
docker compose up -d --no-deps --force-recreate <service-name>
```

If it still fails, manually remove:
```bash
docker rm -f <container-name>
docker compose up -d
```

## Other pitfalls

### Seed scripts with INSERT OR IGNORE + UUIDs create duplicates on re-run

**Problem:** Running `seed.ts` more than once creates duplicate rows because `INSERT OR IGNORE` only ignores PRIMARY KEY conflicts, not logical uniqueness. UUIDs are generated fresh each run.

**Fix — add UNIQUE constraints on logical keys:**
```sql
CREATE TABLE IF NOT EXISTS generation_modes (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  ...
);
```

**Alternative:** Wipe and re-seed:
```typescript
db.exec('DELETE FROM generation_modes');
db.exec('DELETE FROM concepts');
```

### Bun-specific

- `bun.lock` must be present in build context
- `serveStatic` requires `@hono/node-server` >= 1.12.0
- `root` path is relative to runtime WORKDIR, not source file
- CORS config: `CORS_ORIGIN` must be external URL, not localhost:5173
- Remove any `app.get('/', ...)` that conflicts with serveStatic

### Frontend API_BASE must be relative when served from same origin

Set `API_BASE = '/api'` (relative) instead of `http://localhost:3001/api`. Since Hono serves frontend as static files on the same port, relative `/api` works everywhere.

### Docker port mapping

`"3007:3001"` = container listens on 3001, host exposes on 3007. Env vars use external port:
```yaml
environment:
  - CORS_ORIGIN=http://2.26.98.104:3007
  - PORT=3001  # internal
```

### Git branch switching can lose serveStatic

After switching branches, verify:
```bash
grep -q "serveStatic" apps/api/src/index.ts || echo "WARNING: frontend not served"
grep -q "app.notFound" apps/api/src/index.ts || echo "WARNING: SPA routing broken"
```

## References

- `references/sqlite-docker.md` — SQLite database gets baked into Docker image; how to prevent and fix
- `references/ai-photostudio-example.md` — Full example: ai-photostudio Docker setup (multi-stage build, port mapping, seed)

## See Also

- `portfolio-landing-maintenance/references/nextjs-landing-patterns.md` — Next.js + Tailwind v4 landing page patterns (dark theme, pricing cards, AI chat mock)
- `cloudflare-dns-caddy-proxy` — Caddy + Cloudflare DNS for reverse proxy setup

## Verification

```bash
# Check container is running
docker ps --filter name=<service-name>

# Test frontend
curl -s http://localhost:<port>/ | head -5

# Test API
curl -s http://localhost:<port>/api/health
```
