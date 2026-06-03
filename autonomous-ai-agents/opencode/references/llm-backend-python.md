# OpenCode as LLM Backend — Production Python Wrapper

Reliable async wrapper for using OpenCode as a text-generation backend.
Based on the DB-reading approach (the only 100% reliable method).

```python
"""AI Service — OpenCode CLI LLM backend."""
import asyncio
import json
import logging
import sqlite3
import subprocess
from pathlib import Path

OPENCODE_BIN = "opencode"  # or /root/.opencode/bin/opencode outside Docker
OPENCODE_DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
DEFAULT_MODEL = "opencode/deepseek-v4-flash-free"
REQUEST_TIMEOUT = 120  # seconds

logger = logging.getLogger(__name__)


class AIService:
    async def ask(self, prompt: str, model: str = DEFAULT_MODEL) -> str | None:
        return await asyncio.to_thread(self._ask_sync, prompt, model)

    def _ask_sync(self, prompt: str, model: str) -> str | None:
        # Record latest message ID before launching
        before = self._last_message_time()

        try:
            result = subprocess.run(
                [OPENCODE_BIN, "run", "--model", model, prompt],
                capture_output=True, text=True, timeout=REQUEST_TIMEOUT,
                env={**__import__("os").environ, "OPENCODE_NO_TUI": "1"},
            )
        except subprocess.TimeoutExpired:
            logger.error("OpenCode timeout (%ss)", REQUEST_TIMEOUT)
            return None
        except Exception as e:
            logger.error("OpenCode error: %s", e)
            return None

        if result.returncode != 0:
            logger.error("OpenCode exit %s: %s", result.returncode, result.stderr[:200])
            return None

        return self._read_response(before)

    def _last_message_time(self) -> int:
        try:
            conn = sqlite3.connect(str(OPENCODE_DB))
            row = conn.execute(
                "SELECT COALESCE(MAX(time_created), 0) FROM message"
            ).fetchone()
            conn.close()
            return row[0] if row else 0
        except Exception:
            return 0

    def _read_response(self, after_time: int) -> str | None:
        if not OPENCODE_DB.exists():
            logger.warning("OpenCode DB not found: %s", OPENCODE_DB)
            return None

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
                ORDER BY m.time_created DESC
                LIMIT 1
            """, (after_time,)).fetchall()
            conn.close()
            if rows:
                return json.loads(rows[0][0]).get("text", "").strip()
            return None
        except Exception as e:
            logger.error("DB read error: %s", e)
            return None
```

## Docker Compose Integration

```yaml
services:
  bot:
    build: .
    env_file: .env
    volumes:
      - /root/.opencode/bin/opencode:/usr/local/bin/opencode:ro
      - /root/.local/share/opencode:/root/.local/share/opencode
```

## SQLite DB Schema (for reference)

Table `message`:
- `id TEXT PK` — message ID (e.g. `msg_e8bdc0aab00...`)
- `session_id TEXT` — session ID
- `time_created INTEGER` — unix ms timestamp
- `time_updated INTEGER` — unix ms timestamp
- `data TEXT` — JSON: `{"role":"user"|"assistant", "mode":"build"|"plan", ...}`

Table `part`:
- `id TEXT PK` — part ID
- `message_id TEXT FK` — references message
- `session_id TEXT`
- `time_created INTEGER`
- `time_updated INTEGER`
- `data TEXT` — JSON: `{"type":"text"|"reasoning"|"step-start"|"step-finish", "text":"...", ...}`
