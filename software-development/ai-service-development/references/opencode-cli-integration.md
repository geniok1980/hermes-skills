# OpenCode CLI as AI Text Generation Backend

## Overview

OpenCode CLI (`opencode`) provides free AI models without API keys. Two approaches to integrate it:

**APPROACH A (PREFERRED — SQLite DB reading):** `opencode run --model <model> <prompt>` writes the response to an internal SQLite DB (`~/.local/share/opencode/opencode.db`). The bot reads the last `assistant` `type=text` entry from the DB after the run completes. This is more reliable than NDJSON parsing.

**APPROACH B (DEPRECATED — NDJSON parsing):** `opencode run --format json --thinking --model <model> '<prompt>'` — parsing NDJSON events for `type=text`. Less reliable because `--format json` sometimes skips text events even with `--thinking`.

## Approach A: SQLite DB reading (PREFERRED)

```python
import subprocess, json, sqlite3, asyncio
from pathlib import Path

OPENCODE_DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"

class AIService:
    async def ask(self, prompt: str, model: str = DEFAULT_MODEL) -> str | None:
        return await asyncio.to_thread(self._ask_sync, prompt, model)

    def _last_message_time(self) -> int:
        """Get max message timestamp before running opencode."""
        try:
            conn = sqlite3.connect(str(OPENCODE_DB))
            row = conn.execute(
                "SELECT COALESCE(MAX(time_created), 0) FROM message"
            ).fetchone()
            conn.close()
            return row[0] if row else 0
        except Exception:
            return 0

    def _ask_sync(self, prompt: str, model: str) -> str | None:
        before = self._last_message_time()
        try:
            result = subprocess.run(
                ["opencode", "run", "--model", model, prompt],
                capture_output=True, text=True, timeout=120,
                env={**os.environ, "OPENCODE_NO_TUI": "1"},
            )
        except subprocess.TimeoutExpired:
            return "⏱ Timeout"
        except Exception as e:
            return f"❌ Error: {e}"

        if result.returncode != 0:
            return f"❌ OpenCode error: {result.stderr[:200]}"

        return self._read_response(before)

    def _read_response(self, after_time: int) -> str | None:
        """Read the last assistant text message created after after_time."""
        try:
            conn = sqlite3.connect(str(OPENCODE_DB))
            rows = conn.execute("""
                SELECT p.data
                FROM message m
                JOIN part p ON p.message_id = m.id
                WHERE json_extract(m.data, '$.role') = 'assistant'
                AND json_extract(p.data, '$.type') = 'text'
                AND json_extract(p.data, '$.text') IS NOT NULL
                AND m.time_created > ?
                ORDER BY m.time_created DESC LIMIT 1
            """, (after_time,)).fetchall()
            conn.close()
            if rows:
                part = json.loads(rows[0][0])
                return part.get("text", "").strip()
            return None
        except Exception as e:
            return None
```

## Approach B: NDJSON parsing (DEPRECATED)

Run `opencode run --format json --thinking --model <model> '<prompt>'` and parse the NDJSON events.

**CRITICAL: `--thinking` flag is REQUIRED** for NDJSON mode. Without it, only `step_start` events are produced — no `text` events.

### NDJSON parsing implementation

```python
# See old code in templates/ai-telegram-bot.py
# Do NOT reproduce — use Approach A (SQLite DB) instead
```

### Available Commands

- `opencode run --model <model> '<prompt>'` — single-turn (no JSON, stdout is terminal output but SQLite DB is written)
- `opencode models` — list available free models
- `opencode --version` — check version

### Available models (June 2026)

| Model | Notes |
|-------|-------|
| `opencode/deepseek-v4-flash-free` | Fast, default choice (used in this project) |
| `opencode/big-pickle` | General purpose |
| `opencode/mimo-v2.5-free` | Alternative |
| `opencode/nemotron-3-super-free` | Alternative |

All are free, no credentials needed.

## Docker setup — OpenCode inside the container (RECOMMENDED)

Install OpenCode directly in the Dockerfile:

```dockerfile
RUN curl -fsSL https://opencode.ai/install | bash && \
    ln -sf /root/.opencode/bin/opencode /usr/local/bin/opencode
```

The install script puts the binary at `/root/.opencode/bin/opencode` (not in PATH). The symlink makes it accessible as `opencode`.

Mount the OpenCode DB volume so responses persist and reuse model cache:

```yaml
services:
  bot:
    build: .
    env_file: .env
    volumes:
      - /root/.local/share/opencode:/root/.local/share/opencode
    restart: unless-stopped
```

### Docker setup — volume-mount only (ALTERNATIVE, not preferred)

If you can't install in Dockerfile (e.g. slim image constraints), volume-mount from host:

```yaml
volumes:
  - /root/.opencode/bin/opencode:/usr/local/bin/opencode:ro
  - /root/.local/share/opencode:/root/.local/share/opencode
```

## Cost / Token accounting

OpenCode doesn't expose token counts in SQLite mode easily. In NDJSON mode, the `step_finish` event has token info.

## Pitfalls

### 1. OpenCode install path — NOT in PATH after install.sh
The install script puts the binary at `/root/.opencode/bin/opencode`. In Docker, always create a symlink: `ln -sf /root/.opencode/bin/opencode /usr/local/bin/opencode`. Without this, `"opencode": command not found`.

### 2. `--format json` may not produce text events
Despite `--thinking`, `opencode run --format json` can produce zero `type=text` events even with exit code 0. This is why **Approach A (SQLite DB)** is preferred — the DB always has the full response.

### 3. SQLite DB locking
Multiple concurrent `opencode run` calls can cause `database is locked` errors. The AI service runs synchronously (`asyncio.to_thread`), so this is a non-issue for serial requests.

### 4. NEVER return raw OpenCode output to users
Both stdout and DB approaches produce data meaningless to end users. Always parse and extract the text response.

### 5. First run migration
First `opencode run` may print:
```
Performing one time database migration, may take a few minutes...
```
This is normal. Adds ~30s to the first call. Subsequent calls are fast.

### 6. Blocking subprocess
`opencode run` blocks until generation finishes (up to 120s). Wrap in `asyncio.to_thread()` for async contexts (aiogram).

### 7. Model names can change
Check `opencode models` periodically. If a model returns empty responses, switch to another.
