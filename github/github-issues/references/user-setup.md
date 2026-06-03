# User's Repositories

| Repo | URL | Primary Focus |
|------|-----|---------------|
| clawhost-private | github.com/geniok1980/clawhost-private | Main dev project (Hono.js + React monorepo) |

## Active Development Projects

### clawhost-private
- **Stack**: Hono.js backend, React + Vite frontend, Neon PostgreSQL, Bun runtime
- **Conventions**: See `CLAUDE.md` in repo root
- **Key conventions**:
  - Use `@/` path aliases (never `../`)
  - Phosphor icons with `Icon` suffix (e.g., `CheckIcon`, not `Check`)
  - One export per file, types in `@/ts/Interfaces.ts`
  - shadcn/ui + Tailwind CSS
- **Dev workflow**: Multi-agent with Gemini CLI and Trae

## Development Agents

| Agent | Tool | Best For |
|-------|------|----------|
| **Gemini CLI** | `gemini` CLI | Frontend, UI, React components |
| **Trae** | `trae` CLI | Backend, API, database work |

## Multi-Agent Issue Flow

1. User creates raw Issue on GitHub
2. User sends me the link (via Telegram)
3. I format the Issue with proper labels, structure, and instructions
4. Agent picks up the formatted Issue and self-assigns
5. Agent creates PR with `Closes #N`
6. PR merge → Issue auto-closes

## Labels Used

- `agent-ready` — waiting for agent
- `in-progress` — agent working
- `gemini` — for Gemini CLI agent
- `trae` — for Trae agent
- `bug`, `enhancement`, `task` — issue type
- `priority:low`, `priority:medium`, `priority:high`, `priority:critical` — priority