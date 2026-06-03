# AI PhotoStudio — Real-world Bun Docker Deploy Example

This was a real session deploying the `ai-photostudio` monorepo (Bun + Hono API + React/Vite) in Docker.

## Project structure

```
ai-photostudio/
├── apps/
│   ├── api/          # Hono backend (Bun)
│   │   └── src/index.ts
│   └── web/          # React + Vite frontend
│       └── vite.config.ts  → port 5173
├── packages/
│   └── shared/       # @ai-photostudio/shared workspace package
├── package.json      # Turborepo workspaces
├── bun.lock
├── turbo.json
└── .env
```

## Dockerfile

```dockerfile
FROM oven/bun:1 AS build
WORKDIR /app

COPY package.json bun.lock turbo.json ./
COPY apps/api/package.json apps/api/package.json
COPY apps/web/package.json apps/web/package.json
COPY packages/shared/package.json packages/shared/package.json

RUN bun install --no-progress

COPY apps/api apps/api
COPY apps/web apps/web
COPY packages/shared packages/shared
COPY .env .env

WORKDIR /app/packages/shared
RUN bun run build || true

WORKDIR /app/apps/web
RUN bun run build

FROM oven/bun:1-slim AS runtime
WORKDIR /app

COPY --from=build /app/apps/web/dist /app/apps/web/dist
COPY --from=build /app/apps/api /app/apps/api
COPY --from=build /app/packages/shared /app/packages/shared
COPY --from=build /app/bun.lock /app/
COPY --from=build /app/package.json /app/
COPY --from=build /app/.env /app/.env
COPY --from=build /app/node_modules /app/node_modules
COPY --from=build /app/apps/api/node_modules /app/apps/api/node_modules
COPY --from=build /app/apps/web/node_modules /app/apps/web/node_modules
COPY --from=build /app/packages/shared/node_modules /app/packages/shared/node_modules

RUN mkdir -p /app/apps/api/uploads

EXPOSE 3001

WORKDIR /app/apps/api
CMD ["bun", "run", "src/index.ts"]
```

## docker-compose.yml

```yaml
services:
  photostudio:
    build: .
    container_name: ai-photostudio
    restart: unless-stopped
    ports:
      - "3007:3001"
    environment:
      - PORT=3001
      - CORS_ORIGIN=http://localhost:3007
      - APP_URL=http://localhost:3007
      - JWT_SECRET=ai-photostudio-docker-secret-key
```

## Key API patch

Added to `apps/api/src/index.ts`:

```typescript
import { serveStatic } from '@hono/node-server/serve-static';

// Must be BEFORE API routes
app.use('/*', serveStatic({ root: '../web/dist', index: 'index.html' }));

// SPA fallback — catch client-side routes
app.notFound(async (c) => {
  if (c.req.path.startsWith('/api/')) return c.json({ error: 'Not Found' }, 404);
  const { readFileSync } = await import('fs');
  const html = readFileSync('/app/apps/web/dist/index.html', 'utf-8');
  return c.html(html);
});
```

## Host

- External URL: `http://2.26.98.104:3007`
- API: `/api/locations`, `/api/packages`, `/api/auth`, `/api/generate`, `/api/payments`, `/api/admin`
- Database: SQLite (ephemeral inside container)
